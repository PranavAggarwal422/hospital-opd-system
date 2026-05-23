from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash-lite"
TEMPERATURE = 0.1
MAX_OUTPUT_TOKENS = 500

