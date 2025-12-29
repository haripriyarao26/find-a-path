from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import io
import fitz  # PyMuPDF
from docx import Document
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from sentence_transformers import SentenceTransformer
import torch
import re
from typing import List, Dict, Any

app = FastAPI(title="Resume Analysis API")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models (lazy loading)
ner_model = None
ner_tokenizer = None
ner_pipeline = None
sentence_model = None

def load_ner_model():
    """Load NER model for skill extraction"""
    global ner_model, ner_tokenizer, ner_pipeline
    if ner_pipeline is None:
        print("Loading NER model...")
        model_name = "dslim/bert-base-NER"
        ner_pipeline = pipeline(
            "ner",
            model=model_name,
            tokenizer=model_name,
            aggregation_strategy="simple"
        )
        print("NER model loaded!")
    return ner_pipeline

def load_sentence_model():
    """Load sentence transformer model"""
    global sentence_model
    if sentence_model is None:
        print("Loading sentence transformer model...")
        sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Sentence transformer model loaded!")
    return sentence_model

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

@app.post("/extract-skills")
async def extract_skills(data: Dict[str, Any]):
    """
    Extract skills and entities from resume text using NER model
    """
    try:
        text = data.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Load NER model
        ner = load_ner_model()
        
        # Extract entities
        entities = ner(text)
        
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
            entity_text = entity['word'].lower()
            entity_type = entity['entity_group']
            
            # Categorize entities
            if entity_type == 'ORG':
                organizations.append(entity['word'])
            elif entity_type == 'LOC':
                locations.append(entity['word'])
            elif entity_type == 'PER':
                persons.append(entity['word'])
            
            # Check if entity might be a skill
            if any(keyword in entity_text for keyword in skill_keywords):
                if entity['word'] not in skills:
                    skills.append(entity['word'])
        
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

@app.post("/analyze-skills")
async def analyze_skills(data: Dict[str, Any]):
    """
    Analyze skills using sentence transformers for similarity and recommendations
    """
    try:
        skills = data.get("skills", [])
        if not skills or len(skills) == 0:
            raise HTTPException(status_code=400, detail="Skills list is required")
        
        # Load sentence transformer model
        model = load_sentence_model()
        
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
        
        # Create embeddings for user skills
        user_skills_text = " ".join(skills)
        user_embedding = model.encode([user_skills_text])
        
        # Analyze which categories the user has skills in
        category_scores = {}
        recommended_skills = []
        
        for category, category_skills in skill_categories.items():
            category_text = " ".join(category_skills)
            category_embedding = model.encode([category_text])
            
            # Calculate similarity
            from numpy import dot
            from numpy.linalg import norm
            similarity = dot(user_embedding[0], category_embedding[0]) / (norm(user_embedding[0]) * norm(category_embedding[0]))
            
            category_scores[category] = float(similarity)
            
            # Find missing skills in this category
            user_skills_lower = [s.lower() for s in skills]
            missing = [s for s in category_skills if s.lower() not in user_skills_lower]
            
            if missing and similarity < 0.7:  # If low similarity, recommend skills
                recommended_skills.extend(missing[:2])  # Top 2 from each category
        
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

