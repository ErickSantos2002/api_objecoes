# config.py
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("A variável OPENAI_API_KEY não foi encontrada no .env")  # noqa: W292, E501