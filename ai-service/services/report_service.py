from google import genai
from google.genai import types

from core.config import MODEL_NAME, GEMINI_API_KEY
from core.prompts import REPORT_PROMPT

from models.schemas import ReportExplanationResponse


client = genai.Client(api_key=GEMINI_API_KEY)

ALLOWED_MIME_TYPES = {"application/pdf", "image/png", "image/jpg", "image/jpeg"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# validate uploaded report file 
def validate_report_file(upload_file):
    if upload_file.content_type not in ALLOWED_MIME_TYPES:
        raise ValueError("Only PDF, PNG, JPG and JPEG medical reports are supported.")

    return True


def generate_report_response(contents):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction = REPORT_PROMPT,
            response_mime_type="application/json",
            response_schema=ReportExplanationResponse,
            temperature=0
        )
    )

    parsed = response.parsed

    return {
        "summary": parsed.summary,
        "notable_findings": parsed.notable_findings,
        "precautions": parsed.precautions,
        "doctor_consultation_recommended":parsed.doctor_consultation_recommended
    }


# TEXT-BASED REPORT EXPLANATION
def explain_report_text(report_text: str):
    contents = f"""Medical Report: {report_text}"""
    return generate_report_response(contents)


# FILE-BASED REPORT EXPLANATION
def explain_medical_report(file_bytes: bytes, mime_type: str):
    contents = [types.Part.from_bytes(data=file_bytes, mime_type=mime_type)]
    return generate_report_response(contents)

