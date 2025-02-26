from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import spacy
from docx import Document
import PyPDF2
from io import BytesIO

# Initialize FastAPI app
app = FastAPI()

# Load spaCy model for Named Entity Recognition (NER)
nlp = spacy.load("en_core_web_sm")

# Add CORS middleware to your FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can restrict this to your React app's URL in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Define Pydantic model for receiving JSON data (example)
class Person(BaseModel):
    name: str
    age: int

# POST route to handle JSON data
@app.post("/create-person")
async def create_person(person: Person):
    return {"message": f"Person {person.name} with age {person.age} has been created!"}

# POST route to handle file uploads (PDF and DOCX)
@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    filename = file.filename
    file_content = await file.read()

    # Check if the file is a PDF
    if filename.endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

            # Return the success message along with the extracted text (first 500 characters)
            return {"message": "File uploaded and analyzed successfully!", "extracted_text": text[:500]}  # Display the first 500 chars of the extracted text
        except Exception as e:
            return {"error": f"Error reading PDF: {str(e)}"}
    else:
        return {"error": "File must be a PDF"}

# Helper function to extract text from PDF
def extract_pdf_text(file_content: bytes):
    """Extract text from a PDF file"""
    reader = PyPDF2.PdfReader(BytesIO(file_content))
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

# Helper function to extract text from DOCX
def extract_docx_text(file_content: bytes):
    """Extract text from a DOCX file"""
    doc = Document(BytesIO(file_content))
    text = ''
    for para in doc.paragraphs:
        text += para.text + '\n'
    return text

# Function to analyze the resume content (AI-based using spaCy)
def analyze_resume(text: str):
    """Analyze resume text and extract key information using spaCy"""
    doc = nlp(text)

    entities = {"names": [], "skills": [], "organizations": []}

    # Extract named entities (PERSON, ORG, etc.)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            entities["names"].append(ent.text)
        elif ent.label_ == "ORG":
            entities["organizations"].append(ent.text)

    # Example skills list (expand this as needed)
    skills_keywords = ["Python", "Java", "C++", "Machine Learning", "Data Science"]
    for word in doc:
        if word.text in skills_keywords:
            entities["skills"].append(word.text)

    return entities

# POST route to handle form data
@app.post("/submit-form")
async def submit_form(name: str = Form(...), age: int = Form(...)):
    return {"message": f"Form submitted! Name: {name}, Age: {age}"}

# Simple GET route for testing the server is running
@app.get("/")
async def read_root():
    return {"message": "Server is running! Send POST requests to /create-person, /upload-resume, or /submit-form."}
