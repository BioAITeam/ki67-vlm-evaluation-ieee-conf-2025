import os
import re
import base64
import sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise ValueError("OPENAI_API_KEY not found in environment.")
client = OpenAI(api_key=api_key)

this_dir = Path(__file__).parent
with (this_dir / "../3.vlm_processing/system_prompt.txt").open(encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()
with (this_dir / "../3.vlm_processing/user_prompt.txt").open(encoding="utf-8") as f:
    USER_PROMPT = f.read()

def extract_cell_counts_and_index(text: str) -> tuple[int, int, float]:
    """Return (pos_cells, neg_cells, ki67_index) extracted from the model text."""
    pos = int(re.search(r"Immunopositive cells?:\s*(\d+)", text, re.I).group(1)) if re.search(r"Immunopositive cells?:\s*(\d+)", text, re.I) else 0
    neg = int(re.search(r"Immunonegative cells?:\s*(\d+)", text, re.I).group(1)) if re.search(r"Immunonegative cells?:\s*(\d+)", text, re.I) else 0
    m = re.search(r"Ki[\s-]?67[^%]*?(\d+(?:\.\d+)?)\s*%", text, re.I)
    ki = float(m.group(1)) if m else 0.0
    return pos, neg, ki


def predict_ki67(img_path: Path) -> None:
    if not img_path.is_file() or img_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
        raise ValueError("Provide a valid .jpg, .jpeg or .png file.")

    img_b64 = base64.b64encode(img_path.read_bytes()).decode()
    mime = "jpeg" if img_path.suffix.lower() in {'.jpg', '.jpeg'} else "png"

    response = client.chat.completions.create(
        model="gpt-4.1-mini-2025-04-14",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": USER_PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:image/{mime};base64,{img_b64}"}},
                ],
            },
        ],
        temperature=0,
        seed=64,
        max_tokens=1024,
    )

    content = response.choices[0].message.content
    pos, neg, ki = extract_cell_counts_and_index(content)

    print("=" * 60)
    print(f"Image: {img_path.name}")
    print(content.strip())
    print()
    print(f"Immunopositive cells : {pos}")
    print(f"Immunonegative cells : {neg}")
    print(f"Ki-67 Index          : {ki:.2f}%")
    print()
    print("TOKEN USAGE")
    print(f"  Prompt     : {response.usage.prompt_tokens}")
    print(f"  Completion : {response.usage.completion_tokens}")
    print(f"  Total      : {response.usage.total_tokens}")
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(
            "Usage:\n"
            "  python 4.utils/predict_cells.py <image_path>\n"
            "Example:\n"
            "  python 4.utils/predict_cells.py 1.data_access/data_sample/3.data_processed/8.jpg"
        )
        sys.exit(1)

    predict_ki67(Path(sys.argv[1]).resolve())