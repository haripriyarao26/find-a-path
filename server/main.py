from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import io
import fitz  # PyMuPDF
from docx import Document
import requests
import os
import re
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Resume Analysis API")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hugging Face API configuration
# Using alternative NER models (dslim/bert-base-NER may be unavailable)
HF_API_URL_NER_OPTIONS = [
    "https://api-inference.huggingface.co/models/dbmdz/bert-large-cased-finetuned-conll03-english",
    "https://api-inference.huggingface.co/models/xlm-roberta-large-finetuned-conll03-english",
    "https://api-inference.huggingface.co/models/dslim/bert-base-NER",  # Fallback
]
HF_API_URL_NER = HF_API_URL_NER_OPTIONS[0]  # Use first working option
HF_API_URL_EMBEDDING = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
HF_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "")

# Log token status (without exposing the actual token)
if HF_API_TOKEN:
    print("✅ Hugging Face API token loaded successfully")
else:
    print("⚠️  No Hugging Face API token found. Using public API (may have rate limits)")

def call_hf_api(url: str, inputs: str, task: str = "ner", retry_urls: List[str] = None):
    """Call Hugging Face Inference API with fallback options"""
    headers = {"Content-Type": "application/json"}
    if HF_API_TOKEN:
        headers["Authorization"] = f"Bearer {HF_API_TOKEN}"
    
    payload = {"inputs": inputs}
    
    # List of URLs to try (for fallback)
    urls_to_try = [url]
    if retry_urls:
        urls_to_try.extend(retry_urls)
    
    last_error = None
    for attempt_url in urls_to_try:
        try:
            response = requests.post(attempt_url, headers=headers, json=payload, timeout=30)
            
            # Handle 410 Gone - try next URL
            if response.status_code == 410:
                print(f"⚠️  Model {attempt_url} returned 410 Gone, trying alternative...")
                continue
            
            # Handle rate limiting and model loading
            if response.status_code == 503:
                error_data = response.json() if response.content else {}
                if "loading" in str(error_data).lower():
                    raise HTTPException(
                        status_code=503, 
                        detail="Model is loading, please try again in a few seconds"
                    )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 410:
                # 410 Gone - try next URL
                last_error = e
                continue
            elif e.response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
            else:
                last_error = e
                # If this is the last URL, raise the error
                if attempt_url == urls_to_try[-1]:
                    raise HTTPException(status_code=e.response.status_code, detail=f"API call failed: {str(e)}")
        except requests.exceptions.RequestException as e:
            last_error = e
            if attempt_url == urls_to_try[-1]:
                raise HTTPException(status_code=500, detail=f"API call failed: {str(e)}")
    
    # If all URLs failed with 410, raise error
    if last_error:
        raise HTTPException(status_code=410, detail="All NER models are unavailable. Please try again later or use an alternative approach.")

def extract_skills_with_api(text: str):
    """Extract skills using Hugging Face NER API with fallback"""
    try:
        # Call Hugging Face NER API with fallback options
        result = call_hf_api(
            HF_API_URL_NER, 
            text, 
            "ner",
            retry_urls=HF_API_URL_NER_OPTIONS[1:]  # Try other models if first fails
        )
        
        # Process results
        entities = []
        if isinstance(result, list):
            entities = result
        elif isinstance(result, dict) and "error" in result:
            # If model is loading, wait and retry
            if "loading" in result["error"].lower():
                raise HTTPException(status_code=503, detail="Model is loading, please try again in a few seconds")
            raise HTTPException(status_code=500, detail=f"API error: {result['error']}")
        
        return entities
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling NER API: {str(e)}")

