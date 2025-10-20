# FlowShare AI Agents Backend

**Production URLs:**
- **Auditor Agent**: [https://auditor-agent-g5zmzlktoa-ew.a.run.app](https://auditor-agent-g5zmzlktoa-ew.a.run.app)
- **Accountant Agent**: [https://accountant-agent-g5zmzlktoa-ew.a.run.app](https://accountant-agent-g5zmzlktoa-ew.a.run.app)
- **Communicator Agent**: [https://communicator-agent-g5zmzlktoa-ew.a.run.app](https://communicator-agent-g5zmzlktoa-ew.a.run.app)

A production-grade, multi-agent Python backend system for autonomous hydrocarbon allocation, reconciliation, and reporting. Built with FastAPI and deployed on Google Cloud Run.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Agent Services](#agent-services)
- [Shared Infrastructure](#shared-infrastructure)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Monitoring & Logging](#monitoring--logging)
- [Testing](#testing)
- [Contributing](#contributing)

---

## Overview

FlowShare's backend is a sophisticated multi-agent system where specialized AI agents work autonomously to handle complex hydrocarbon reconciliation workflows. Each agent is a microservice deployed independently on Google Cloud Run, communicating through well-defined APIs.

### System Goals

- **Autonomous Operation**: AI agents handle complex tasks without human intervention
- **Scalability**: Independent services scale based on demand
- **Reliability**: Production-grade error handling and monitoring
- **Maintainability**: Clean architecture with shared infrastructure
- **Observability**: Comprehensive logging and health monitoring

### The Three Agents

1. **Auditor Agent**: Validates production data and detects anomalies
2. **Accountant Agent**: Performs complex allocation calculations
3. **Communicator Agent**: Generates reports and sends notifications

---

## Architecture

### System Architecture Diagram

```
                        ┌─────────────────────────────────┐
                        │      FlowShare Frontend         │
                        │      (Next.js Client)           │
                        └─────────────┬───────────────────┘
                                      │
                                      │ HTTPS/REST API
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
        ┌───────────────────────┐         ┌───────────────────────┐
        │   Google Cloud Run    │         │   Firebase Cloud      │
        │   (Container Platform)│         │   ┌─────────────────┐ │
        │                       │         │   │  Authentication │ │
        │  ┌─────────────────┐ │         │   ├─────────────────┤ │
        │  │ Auditor Agent   │ │◄────────┼───┤    Firestore    │ │
        │  │   Port: 8081    │ │         │   │    (Database)   │ │
        │  └────────┬────────┘ │         │   ├─────────────────┤ │
        │           │           │         │   │  Cloud Storage  │ │
        │  ┌────────▼────────┐ │         │   └─────────────────┘ │
        │  │Accountant Agent │ │◄────────┤                       │
        │  │   Port: 8082    │ │         └───────────────────────┘
        │  └────────┬────────┘ │
        │           │           │         ┌───────────────────────┐
        │  ┌────────▼────────┐ │         │  Google Generative AI │
        │  │Communicator     │ │◄────────┤    (Gemini API)       │
        │  │     Agent       │ │         │                       │
        │  │   Port: 8083    │ │         └───────────────────────┘
        │  └─────────────────┘ │
        │                       │
        │  Each agent:          │
        │  • FastAPI service    │
        │  • Independent scaling│
        │  • Shared libraries   │
        │  • Health monitoring  │
        └───────────────────────┘
```

### Multi-Agent Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Reconciliation Workflow                       │
└─────────────────────────────────────────────────────────────────┘

1. Field Operator Inputs Production Data
   │
   ├──► Frontend validates & saves to Firestore
   │
   └──► Firestore trigger invokes Auditor Agent
        │
        ▼
   ┌─────────────────────────────────────────┐
   │      AUDITOR AGENT (Data Validation)     │
   ├─────────────────────────────────────────┤
   │ • Fetch historical data for partner     │
   │ • Analyze with Gemini API              │
   │ • Detect statistical anomalies         │
   │ • Flag suspicious entries              │
   │ • Update Firestore with validation     │
   └──────────────────┬──────────────────────┘
                      │
                      │ Data validated ✓
                      │
2. JV Coordinator Creates Terminal Receipt
   │
   └──► Frontend invokes Accountant Agent
        │
        ▼
   ┌─────────────────────────────────────────┐
   │   ACCOUNTANT AGENT (Reconciliation)     │
   ├─────────────────────────────────────────┤
   │ • Query validated production entries   │
   │ • Calculate net volumes                │
   │ • Compute shrinkage factors            │
   │ • Allocate terminal volume             │
   │ • Generate reconciliation report       │
   │ • Save results to Firestore            │
   └──────────────────┬──────────────────────┘
                      │
                      │ Reconciliation complete ✓
                      │
   ┌──────────────────▼──────────────────────┐
   │  COMMUNICATOR AGENT (Notifications)     │
   ├─────────────────────────────────────────┤
   │ • Fetch reconciliation results         │
   │ • Generate AI summary with Gemini      │
   │ • Create notification documents        │
   │ • Send to stakeholder dashboards       │
   └─────────────────────────────────────────┘
                      │
                      │ Notifications sent ✓
                      │
3. Stakeholders View Results in Frontend Dashboard
```

### Agent Independence & Communication

- **Stateless Services**: Each agent is stateless and scales independently
- **Firestore as Message Bus**: Agents communicate via Firestore documents
- **Event-Driven**: Changes in Firestore trigger agent workflows
- **REST APIs**: Direct HTTP calls for synchronous operations

---

## Features

### Core Capabilities

- **Multi-Agent Architecture**: Specialized microservices for distinct tasks
- **AI-Powered Validation**: Gemini API for intelligent anomaly detection
- **Automated Reconciliation**: Complex industry-standard calculations (API MPMS)
- **Intelligent Reporting**: Natural language report generation
- **Production-Grade Infrastructure**: Middleware, logging, error handling
- **Cloud-Native**: Designed for Google Cloud Run
- **Auto-Scaling**: Each agent scales based on load
- **Health Monitoring**: Comprehensive health check endpoints
- **Security**: CORS protection, rate limiting, timeout management
- **CI/CD**: Automated deployment via GitHub Actions

### Advanced Features

- **Structured Logging**: JSON logs with request tracking
- **Request Tracing**: Unique request IDs across the system
- **Rate Limiting**: Protection against API abuse
- **Timeout Management**: Automatic request timeout handling
- **GZip Compression**: Response compression for performance
- **Security Headers**: HSTS, CSP, and other security headers
- **Graceful Shutdown**: Proper cleanup on container termination

---

## Technology Stack

### Core Framework

- **[FastAPI 0.115.0+](https://fastapi.tiangolo.com/)** - Modern, high-performance web framework
- **[Uvicorn 0.32.0+](https://www.uvicorn.org/)** - Lightning-fast ASGI server
- **[Python 3.12+](https://www.python.org/)** - Programming language

### Google Cloud Services

- **[Google Cloud Firestore 2.19.0+](https://cloud.google.com/firestore)** - NoSQL database
- **[Firebase Admin SDK 6.0.0+](https://firebase.google.com/docs/admin/setup)** - Backend Firebase integration
- **[Google Generative AI 1.0.0+](https://ai.google.dev/)** - Gemini API for AI capabilities
- **[Google Cloud Storage](https://cloud.google.com/storage)** - File storage

### Data & Validation

- **[Pydantic 2.0.0+](https://docs.pydantic.dev/)** - Data validation and settings
- **[Pydantic Settings 2.0.0+](https://docs.pydantic.dev/latest/usage/pydantic_settings/)** - Configuration management

### Development & Deployment

- **[Python-dotenv 1.0.0+](https://github.com/thenceforward/python-dotenv)** - Environment variable management
- **[Docker](https://www.docker.com/)** - Containerization
- **[GitHub Actions](https://github.com/features/actions)** - CI/CD automation
- **[Google Cloud Run](https://cloud.google.com/run)** - Serverless container platform

---

## Prerequisites

### Required Software

- **Python**: 3.12 or later ([Download](https://www.python.org/downloads/))
- **pip**: Package installer (comes with Python)
- **Git**: Version control ([Download](https://git-scm.com/))
- **Docker**: (Optional) For local containerized testing ([Download](https://www.docker.com/))
- **Google Cloud SDK**: For Cloud Run deployment ([Install](https://cloud.google.com/sdk/docs/install))

### Google Cloud Setup

1. **GCP Project**: `<project-id>` (or your project ID)
2. **Service Account**: `<service-account>.iam.gserviceaccount.com`
3. **Region**: `europe-west1`
4. **Enabled APIs**:
   - Cloud Run API
   - Cloud Build API
   - Firestore API
   - Cloud Storage API
   - Identity Platform (Firebase Auth)
   - Generative AI API

### System Requirements

- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 2GB free space
- **OS**: macOS, Linux, or Windows with WSL2

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/todak2000/flowshare-agents-backend.git
cd flowshare-agents-backend
```

### 2. Set Up Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 3. Install Shared Dependencies

```bash
# Install shared dependencies first
pip install -r shared/requirements.txt
```

### 4. Install Agent-Specific Dependencies

```bash
# Install all agents' dependencies
pip install -r accountant-agent/requirements.txt
pip install -r auditor-agent/requirements.txt
pip install -r communicator-agent/requirements.txt
```

### 5. Verify Installation

```bash
python --version
# Expected: Python 3.12.x or later

pip list | grep fastapi
# Expected: fastapi 0.115.0 or later
```

---

## Configuration

### 1. Environment Variables

Create a `.env` file in the root of `flowshare-agents-backend/`:

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=<project-id>
GCP_REGION=europe-west1
ENVIRONMENT=development

# Firebase Configuration
FIREBASE_PROJECT_ID=<project-id>
FIREBASE_CLIENT_EMAIL=<service-account>.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_PRIVATE_KEY_ID=<your_private_key_id>
FIREBASE_CLIENT_ID=<your_client_id>

# Gemini AI Configuration
GEMINI_API_KEY=<your_gemini_api_key>

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# Service Ports (for local development)
AUDITOR_AGENT_PORT=8081
ACCOUNTANT_AGENT_PORT=8082
COMMUNICATOR_AGENT_PORT=8083

# CORS Configuration (comma-separated origins)
ALLOWED_ORIGINS=http://localhost:3000

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Timeout Configuration (seconds)
REQUEST_TIMEOUT=30
```

### 2. Firebase Service Account

Download your Firebase service account JSON and set up the private key:

```bash
# Save your service account JSON file
# Extract the private_key field and set it in .env

# Alternatively, set GOOGLE_APPLICATION_CREDENTIALS
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

### 3. Configure CORS

Update `shared/middleware/__init__.py` if you need to add more allowed origins:

```python
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://your-custom-domain.com"
]
```

---

## Running the Application

### Running Individual Agents Locally

#### Option 1: Using Python Directly

```bash
# Activate virtual environment
source venv/bin/activate

# Run Auditor Agent
cd auditor-agent
python main.py
# Runs on http://localhost:8081

# Run Accountant Agent (in new terminal)
cd accountant-agent
python main.py
# Runs on http://localhost:8082

# Run Communicator Agent (in new terminal)
cd communicator-agent
python main.py
# Runs on http://localhost:8083
```

#### Option 2: Using Uvicorn Directly

```bash
# Run with auto-reload (for development)
cd accountant-agent
uvicorn main:app --host 0.0.0.0 --port 8082 --reload
```

### Running All Agents Concurrently

Create a `run_all.sh` script:

```bash
#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run all agents in background
cd auditor-agent && python main.py &
cd accountant-agent && python main.py &
cd communicator-agent && python main.py &

# Wait for all background processes
wait
```

Make it executable and run:

```bash
chmod +x run_all.sh
./run_all.sh
```

### Running with Docker

#### Build Individual Agent

```bash
# Build Accountant Agent
cd accountant-agent
docker build -t accountant-agent:latest .

# Run the container
docker run -p 8082:8082 --env-file ../.env accountant-agent:latest
```

#### Build All Agents

```bash
# Build all agents
docker build -t auditor-agent:latest -f auditor-agent/Dockerfile .
docker build -t accountant-agent:latest -f accountant-agent/Dockerfile .
docker build -t communicator-agent:latest -f communicator-agent/Dockerfile .
```

### Verify Services are Running

```bash
# Check Auditor Agent
curl http://localhost:8081/health

# Check Accountant Agent
curl http://localhost:8082/health

# Check Communicator Agent
curl http://localhost:8083/health

# Expected response:
# {
#   "status": "healthy",
#   "agent": "Accountant Agent",
#   "version": "1.0.0",
#   "timestamp": "2025-10-20T10:30:00Z"
# }
```

---

## Project Structure

```
flowshare-agents-backend/
│
├── shared/                                # Shared infrastructure & utilities
│   ├── __init__.py
│   ├── config.py                         # Configuration management (Pydantic)
│   ├── logger.py                         # Structured JSON logging
│   ├── models.py                         # Pydantic data models
│   ├── firestore_client.py              # Firestore database wrapper
│   ├── gemini_client.py                 # Gemini AI client wrapper
│   ├── storage_client.py                # Cloud Storage client
│   │
│   ├── middleware/                       # FastAPI middleware
│   │   ├── __init__.py
│   │   ├── security.py                  # Security headers
│   │   ├── tracking.py                  # Request ID tracking
│   │   ├── rate_limit.py                # Rate limiting
│   │   └── timeout.py                   # Timeout management
│   │
│   ├── routes/                           # Shared API routes
│   │   ├── __init__.py
│   │   └── health.py                    # Health check endpoints
│   │
│   ├── utils/                            # Utility functions
│   │   ├── __init__.py
│   │   ├── validation.py                # Data validation
│   │   ├── formatting.py                # Data formatting
│   │   └── crypto.py                    # Cryptographic utilities
│   │
│   └── requirements.txt                  # Shared dependencies
│
├── accountant-agent/                      # Reconciliation calculation agent
│   ├── __init__.py
│   ├── main.py                           # FastAPI application
│   ├── agent.py                          # Core reconciliation logic
│   ├── agents_api.py                     # External agent communication
│   │
│   ├── calculators/                      # Calculation modules
│   │   ├── __init__.py
│   │   ├── net_volume.py                # Net volume calculations
│   │   ├── shrinkage.py                 # Shrinkage calculations
│   │   └── allocation.py                # Allocation algorithms
│   │
│   ├── routes/                           # API endpoints
│   │   ├── __init__.py
│   │   ├── allocation.py                # Allocation endpoints
│   │   └── reconciliation.py            # Reconciliation endpoints
│   │
│   ├── Dockerfile                        # Container definition
│   └── requirements.txt                  # Agent dependencies
│
├── auditor-agent/                         # Data validation agent
│   ├── __init__.py
│   ├── main.py                           # FastAPI application
│   ├── agent.py                          # Core validation logic
│   │
│   ├── validators/                       # Validation modules
│   │   ├── __init__.py
│   │   ├── statistical.py               # Statistical validation
│   │   └── business_rules.py            # Business rule validation
│   │
│   ├── routes/                           # API endpoints
│   │   ├── __init__.py
│   │   └── validation.py                # Validation endpoints
│   │
│   ├── Dockerfile                        # Container definition
│   └── requirements.txt                  # Agent dependencies
│
├── communicator-agent/                    # Notification & reporting agent
│   ├── __init__.py
│   ├── main.py                           # FastAPI application
│   ├── agent.py                          # Core communication logic
│   │
│   ├── generators/                       # Report generators
│   │   ├── __init__.py
│   │   ├── summary.py                   # Summary generation
│   │   └── detailed.py                  # Detailed report generation
│   │
│   ├── routes/                           # API endpoints
│   │   ├── __init__.py
│   │   ├── notifications.py             # Notification endpoints
│   │   └── reports.py                   # Report endpoints
│   │
│   ├── Dockerfile                        # Container definition
│   └── requirements.txt                  # Agent dependencies
│
├── .github/
│   └── workflows/                         # CI/CD pipelines
│       ├── deploy-auditor.yml            # Auditor agent deployment
│       ├── deploy-accountant.yml         # Accountant agent deployment
│       └── deploy-communicator.yml       # Communicator agent deployment
│
├── venv/                                  # Python virtual environment (gitignored)
├── .env                                   # Environment variables (gitignored)
├── .gitignore                             # Git ignore rules
└── README.md                              # This file
```

---

## Agent Services

### 1. Auditor Agent (Port 8081)

**Purpose**: Validate production data and detect anomalies

#### Core Responsibilities

- **Real-time Validation**: Validate production entries as they're created
- **Anomaly Detection**: Use Gemini AI to identify statistical outliers
- **Historical Analysis**: Compare new entries against historical patterns
- **Flagging**: Mark suspicious entries for review
- **Audit Logging**: Track all validation activities

#### Key Functions

```python
class AuditorAgent:
    async def validate_production_entry(self, entry_id: str) -> ValidationResult:
        """
        Validate a production entry

        Steps:
        1. Fetch entry from Firestore
        2. Fetch historical data for partner
        3. Analyze with Gemini API
        4. Detect anomalies
        5. Update Firestore with results
        """
        pass

    async def analyze_anomaly(self, entry: ProductionEntry, historical: List[ProductionEntry]) -> AnomalyReport:
        """Use Gemini to analyze for anomalies"""
        pass
```

#### API Endpoints

```
GET  /health                           # Health check
GET  /status                           # Detailed status
POST /api/validate                     # Validate production entry
GET  /api/validation-history/{entry_id} # Get validation history
```

#### Example Usage

```bash
curl -X POST http://localhost:8081/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "entry_id": "prod_entry_12345",
    "partner_id": "partner_001",
    "volume": 1500.5,
    "timestamp": "2025-10-20T10:30:00Z"
  }'
```

---

### 2. Accountant Agent (Port 8082)

**Purpose**: Perform complex allocation calculations and reconciliation

#### Core Responsibilities

- **Net Volume Calculation**: Apply industry-standard corrections (API MPMS)
- **Shrinkage Computation**: Calculate field-to-terminal shrinkage
- **Volume Allocation**: Proportionally allocate terminal volumes to partners
- **Report Generation**: Create detailed reconciliation reports
- **Data Integrity**: Generate cryptographic hashes for verification

#### Key Functions

```python
class AccountantAgent:
    async def run_reconciliation(self, terminal_receipt_id: str) -> ReconciliationResult:
        """
        Execute reconciliation workflow

        Steps:
        1. Query validated production entries
        2. Calculate net volumes
        3. Compute shrinkage
        4. Allocate terminal volume
        5. Generate report
        6. Save to Firestore
        """
        pass

    def calculate_net_volume(self, gross: float, bsw: float, temp: float, api: float) -> float:
        """Calculate net volume with corrections"""
        pass

    def allocate_volume(self, partners: List[Partner], total: float) -> Dict[str, Allocation]:
        """Allocate volume proportionally"""
        pass
```

#### Calculation Modules

**Net Volume Calculator** (`calculators/net_volume.py`):
- BS&W (Basic Sediment & Water) correction
- Temperature correction (API MPMS Table 6A)
- API gravity adjustment

**Shrinkage Calculator** (`calculators/shrinkage.py`):
- Compare field total vs terminal measurement
- Calculate shrinkage factor
- Apply evenly across partners

**Allocation Engine** (`calculators/allocation.py`):
- Proportional allocation based on contribution
- Handle rounding to maintain total
- Generate allocation breakdown

#### API Endpoints

```
GET  /health                           # Health check
GET  /status                           # Detailed status
POST /api/allocate                     # Run allocation
POST /api/reconcile                    # Run full reconciliation
GET  /api/reconciliation/{id}          # Get reconciliation result
```

#### Example Usage

```bash
curl -X POST http://localhost:8082/api/reconcile \
  -H "Content-Type: application/json" \
  -d '{
    "terminal_receipt_id": "receipt_67890",
    "period_start": "2025-10-01T00:00:00Z",
    "period_end": "2025-10-20T23:59:59Z"
  }'
```

---

### 3. Communicator Agent (Port 8083)

**Purpose**: Generate reports and send notifications

#### Core Responsibilities

- **Report Generation**: Create human-readable summaries using Gemini
- **Notification Distribution**: Send notifications to stakeholders
- **Multi-Format Support**: Generate reports in various formats
- **Personalization**: Customize reports for different user roles
- **Audit Trail**: Log all communication activities

#### Key Functions

```python
class CommunicatorAgent:
    async def generate_summary(self, reconciliation_id: str) -> str:
        """
        Generate AI summary of reconciliation

        Steps:
        1. Fetch reconciliation results
        2. Use Gemini to generate natural language summary
        3. Personalize for audience
        4. Return formatted summary
        """
        pass

    async def notify_stakeholders(self, reconciliation_id: str, recipient_ids: List[str]) -> None:
        """
        Send notifications to stakeholders

        Steps:
        1. Generate summary
        2. Create notification documents in Firestore
        3. Frontend displays in notification center
        """
        pass
```

#### API Endpoints

```
GET  /health                           # Health check
GET  /status                           # Detailed status
POST /api/notify                       # Send notifications
POST /api/generate-summary             # Generate AI summary
GET  /api/notifications/{user_id}      # Get user notifications
```

#### Example Usage

```bash
curl -X POST http://localhost:8083/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "reconciliation_id": "recon_11111",
    "recipient_ids": ["user_001", "user_002", "user_003"]
  }'
```

---

## Shared Infrastructure

### Configuration Management (`shared/config.py`)

Centralized configuration using Pydantic Settings:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Google Cloud
    google_cloud_project: str
    gcp_region: str = "europe-west1"

    # Firebase
    firebase_project_id: str
    firebase_client_email: str
    firebase_private_key: str

    # Gemini AI
    gemini_api_key: str

    # Application
    environment: str = "development"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
```

### Structured Logging (`shared/logger.py`)

JSON-formatted logging for Cloud Run:

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ["args", "asctime", "created", ...]:
                log_data[key] = value

        return json.dumps(log_data)

logger = logging.getLogger("flowshare")
```

### Firestore Client (`shared/firestore_client.py`)

Wrapper for Firestore operations:

```python
from google.cloud import firestore
from firebase_admin import firestore as admin_firestore

class FirestoreClient:
    def __init__(self):
        self.db = admin_firestore.client()

    async def get_document(self, collection: str, doc_id: str) -> dict:
        """Get a document"""
        doc = self.db.collection(collection).document(doc_id).get()
        return doc.to_dict() if doc.exists else None

    async def query_collection(self, collection: str, filters: list) -> list:
        """Query a collection"""
        query = self.db.collection(collection)
        for field, operator, value in filters:
            query = query.where(field, operator, value)
        return [doc.to_dict() for doc in query.stream()]
```

### Gemini Client (`shared/gemini_client.py`)

Wrapper for Gemini AI API:

```python
from google import genai

class GeminiClient:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash-exp"

    async def generate_text(self, prompt: str, context: dict = None) -> str:
        """Generate text using Gemini"""
        full_prompt = self._build_prompt(prompt, context)
        response = self.client.models.generate_content(
            model=self.model,
            contents=full_prompt
        )
        return response.text
```

### Middleware Stack

**Security Headers** (`shared/middleware/security.py`):
- HSTS (HTTP Strict Transport Security)
- Content Security Policy
- X-Frame-Options
- X-Content-Type-Options

**Request Tracking** (`shared/middleware/tracking.py`):
- Generate unique request IDs
- Log request/response timing
- Track request metadata

**Rate Limiting** (`shared/middleware/rate_limit.py`):
- In-memory rate limiting
- Configurable limits per endpoint
- 429 responses for exceeded limits

**Timeout Management** (`shared/middleware/timeout.py`):
- Automatic request timeout
- Configurable per-agent
- Graceful timeout responses

---

## API Documentation

### Interactive API Docs

Each agent provides interactive API documentation (in development mode):

- **Auditor Agent**: [http://localhost:8081/docs](http://localhost:8081/docs)
- **Accountant Agent**: [http://localhost:8082/docs](http://localhost:8082/docs)
- **Communicator Agent**: [http://localhost:8083/docs](http://localhost:8083/docs)

### Common Response Formats

#### Success Response

```json
{
  "status": "success",
  "data": { ... },
  "request_id": "req_12345abcde",
  "timestamp": "2025-10-20T10:30:00Z"
}
```

#### Error Response

```json
{
  "status": "error",
  "error": "Validation failed",
  "message": "Production entry not found",
  "request_id": "req_12345abcde",
  "timestamp": "2025-10-20T10:30:00Z"
}
```

### Health Check Response

```json
{
  "status": "healthy",
  "agent": "Accountant Agent",
  "version": "1.0.0",
  "timestamp": "2025-10-20T10:30:00Z",
  "dependencies": {
    "firestore": "connected",
    "gemini": "available"
  }
}
```

---

## Deployment

### Manual Deployment to Cloud Run

#### 1. Authenticate with GCP

```bash
gcloud auth login
gcloud config set project <project-id>
```

#### 2. Build and Deploy Auditor Agent

```bash
cd auditor-agent

# Build container
gcloud builds submit --tag gcr.io/<project-id>/auditor-agent

# Deploy to Cloud Run
gcloud run deploy auditor-agent \
  --image gcr.io/<project-id>/auditor-agent \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8081 \
  --set-env-vars "FIREBASE_PROJECT_ID=<project-id>,GEMINI_API_KEY=$GEMINI_API_KEY"
```

#### 3. Deploy Accountant Agent

```bash
cd accountant-agent

gcloud builds submit --tag gcr.io/<project-id>/accountant-agent

gcloud run deploy accountant-agent \
  --image gcr.io/<project-id>/accountant-agent \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8082 \
  --set-env-vars "FIREBASE_PROJECT_ID=<project-id>,GEMINI_API_KEY=$GEMINI_API_KEY"
```

#### 4. Deploy Communicator Agent

```bash
cd communicator-agent

gcloud builds submit --tag gcr.io/<project-id>/communicator-agent

gcloud run deploy communicator-agent \
  --image gcr.io/<project-id>/communicator-agent \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8083 \
  --set-env-vars "FIREBASE_PROJECT_ID=<project-id>,GEMINI_API_KEY=$GEMINI_API_KEY"
```

### Deployment Configuration

#### Cloud Run Service Configuration

- **Concurrency**: 80 requests per container
- **CPU**: 1 vCPU
- **Memory**: 512 MB
- **Max Instances**: 10 (auto-scaling)
- **Min Instances**: 0 (scale to zero)
- **Timeout**: 300 seconds

---

## CI/CD Pipeline

### GitHub Actions Workflow

Each agent has its own deployment workflow in `.github/workflows/`:

#### Example: `deploy-accountant.yml`

```yaml
name: Deploy Accountant Agent to Cloud Run

on:
  push:
    branches:
      - main
    paths:
      - 'flowshare-agents-backend/accountant-agent/**'
      - 'flowshare-agents-backend/shared/**'

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: <project-id>

      - name: Build and push Docker image
        run: |
          cd flowshare-agents-backend/accountant-agent
          gcloud builds submit --tag gcr.io/<project-id>/accountant-agent

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy accountant-agent \
            --image gcr.io/<project-id>/accountant-agent \
            --platform managed \
            --region europe-west1 \
            --allow-unauthenticated \
            --set-env-vars "FIREBASE_PROJECT_ID=${{ secrets.FIREBASE_PROJECT_ID }},GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }}"
```

### Deployment Triggers

- **Automatic**: Pushed to `main` branch with changes in agent directory
- **Manual**: Via GitHub Actions UI
- **Rollback**: Deploy previous container image

---

## Monitoring & Logging

### Cloud Logging

View logs in Google Cloud Console:

```bash
# View Accountant Agent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=accountant-agent" --limit 50

# Stream logs in real-time
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=accountant-agent"
```

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical failures requiring immediate attention

### Request Tracking

Every request has a unique `X-Request-ID` header for tracing across services.

Example log entry:

```json
{
  "timestamp": "2025-10-20T10:30:00Z",
  "level": "INFO",
  "logger": "accountant-agent",
  "message": "Reconciliation completed successfully",
  "request_id": "req_abc123",
  "duration_ms": 1234,
  "reconciliation_id": "recon_xyz",
  "partners": 5,
  "total_volume": 15000.5
}
```

### Health Monitoring

Cloud Run automatically monitors:
- **CPU Usage**
- **Memory Usage**
- **Request Count**
- **Request Latency**
- **Error Rate**

Set up alerts in Cloud Monitoring for:
- High error rate (>5%)
- High latency (>2s p99)
- Container crashes

---

## Testing

### Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

### Integration Tests

```bash
# Test with running agents
pytest tests/integration/
```

### Manual API Testing

```bash
# Test Accountant Agent health
curl http://localhost:8082/health

# Test reconciliation endpoint
curl -X POST http://localhost:8082/api/reconcile \
  -H "Content-Type: application/json" \
  -d '{"terminal_receipt_id": "test_receipt"}'
```

### Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Load test health endpoint
ab -n 1000 -c 10 http://localhost:8082/health
```

---

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find process using port 8082
lsof -ti:8082

# Kill the process
kill -9 $(lsof -ti:8082)
```

#### Import Errors

```bash
# Ensure shared module is in Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/flowshare-agents-backend"

# Or add to main.py
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```

#### Firebase Authentication Errors

- Verify `.env` has correct credentials
- Check service account has Firestore permissions
- Ensure Firebase project ID matches

#### Gemini API Errors

- Verify `GEMINI_API_KEY` is set correctly
- Check API quota limits
- Ensure Generative AI API is enabled in GCP

### Debugging

#### Enable Debug Logging

```bash
# Set in .env
LOG_LEVEL=DEBUG

# Or set environment variable
export LOG_LEVEL=DEBUG
```

#### View Detailed Error Traces

```python
# In main.py, add:
import traceback

@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    raise exc
```

---

## Performance Optimization

### Best Practices

1. **Connection Pooling**: Reuse Firestore connections
2. **Caching**: Cache frequently accessed data
3. **Batch Operations**: Use Firestore batch writes
4. **Async Operations**: Use async/await throughout
5. **Resource Limits**: Set appropriate CPU and memory

### Scaling Configuration

```bash
# Increase max instances
gcloud run services update accountant-agent \
  --max-instances 100

# Set minimum instances (avoid cold starts)
gcloud run services update accountant-agent \
  --min-instances 1

# Increase CPU and memory
gcloud run services update accountant-agent \
  --cpu 2 \
  --memory 1Gi
```

---

## Security

### Security Best Practices

1. **Environment Variables**: Never commit secrets to Git
2. **Service Accounts**: Use minimal permissions
3. **CORS**: Restrict to known origins
4. **Rate Limiting**: Prevent abuse
5. **Input Validation**: Validate all inputs with Pydantic
6. **HTTPS Only**: Enforce HTTPS in production

### Firestore Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Require authentication
    match /{document=**} {
      allow read, write: if request.auth != null;
    }

    // Role-based access
    match /production_entries/{entry} {
      allow create: if request.auth.token.role == 'field_operator';
      allow update: if request.auth.token.role in ['field_operator', 'jv_coordinator'];
      allow read: if request.auth != null;
    }
  }
}
```

---

## Contributing

### Development Workflow

1. **Create Feature Branch**: `git checkout -b feature/your-feature`
2. **Implement Changes**: Follow coding standards
3. **Test Locally**: Run all tests
4. **Lint Code**: Follow PEP 8 style guide
5. **Commit Changes**: Use conventional commits
6. **Push Branch**: `git push origin feature/your-feature`
7. **Create Pull Request**: On GitHub

### Code Standards

- **Python Style**: Follow PEP 8
- **Type Hints**: Use type hints for all functions
- **Docstrings**: Document all public functions
- **Naming**:
  - Functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`

### Git Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance

---

## License

Proprietary - All rights reserved

---

## Support

For questions or issues:

- **GitHub Issues**: Create an issue
- **Email**: todak2000@gmail.com

---

## Acknowledgments

- Built for Google Cloud Run Hackathon 2025
- Powered by FastAPI and Google Cloud
- AI capabilities by Google Gemini

---

**Built with engineering excellence by the FlowShare Engineering Team**
