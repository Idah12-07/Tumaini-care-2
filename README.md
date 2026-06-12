# 🌱 Tumaini Care

**AI-Powered Post-Pregnancy Loss Surveillance & Support System**

---

## What is Tumaini?

Tumaini (hope in Swahili) monitors women's health and provides emotional
support in the critical 48-72 hours after early pregnancy loss, operating
via WhatsApp, SMS, and USSD with CHW integration and DHIS2 reporting.

## Quick Start

\\\ash
# Clone and setup
git clone <your-repo-url>
cd tumaini-care

# Backend
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
\\\

## Project Structure

\\\
tumaini-care/
├── frontend/          React dashboard + AI companion UI
├── backend/           FastAPI AI engine + triage logic
├── data/              Synthetic datasets (safe to share)
├── docs/              Clinical protocols + architecture
└── scripts/           Setup, migration, deployment utilities
\\\

## Stack

| Layer | Tools |
|---|---|
| Frontend | React, Vite, Tailwind |
| Backend | FastAPI, Python, LangChain |
| AI | Claude API (Anthropic) |
| Database | PostgreSQL, Redis |
| Messaging | RapidPro, Africa's Talking |
| Health system | DHIS2 (KHIS), Community Health Toolkit |
| Analytics | Metabase |

---
Prepared by: Idah Anyango 
