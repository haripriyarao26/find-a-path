# Find Your Path - AI-Powered Career Roadmap Generator

A full-stack, AI-driven application that analyzes resumes and generates personalized career roadmaps with skill gap analysis and visual mind maps.

---

## 📁 Project Structure

```
find-a-path/
├── client/              # Next.js frontend application
│   ├── app/             # Next.js app directory
│   ├── package.json     # Frontend dependencies
│   └── ...
├── server/              # FastAPI backend application
│   ├── main.py          # FastAPI application
│   ├── requirements.txt # Python dependencies
│   └── ...
└── README.md            # Project documentation
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- pip

### Setup

1. **Client (Frontend) Setup:**
```bash
cd client
npm install
npm run dev
```
Frontend runs on `http://localhost:3000`

2. **Server (Backend) Setup:**
```bash
cd server
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m uvicorn main:app --reload --port 8000
```

Or use the start script:
```bash
cd server
./start.sh
```

Backend runs on `http://localhost:8000`

**Note:** If you get "command not found" errors, make sure:
- Virtual environment is activated (you should see `(venv)` in your prompt)
- Use `python3 -m pip` instead of just `pip`
- Use `python3 -m uvicorn` instead of just `uvicorn`

**Note:** First run will download Hugging Face models (~500MB), which may take a few minutes.

### Usage
1. Start both frontend and backend servers
2. Open `http://localhost:3000` in your browser
3. Upload a PDF or DOCX resume
4. View extracted skills and analysis results

---

## 🎯 Project Overview

This project helps users understand their career trajectory by:
- Uploading their resume (PDF/DOCX)
- Extracting skills, experience, and education using NLP
- Analyzing skill gaps and suggesting learning paths
- Generating visual mind maps of career progression
- Storing data for future reference and tracking

**Why This Project is Strong:**
- **Full-Stack Exposure:** Front-end, back-end, database, and AI integration
- **AI/ML Involvement:** NLP for resume parsing, LLM for analysis and recommendations
- **Recruiter Appeal:** Demonstrates end-to-end engineering and practical AI application
- **Portfolio Value:** Showcases system design, NLP skills, and visual presentation

---

## 🚀 Project Phases

### **Phase 1: Upload & Analysis** ✅ (Current)
**Goal:** Build the foundation with resume upload and basic analysis

**Features:**
- ✅ Resume upload interface (PDF/DOCX support)
- ✅ Resume parsing using NLP (extract skills, roles, technologies, education)
- ✅ **Learning path suggestions** based on current skills
- ✅ **Skill gap analysis** - identify what skills are missing

**Tech Stack:**
- Front-End: React / Next.js / Tailwind CSS
- Back-End: FastAPI / Django REST Framework
- NLP Libraries: `spacy`, `pdfminer`, `PyMuPDF`, `python-docx`
- AI: GPT-3.5/4 or LLaMA 2 for analysis

**Deliverables:**
- Working upload interface
- Resume text extraction
- Skills and experience extraction
- AI-generated learning path recommendations
- Skill gap analysis report

---

### **Phase 2: Visual Mind Map Generation**
**Goal:** Create interactive visualizations of career paths

**Features:**
- Generate visual mind maps from extracted data
- Interactive nodes showing skills, roles, and connections
- Visual representation of learning paths
- Clickable nodes for detailed information

**Tech Stack Options:**
- **Graphviz** - Static graph generation
- **D3.js** - Interactive, customizable visualizations
- **Mermaid.js** - Easy-to-use diagram library

**Deliverables:**
- Mind map visualization component
- Interactive career roadmap display
- Visual skill connections and dependencies

---

### **Phase 3: Role-Based Skill Identification**
**Goal:** Help users identify missing skills for target roles

**Features:**
- User can specify desired roles/positions
- AI compares current skills vs. required skills for target roles
- Detailed breakdown of missing competencies
- Prioritized skill acquisition recommendations
- Role-specific learning paths

**Tech Stack:**
- AI/LLM: GPT-4 or similar for role analysis
- Database: Store role requirements and skill mappings

**Deliverables:**
- Role selection interface
- Skill comparison tool
- Missing skills identification
- Prioritized recommendations

---

### **Phase 4: Database Storage & Future Features**
**Goal:** Persist data and enable advanced features

**Features:**
- Store resumes, extracted tags, and analysis results in database
- User accounts and session management
- Historical tracking of skill progression
- Save and retrieve previous analyses
- Multi-resume analysis and comparison

**Tech Stack:**
- Database: PostgreSQL / MongoDB / SQLite (for MVP)
- Authentication: JWT or OAuth
- File Storage: Local storage or cloud (AWS S3, etc.)

**Deliverables:**
- Database schema design
- User authentication system
- Data persistence layer
- Historical analysis dashboard

---

## 🛠️ Complete Tech Stack

| Layer         | Technology Options                                    |
| ------------- | ----------------------------------------------------- |
| **Front-End** | React / Next.js / Tailwind CSS / D3.js / Mermaid.js  |
| **Back-End**  | FastAPI / Django REST Framework                       |
| **Database**  | PostgreSQL / MongoDB / SQLite (MVP)                   |
| **AI/NLP**    | GPT-3.5/4, LLaMA 2, SpaCy, Hugging Face Transformers |
| **File Handling** | python-docx, pdfminer, PyMuPDF                    |

---

## 📋 Implementation Roadmap

### Phase 1 Implementation Steps:
1. ✅ Set up Next.js frontend with upload interface
2. Build backend API (FastAPI/Django)
3. Implement resume parsing (PDF/DOCX extraction)
4. Integrate NLP for entity extraction (skills, roles, education)
5. Add AI integration for learning path generation
6. Implement skill gap analysis logic
7. Display results on frontend

### Phase 2 Implementation Steps:
1. Choose visualization library (D3.js recommended)
2. Design mind map data structure
3. Create visualization component
4. Integrate with Phase 1 data
5. Add interactivity (hover, click, zoom)

### Phase 3 Implementation Steps:
1. Create role database/API
2. Build role selection interface
3. Implement skill comparison algorithm
4. Generate missing skills report
5. Create prioritized recommendations

### Phase 4 Implementation Steps:
1. Design database schema
2. Set up authentication
3. Implement data persistence
4. Build user dashboard
5. Add historical tracking features

---

## 💡 Key Talking Points for Interviews

- **System Architecture:** How you structured the pipeline: upload → parse → extract → analyze → visualize → store
- **AI Design Decisions:** Why you chose specific models (LLaMA vs GPT), prompt engineering strategies, handling ambiguous data
- **System Design:** File storage approach, database schema, async processing for AI calls, caching strategies
- **Full-Stack Integration:** How front-end, back-end, AI layer, and database communicate
- **Scalability:** How the system handles multiple users, large files, and concurrent AI requests

---

## 🎨 Optional Enhancements (Future)

- **Interactive Mind Map:** Click nodes for resources, tutorials, or projects
- **Recommendation Engine:** Suggest certifications, courses, or articles
- **Multi-Resume Analysis:** Compare multiple resumes to see skill progression
- **Export Features:** Download mind maps as images or PDFs
- **Social Features:** Share career paths with mentors or peers

---

## 📝 Notes

This project demonstrates:
- End-to-end full-stack development
- AI/ML integration in practical applications
- System design and architecture skills
- NLP and data extraction capabilities
- Visual presentation and UX design

Perfect for showcasing to recruiters and demonstrating your ability to build production-ready, AI-powered applications.
