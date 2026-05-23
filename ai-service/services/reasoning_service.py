from google import genai
from google.genai import types
from pydantic import BaseModel
from core.config import GEMINI_API_KEY, MODEL_NAME

from models.schemas import DepartmentRecommendationResponse, SymptomAnalysisResponse

client = genai.Client(api_key=GEMINI_API_KEY)

def analyze_symptoms(symptoms: list[str]):
    prompt = f"""
    You are an internal medical reasoning engine for a hospital orchestration system.

    Patient symptoms:
    {symptoms}

    Your responsibilities:
    - analyze symptoms conservatively
    - explain symptoms briefly in simple language
    - identify appropriate hospital departments
    - prefer the SINGLE most relevant department when possible

    IMPORTANT RESTRICTIONS:
    - Do NOT diagnose diseases
    - Do NOT prescribe medications
    - Do NOT recommend dosages
    - Do NOT claim certainty
    - Avoid alarming language
    - Keep analysis concise and practical

    EMERGENCY RULE:
    If symptoms appear severe or dangerous, recommend urgent medical attention.

    DEPARTMENT ROUTING EXAMPLES:
    - Chest pain: Cardiology
    - Headache/migraine: Neurology
    - Bone/joint pain: Orthopedics
    - Skin issues: Dermatology
    - Fever/general illness: General Medicine
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SymptomAnalysisResponse,
            temperature=0
        )
    )

    parsed = response.parsed

    return {
        "symptoms": symptoms,
        "analysis": parsed.analysis,
        "suggested_departments": parsed.suggested_departments or []
    }

def recommend_departments(symptoms: list[str]):    
    prompt = f"""
        You are an internal department recommendation engine for a hospital orchestration system.

        Patient symptoms:
        {symptoms}

        Your task:
        - identify the most appropriate hospital departments
        - return only real hospital departments
        - prefer broad standard departments
        - keep explanation concise

        DEPARTMENT ROUTING EXAMPLES:
        - Chest pain: Cardiology
        - Skin issues: Dermatology
        - Headaches/migraines: Neurology
        - Bone/joint pain: Orthopedics
        - Fever/general illness: General Medicine

        IMPORTANT:
        - Do NOT diagnose diseases
        - Do NOT recommend medicines
        - Do NOT provide treatment advice
        """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DepartmentRecommendationResponse,
            temperature=0
        )
    )

    parsed = response.parsed

    return {
        "symptoms": symptoms,
        "departments": parsed.departments,
        "recommendation": parsed.explanation
    }