def get_embeddings_with_api(text: str):
    """Get embeddings using Hugging Face Inference API"""
    try:
        result = call_hf_api(HF_API_URL_EMBEDDING, text, "embedding")
        
        if isinstance(result, dict) and "error" in result:
            if "loading" in result["error"].lower():
                raise HTTPException(status_code=503, detail="Model is loading, please try again in a few seconds")
            raise HTTPException(status_code=500, detail=f"API error: {result['error']}")
        
        # API returns embeddings as a list
        if isinstance(result, list):
            # If it's a list of lists, return the first one
            if len(result) > 0 and isinstance(result[0], list):
                return result[0]
            return result
        
        return result
    except HTTPException as e:
        # If API fails, return None to trigger fallback
        if e.status_code in [410, 503, 500]:
            return None
        raise
    except Exception as e:
        # Return None on any error to trigger fallback
        print(f"⚠️  Embedding API error: {str(e)}, using fallback analysis")
        return None

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_document = fitz.open(stream=file_content, filetype="pdf")
        text = ""
        for page in pdf_document:
            text += page.get_text()
        pdf_document.close()
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        doc = Document(io.BytesIO(file_content))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading DOCX: {str(e)}")

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Extract text from uploaded resume (PDF or DOCX)
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Determine file type and extract text
        if file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(file_content)
        elif file.filename.endswith(('.doc', '.docx')):
            text = extract_text_from_docx(file_content)
        else:
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file type. Please upload PDF or DOCX file."
            )
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text found in the document")
        
        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "text": text,
            "text_length": len(text)
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

def extract_skills_with_regex(text: str):
    """Fallback: Extract skills using regex patterns when API fails"""
    skills = []
    
    # Comprehensive skill patterns
    skill_patterns = [
        # Programming Languages
        r'\b(?:Python|Java|JavaScript|TypeScript|C\+\+|C#|Go|Rust|Swift|Kotlin|Scala|Ruby|PHP|Perl|R|MATLAB)\b',
        # Frontend
        r'\b(?:React|Vue|Angular|Next\.js|Nuxt\.js|Svelte|HTML|CSS|SCSS|SASS|Tailwind|Bootstrap|Material-UI|Redux|MobX)\b',
        # Backend
        r'\b(?:Node\.js|Express|Django|Flask|FastAPI|Spring|Spring Boot|Laravel|ASP\.NET|Rails|GraphQL|REST API)\b',
        # Databases
        r'\b(?:PostgreSQL|MySQL|MongoDB|Redis|Elasticsearch|Cassandra|DynamoDB|SQLite|Oracle|SQL Server|NoSQL|SQL)\b',
        # Cloud & DevOps
        r'\b(?:AWS|Azure|GCP|Google Cloud|Docker|Kubernetes|Terraform|Ansible|Jenkins|CI/CD|Git|GitHub|GitLab)\b',
        # Data Science
        r'\b(?:Machine Learning|ML|Deep Learning|AI|Data Science|NLP|Computer Vision|TensorFlow|PyTorch|Keras|Pandas|NumPy|Scikit-learn)\b',
        # Tools
        r'\b(?:Linux|Unix|Bash|Shell|Agile|Scrum|JIRA|Confluence|Microservices|System Design|API Design)\b',
    ]
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        skills.extend(matches)
    
    return list(set(skills))  # Remove duplicates

