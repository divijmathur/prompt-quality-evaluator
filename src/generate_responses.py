# src/generate_responses.py
from pathlib import Path
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_responses(input_csv: Path, output_csv: Path):
    prompts = pd.read_csv(input_csv)
    responses = []
    for p in prompts["prompt"]:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": p}]
        )
        responses.append(r.choices[0].message.content)
    prompts["response"] = responses
    prompts.to_csv(output_csv, index=False)
    print(f"✅ Responses saved to {output_csv}")

if __name__ == "__main__":
    generate_responses(Path("data/prompts.csv"), Path("data/responses.csv"))