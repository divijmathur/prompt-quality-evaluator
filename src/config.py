from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
EVAL_MODEL_NAME = os.getenv("EVAL_MODEL_NAME", "gpt-4o")
DATABASE_PATH = os.getenv("DATABASE_PATH", "db/evals.db")