from fastapi import FastAPI, File, UploadFile
import aiofiles

app = FastAPI()

# Dummy function to analyze resume (we will improve this later)
async def analyze_resume(content: str) -> dict:
    response = {"score": 85, "feedback": "Consider adding more industry-specific keywords."}
    return response

@app.get("/")
async def home():
    return {"message": "Welcome to the AI Resume Analyzer!"}

@app.post("/analyze/")
async def upload_resume(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")  # Convert bytes to string
    result = await analyze_resume(text)
    return {"filename": file.filename, "analysis": result}
