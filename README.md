# Tespire AI Backend (Prototype)

##  Overview

This project is an AI-powered backend system designed to provide school analytics and insights based on structured data.

It supports queries related to:
- Enrollment
- Attendance
- Payments
- Academic performance

The system processes user questions, determines intent, fetches relevant data from the database, and returns structured, explainable responses.


##  Key Features

-  AI-driven intent detection
-  JWT-based authentication (Supabase)
-  Rate limiting for API protection
-  Caching for performance optimization
-  Guardrails to prevent unsafe queries
-  Report-based data integrity (authoritative data enforcement)
-  Structured responses with metrics and insights
-  Logging for observability


## Architecture

User -> FastAPI -> Intent Router -> Metrics/Reports -> Supabase -> Response Builder -> Response 


## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase JWT
- **AI Model**: HuggingFace Spaces
- **Hosting**: Render
- **Version Control**: GitHub


## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/tespireaidev-source/tespire-ai-prototype.git
cd tespire-ai-prototype
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file based on `.env.example`:


SUPABASE_URL=your_url
SUPABASE_ANON_KEY=your_key
SUPABASE_JWT_SECRET=your_jwt_secret



### 4. Run the server

```bash
uvicorn main:app --reload
```


## Authentication

* Uses **JWT from Supabase**
* Role and school context are derived from token
* Frontend should NOT pass role manually


## API Endpoints

### 1. Ask AI

**POST /ask**

```json
{
  "question": "What is attendance this term?",
  "context": {
    "session_id": "abc123"
  }
}
```

### 2. Monthly Report

**GET /reports/monthly**

Params:

* role
* school_id
* session_id
* term_id

### 3. Academic Report

**GET /reports/term-academic**

### 4. Report History

**GET /reports/history**

### 5. Drilldown

**POST /drilldown**


## Performance Optimizations

* In-memory caching (TTL-based)
* Rate limiting (per user)
* Reduced database calls

## System Components

 Component              Description                

 `main.py`              API entry point            
 `intent_router.py`     Routes user queries        
 `metrics.py`           Data aggregation layer     
 `reports/`             Official report generation 
 `response_builder.py`  Formats AI responses       
 `guardrails`           Safety filters             
 `cache.py`             In-memory caching          
 `rate_limiter.py`      Request throttling         


## Database Tables (Supabase)

* `students`  student records
* `attendances` attendance logs
* `invoices`  payment records
* `student_term_results`  academic results
* `session_terms`  academic periods

## Known Limitations

* In-memory cache resets on server restart
* Memory store is not persistent
* No background job processing
* Rate limiting is instance-based (not distributed)

## Future Improvements

* Add Redis for distributed caching
* Add background jobs for report generation
* Integrate monitoring tools (Sentry)
* Improve scalability for multi-instance deployment


## Deployment (Render)

1. Connect GitHub repo
2. Set environment variables
3. Start command:

```bash
uvicorn main:app --host 0.0.0.0 --port 10000
```

## Handover Note

This system is delivered as a production-grade prototype with security, performance optimization, and data integrity mechanisms in place. 

It is designed for current scale and can be extended for full production deployment.