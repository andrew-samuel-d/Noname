from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import shutil
from services.batch_scorer import score_excel

router = APIRouter(prefix="/batch", tags=["Batch Scoring"])


@router.post("/score-excel")
async def batch_score_endpoint(file: UploadFile = File(...)):
    if not (file.filename.endswith(".xlsx") or file.filename.endswith(".xls")):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are supported.")

    upload_dir = "data"
    os.makedirs(upload_dir, exist_ok=True)
    input_path = os.path.join(upload_dir, f"upload_{file.filename}")
    output_path = os.path.join(upload_dir, f"scored_{file.filename}")

    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        score_excel(input_path, output_path)

        return FileResponse(
            output_path,
            filename=f"scored_{file.filename}",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch scoring error: {str(e)}")