@app.post("/extract-skills")
async def extract_skills(data: Dict[str, Any]):
    """
    Extract skills and entities from resume text using Hugging Face NER API
    Falls back to regex extraction if API fails
    """
    try:
        text = data.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Try to extract entities using API
        entities = []
        try:
            entities = extract_skills_with_api(text)
        except HTTPException as e:
            # If API fails (410, etc.), use regex fallback
            if e.status_code in [410, 503, 500]:
                print("⚠️  API unavailable, using regex-based skill extraction")
                skills = extract_skills_with_regex(text)
                return JSONResponse({
                    "success": True,
                    "skills": skills,
                    "organizations": [],
                    "locations": [],
                    "persons": [],
                    "total_entities": len(skills),
                    "note": "Using regex extraction (API unavailable)"
                })
            else:
                raise
        
        # Filter and categorize entities
        skills = []
        organizations = []
        locations = []
        persons = []
        
        # Common skill keywords to filter
        skill_keywords = [
            'python', 'java', 'javascript', 'react', 'node', 'aws', 'docker', 
            'kubernetes', 'sql', 'mongodb', 'postgresql', 'git', 'linux', 
            'agile', 'scrum', 'machine learning', 'ai', 'data science',
            'typescript', 'angular', 'vue', 'django', 'flask', 'fastapi',
            'html', 'css', 'tailwind', 'bootstrap', 'redux', 'graphql',
            'rest api', 'microservices', 'ci/cd', 'jenkins', 'terraform',
            'azure', 'gcp', 'redis', 'elasticsearch', 'kafka', 'spark'
        ]
        
        for entity in entities:
            # Handle different API response formats
            if isinstance(entity, dict):
                entity_text = entity.get('word', entity.get('entity', '')).lower()
                entity_type = entity.get('entity_group', entity.get('label', ''))
                entity_word = entity.get('word', entity.get('entity', ''))
            else:
                continue
            
            # Categorize entities
            if entity_type == 'ORG':
                organizations.append(entity_word)
            elif entity_type == 'LOC':
                locations.append(entity_word)
            elif entity_type == 'PER':
                persons.append(entity_word)
            
            # Check if entity might be a skill
            if any(keyword in entity_text for keyword in skill_keywords):
                if entity_word not in skills:
                    skills.append(entity_word)
        
        # Extract additional skills using regex patterns
        skill_patterns = [
            r'\b(?:Python|Java|JavaScript|TypeScript|React|Node\.js|Angular|Vue|Django|Flask|FastAPI)\b',
            r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Terraform|Jenkins|Git)\b',
            r'\b(?:SQL|MongoDB|PostgreSQL|Redis|Elasticsearch|Kafka)\b',
            r'\b(?:Machine Learning|AI|Data Science|Deep Learning|NLP|Computer Vision)\b',
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match not in skills:
                    skills.append(match)
        
        return JSONResponse({
            "success": True,
            "skills": list(set(skills)),  # Remove duplicates
            "organizations": list(set(organizations)),
            "locations": list(set(locations)),
            "persons": list(set(persons)),
            "total_entities": len(entities)
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting skills: {str(e)}")

def analyze_skills_fallback(skills: List[str], skill_categories: Dict[str, List[str]]):
    """Fallback skill analysis using keyword matching when API fails"""
    category_scores = {}
    recommended_skills = []
    user_skills_lower = [s.lower() for s in skills]
    
    for category, category_skills in skill_categories.items():
        # Count how many skills from this category the user has
        matching_skills = [s for s in category_skills if s.lower() in user_skills_lower]
        match_count = len(matching_skills)
        total_in_category = len(category_skills)
        
        # Calculate score based on percentage of category skills matched
        if total_in_category > 0:
            score = match_count / total_in_category
        else:
            score = 0.0
        
        category_scores[category] = float(score)
        
        # Find missing skills in this category
        missing = [s for s in category_skills if s.lower() not in user_skills_lower]
        
        # Recommend skills if user has less than 50% of category skills
        if missing and score < 0.5:
            recommended_skills.extend(missing[:2])  # Top 2 from each category
    
    return category_scores, recommended_skills

@app.post("/analyze-skills")
async def analyze_skills(data: Dict[str, Any]):
    """
    Analyze skills using Hugging Face embedding API for similarity and recommendations
    Falls back to keyword matching if API is unavailable
    """
    try:
        skills = data.get("skills", [])
        if not skills or len(skills) == 0:
            raise HTTPException(status_code=400, detail="Skills list is required")
        
        # Common skill categories for analysis
        skill_categories = {
            "Programming Languages": ["Python", "Java", "JavaScript", "TypeScript", "C++", "Go", "Rust", "Swift", "Kotlin"],
            "Frontend": ["React", "Vue", "Angular", "HTML", "CSS", "Tailwind CSS", "Next.js", "Redux"],
            "Backend": ["Node.js", "Django", "Flask", "FastAPI", "Spring Boot", "Express.js", "REST API", "GraphQL"],
            "Databases": ["PostgreSQL", "MongoDB", "MySQL", "Redis", "Elasticsearch", "SQL", "NoSQL"],
            "Cloud & DevOps": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "CI/CD", "Jenkins", "Git"],
            "Data Science": ["Machine Learning", "Deep Learning", "Data Science", "AI", "NLP", "TensorFlow", "PyTorch", "Pandas"],
            "Tools & Others": ["Git", "Linux", "Agile", "Scrum", "Microservices", "System Design"]
        }
        
        # Try to get embeddings for user skills using API
        user_skills_text = " ".join(skills)
        user_embedding = get_embeddings_with_api(user_skills_text)
        
        # If API failed, use fallback method
        if user_embedding is None:
            print("⚠️  Embedding API unavailable, using keyword-based analysis")
            category_scores, recommended_skills = analyze_skills_fallback(skills, skill_categories)
        else:
            # Use embedding-based analysis
            # Ensure it's a list
            if not isinstance(user_embedding, list):
                user_embedding = [user_embedding]
            
            # Analyze which categories the user has skills in
            category_scores = {}
            recommended_skills = []
            
            import numpy as np
            
            for category, category_skills in skill_categories.items():
                category_text = " ".join(category_skills)
                category_embedding = get_embeddings_with_api(category_text)
                
                # If category embedding fails, use fallback for this category
                if category_embedding is None:
                    user_skills_lower = [s.lower() for s in skills]
                    matching_skills = [s for s in category_skills if s.lower() in user_skills_lower]
                    score = len(matching_skills) / len(category_skills) if category_skills else 0.0
                    category_scores[category] = float(score)
                    
                    missing = [s for s in category_skills if s.lower() not in user_skills_lower]
                    if missing and score < 0.5:
                        recommended_skills.extend(missing[:2])
                    continue
                
                # Ensure it's a list
                if not isinstance(category_embedding, list):
                    category_embedding = [category_embedding]
                
                # Validate embeddings are not None
                if user_embedding is None or category_embedding is None:
                    # Fallback for this category
                    user_skills_lower = [s.lower() for s in skills]
                    matching_skills = [s for s in category_skills if s.lower() in user_skills_lower]
                    score = len(matching_skills) / len(category_skills) if category_skills else 0.0
                    category_scores[category] = float(score)
                    continue
                
                try:
                    # Calculate cosine similarity
                    user_emb = np.array(user_embedding)
                    cat_emb = np.array(category_embedding)
                    
                    # Validate arrays are not empty
                    if user_emb.size == 0 or cat_emb.size == 0:
                        raise ValueError("Empty embedding array")
                    
                    # Normalize vectors
                    user_norm = np.linalg.norm(user_emb)
                    cat_norm = np.linalg.norm(cat_emb)
                    
                    if user_norm > 0 and cat_norm > 0:
                        similarity = np.dot(user_emb, cat_emb) / (user_norm * cat_norm)
                    else:
                        similarity = 0.0
                    
                    category_scores[category] = float(similarity)
                    
                    # Find missing skills in this category
                    user_skills_lower = [s.lower() for s in skills]
                    missing = [s for s in category_skills if s.lower() not in user_skills_lower]
                    
                    if missing and similarity < 0.7:  # If low similarity, recommend skills
                        recommended_skills.extend(missing[:2])  # Top 2 from each category
                except (ValueError, TypeError) as e:
                    # If numpy operations fail, use keyword matching for this category
                    user_skills_lower = [s.lower() for s in skills]
                    matching_skills = [s for s in category_skills if s.lower() in user_skills_lower]
                    score = len(matching_skills) / len(category_skills) if category_skills else 0.0
                    category_scores[category] = float(score)
                    
                    missing = [s for s in category_skills if s.lower() not in user_skills_lower]
                    if missing and score < 0.5:
                        recommended_skills.extend(missing[:2])
        
        # Get top 3 strongest categories
        top_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Remove duplicates from recommendations
        recommended_skills = list(set(recommended_skills))[:10]
        
        return JSONResponse({
            "success": True,
            "category_analysis": {
                category: {
                    "score": round(score, 3),
                    "strength": "Strong" if score > 0.7 else "Moderate" if score > 0.5 else "Weak"
                }
                for category, score in category_scores.items()
            },
            "top_categories": [{"category": cat, "score": round(score, 3)} for cat, score in top_categories],
            "recommended_skills": recommended_skills,
            "total_skills_analyzed": len(skills)
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing skills: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Resume Analysis API is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

