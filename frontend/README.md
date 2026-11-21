# CashFlowScore Frontend 🚀
### Real-Time Credit Scoring for India's Unbanked MSMEs
**FINANCE · F2: Credit for the Credit-Invisible**

A modern **React** Single-Page Application (SPA) designed as an institutional **Lender Dashboard** for mid-size NBFCs and Small Finance Banks. 

---

## 🛠️ Complete Tech Stack Mapping (From Slides 4 & 5)

| Component | Technology | Role in Dashboard |
| :--- | :--- | :--- |
| **Frontend UI** | **React 18, Tailwind CSS** | Real-time Lender Dashboard, Gauges, Excel batch interface |
| **API Layer** | **FastAPI, Python 3.13** | High-throughput asynchronous REST gateway |
| **ML Engine** | **XGBoost 3.3.0** | Gradient boosted decision trees trained on 11 MSME features |
| **Explainability** | **SHAP** | Auditor-ready, plain-English reasons & feature impact |
| **Event Ingestion**| **Kafka Event Bus** | Streaming simulation for live UPI / Bank / GST events |
| **Caching & Dedup**| **Redis** | Sub-millisecond feature lookup, dedup & score caching |
| **History Store** | **TimescaleDB** | Time-series historical financial ledger tracking |
| **Zero-Internet** | **Edge Offline Mode** | Full client & local Python model evaluation without internet |

---

## 🌟 Dashboard Features

1. **📊 Portfolio Overview & MSME Macro Impact (Slide 2 & 7)**
   - Tracks India's **₹25 Lakh Crore** unmet credit gap (Deloitte 2025).
   - Displays the **14% formal credit access** reality vs 86% unbanked opportunity.
   - Live **Kafka Event Stream ticker** showing real-time UPI, Bank, and GST inflow events.

2. **⚡ Real-Time Single Business Underwriter (Slide 2 & 4)**
   - **3-in-1 Fusion:** Ingests UPI transaction flows, net banking statements, and GST tax compliance.
   - **Interactive Score Gauge (0–100):** Visual risk tier (`Low Risk`, `Moderate Risk`, `High Risk`) and approval decision badge.
   - **Auditor-Ready SHAP Explanations:** Plain-English reasons explaining every positive and negative driver.
   - **Pre-loaded Quick Presets:** Kiran Supermarket (Prime), Sri Krishna Textiles (Moderate), New Age Fabrication (Young), City Logistics (High Risk).
   - **RBI Account Aggregator (AA) Consent Toggle:** Demonstrates consent-only architecture.

3. **📑 Bulk Excel / CSV Underwriting (Slide 5)**
   - Drag-and-drop batch upload (`.xlsx` or `.csv`).
   - One-click load of the **100 Sample Businesses Benchmark** (`sample_100_businesses_input.xlsx`).
   - In-browser portfolio preview and download of scored Excel file.

4. **🛰️ Architecture & System Telemetry Explorer (Slide 5)**
   - Interactive visual flow of the event-driven ingestion pipeline.
   - Real-time telemetry cards for FastAPI, XGBoost, SHAP, Kafka, Redis, and TimescaleDB.

5. **📖 Hackathon Pitch Deck & Competitive Novelty (Slide 3 & 6)**
   - Feature comparison matrix: Perfios/Jocata vs In-House Models vs Bureau+GST Hybrids vs CashFlowScore.
   - B2B SaaS unit economics and consent-first regulatory moat.

---

## 🚀 How to Run

### Method 1: Instant In-Browser (Served via FastAPI)
No separate Node.js server needed! FastAPI automatically serves the React dashboard at root:

```powershell
uv run uvicorn api.main:app --reload
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser!

### Method 2: Standalone React Dev Server (Vite)
If you wish to run a dedicated Vite development server:

```powershell
cd frontend
npm install
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)**.
