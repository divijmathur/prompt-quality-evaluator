# src/auto_evaluator.py
import json
import pandas as pd
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RUBRIC = """
You are an evaluator. Rate the given response from 1–5 on:
1. Clarity (Is it well-structured and understandable?)
2. Factuality (Is it accurate and non-hallucinatory?)
3. Style (Is it engaging, concise, and appropriate?)

Also provide one short explanation for each score.

Respond ONLY in JSON format:
{
  "clarity": {"score": x, "reason": "short text"},
  "factuality": {"score": y, "reason": "short text"},
  "style": {"score": z, "reason": "short text"}
}
"""

def evaluate_responses(input_csv: Path, output_csv: Path, model="gpt-4o-mini"):
    print(f"🔍 Loading input CSV: {input_csv}")
    if not input_csv.exists():
        print(f"❌ File not found: {input_csv}")
        return

    df = pd.read_csv(input_csv)
    print(f"Found {len(df)} rows to evaluate.")
    scores, reasons = [], []

    for i, row in df.iterrows():
        print(f"🧠 Evaluating row {i+1}/{len(df)}: {row['prompt'][:50]}...")
        eval_prompt = f"{RUBRIC}\n\nPrompt: {row['prompt']}\nResponse: {row['response']}"
        result = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": eval_prompt}]
        )
        try:
            content = result.choices[0].message.content
            data = json.loads(content)
            scores.append({
                "clarity": data["clarity"]["score"],
                "factuality": data["factuality"]["score"],
                "style": data["style"]["score"]
            })
            reasons.append({
                "clarity_reason": data["clarity"]["reason"],
                "factuality_reason": data["factuality"]["reason"],
                "style_reason": data["style"]["reason"]
            })
        except Exception as e:
            print(f"⚠️ Error parsing JSON for row {i}: {e}")
            print("Raw response:", result.choices[0].message.content)
            scores.append({"clarity": None, "factuality": None, "style": None})
            reasons.append({"clarity_reason": "", "factuality_reason": "", "style_reason": ""})

    scores_df = pd.DataFrame(scores)
    reasons_df = pd.DataFrame(reasons)
    final_df = pd.concat([df, scores_df, reasons_df], axis=1)
    final_df.to_csv(output_csv, index=False)
    print(f"✅ Scored responses with reasons saved to {output_csv}")

if __name__ == "__main__":
    evaluate_responses(Path("data/responses.csv"), Path("data/scored_responses_with_reasons.csv"))