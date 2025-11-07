import pandas as pd
from pathlib import Path

src = Path("data/scored_responses_with_reasons_backup.csv")
dest = Path("data/scored_responses_with_reasons_fixed.csv")

df = pd.read_csv(src, on_bad_lines="skip")
print("Loaded:", df.shape, "columns:", list(df.columns))

# Write safely with proper quoting and newlines
df.to_csv(dest, index=False, quoting=1, lineterminator="\n")
print("✅ Clean CSV written to", dest.resolve())
