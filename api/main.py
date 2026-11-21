from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from starlette.background import BackgroundTask

from services.batch_scorer import score_excel
from .scoring_service import score_business

import json
import os
import tempfile


# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(
    title="CashFlowScore API",
    version="1.0"
)


# =====================================================
# PATH RESOLVER
# =====================================================

def resolve_model_file(filename: str) -> str:
    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model", filename),
        os.path.join("model", filename),
        os.path.join("..", "model", filename)
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return os.path.join("model", filename)


def get_data_dir() -> str:
    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"),
        os.path.join("data"),
        os.path.join("..", "data")
    ]
    for d in candidates:
        if os.path.exists(d):
            return d
    target = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(target, exist_ok=True)
    return target


# =====================================================
# HEALTH
# =====================================================

@app.get("/health")
def health():
    model_exists = os.path.exists(resolve_model_file("xgb_model.json"))
    metrics_exists = os.path.exists(resolve_model_file("metrics.json"))

    redis_status = "not_configured"
    try:
        import redis
        r = redis.Redis(host="localhost", port=6379, socket_timeout=1)
        r.ping()
        redis_status = "connected"
    except Exception:
        redis_status = "unavailable (running in standalone mode)"

    return {
        "status": "healthy" if model_exists else "degraded",
        "model_loaded": model_exists,
        "metrics_loaded": metrics_exists,
        "redis": redis_status
    }


# =====================================================
# FRONTEND & DASHBOARD
# =====================================================

def resolve_frontend_html() -> str:
    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "index.html"),
        os.path.join("frontend", "index.html"),
        os.path.join("..", "frontend", "index.html")
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return ""


@app.get("/", response_class=HTMLResponse)
def home():
    html_path = resolve_frontend_html()
    if html_path and os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>CashFlowScore API Running 🚀</h1><p>Visit <a href='/docs'>/docs</a></p>")


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return home()


@app.get("/api")
def api_status():
    return {
        "message": "CashFlowScore API Running 🚀",
        "version": "1.0",
        "endpoints": ["/", "/dashboard", "/health", "/score", "/score-batch", "/docs"]
    }


@app.get("/data/{filename}")
def download_data_file(filename: str):
    data_dir = get_data_dir()
    if os.path.basename(filename) != filename or filename in {".", ".."}:
        raise HTTPException(status_code=400, detail="Invalid file name")
    filepath = os.path.join(data_dir, filename)
    if os.path.exists(filepath):
        return FileResponse(filepath)
    raise HTTPException(status_code=404, detail="Data file not found")


# =====================================================
# LOAD METRICS
# =====================================================

def load_metrics():
    path = resolve_model_file("metrics.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {}


# =====================================================
# LOAD FEATURE IMPORTANCE
# =====================================================

def load_feature_importance():
    path = resolve_model_file("feature_importance.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return []


# =====================================================
# SCORE
# =====================================================

@app.post("/score")
def score(features: dict):
    try:
        result = score_business(features)
        if "error" in result:
            raise HTTPException(status_code=400, detail=f"Scoring error: {result['error']}")

        metrics = load_metrics()
        result["model_metrics"] = {
            "baseline_accuracy": metrics.get("baseline_accuracy"),
            "train_accuracy": metrics.get("train_accuracy"),
            "test_accuracy": metrics.get("test_accuracy"),
            "accuracy": metrics.get("accuracy"),
            "precision": metrics.get("precision"),
            "recall": metrics.get("recall"),
            "f1_score": metrics.get("f1_score"),
            "auc": metrics.get("auc"),
            "cross_validation_mean": metrics.get("cross_validation_mean"),
            "cross_validation_std": metrics.get("cross_validation_std"),
            "train_test_gap": metrics.get("train_test_gap"),
            "improvement_percentage_points": metrics.get("improvement_percentage_points")
        }

        result["feature_importance"] = load_feature_importance()
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal prediction error: {str(e)}")


# =====================================================
# BATCH EXCEL / CSV
# =====================================================

@app.post("/score-batch")
async def score_batch(file: UploadFile = File(...)):
    input_path = None
    output_path = None
    try:
        original_name = (file.filename or "businesses.xlsx").replace("\\", "/").rsplit("/", 1)[-1]
        ext = os.path.splitext(original_name)[1].lower()
        if ext not in {".csv", ".xlsx"}:
            raise HTTPException(status_code=400, detail="Upload a .xlsx or .csv file.")
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Upload a file smaller than 10 MB.")

        data_dir = get_data_dir()
        os.makedirs(data_dir, exist_ok=True)
        input_fd, input_path = tempfile.mkstemp(prefix="score_input_", suffix=ext, dir=data_dir)
        output_fd, output_path = tempfile.mkstemp(prefix="score_output_", suffix=ext, dir=data_dir)
        os.close(input_fd)
        os.close(output_fd)
        with open(input_path, "wb") as f:
            f.write(content)

        summary = score_excel(input_path, output_path)

        media_type = "text/csv" if ext == ".csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        download_name = f"scored_{os.path.splitext(original_name)[0]}{ext}"

        def cleanup_files():
            for path in (input_path, output_path):
                try:
                    os.remove(path)
                except OSError:
                    pass

        return FileResponse(
            output_path,
            filename=download_name,
            media_type=media_type,
            headers={
                "X-Score-Records": str(summary["records"]),
                "X-Score-Approved": str(summary["approved"]),
                "X-Score-Rejected": str(summary["rejected"]),
                "X-Score-Average": str(summary["average_score"]),
                "Access-Control-Expose-Headers": "X-Score-Records, X-Score-Approved, X-Score-Rejected, X-Score-Average",
            },
            background=BackgroundTask(cleanup_files),
        )
    except HTTPException:
        raise
    except ValueError as e:
        for path in (input_path, output_path):
            if path:
                try:
                    os.remove(path)
                except OSError:
                    pass
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        for path in (input_path, output_path):
            if path:
                try:
                    os.remove(path)
                except OSError:
                    pass
        raise HTTPException(status_code=500, detail=f"Batch scoring failed: {str(e)}")
