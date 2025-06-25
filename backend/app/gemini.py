import os
import google.genai as genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Client Initialization ---
api_key = os.getenv("GEMINI_API_KEY")
client = None
if not api_key:
    print("Warning: GEMINI_API_KEY not found. Gemini features will be disabled.")
else:
    # The new, correct way to initialize the client
    client = genai.Client(api_key=api_key)

# --- Model Configuration ---
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

def generate_training_plan_from_prompt(prompt: str) -> str | None:
    """
    Generates a structured training plan from a user prompt using the Gemini API.
    This function now uses the new Client API.
    """
    if not client:
        print("Gemini client is not initialized. Cannot generate plan.")
        return None

    # The prompt asks for a structured JSON response.
    full_prompt = f"""Crée un plan d'entraînement basé sur cette demande de l'utilisateur : '{prompt}'.

La réponse DOIT être un objet JSON valide et rien d'autre. La structure doit être la suivante :
{{
  "name": "Nom du plan (ex: Préparation Marathon en 16 semaines)",
  "goal": "Description de l'objectif (ex: Courir un marathon en moins de 4 heures)",
  "sessions": [
    {{
      "date": "YYYY-MM-DD",
      "type": "course_a_pied" | "cardio" | "repos" | "autre",
      "exercise": "Description de la séance (ex: 5km allure modérée)"
    }}
  ]
}}
"""

    try:
        # The new, correct way to call the model
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=full_prompt,
            config=types.GenerateContentConfig(**generation_config)
        )
        return response.text
    except Exception as e:
        print(f"Error generating plan with Gemini: {e}")
        return None
