import os
import re
import base64
import time
import csv
from datetime import datetime
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
    pos = int(re.search(r"Immunopositive cells?:\s*(\d+)", text, re.I).group(1)) if re.search(r"Immunopositive cells?:\s*(\d+)", text, re.I) else 0
    neg = int(re.search(r"Immunonegative cells?:\s*(\d+)", text, re.I).group(1)) if re.search(r"Immunonegative cells?:\s*(\d+)", text, re.I) else 0
    m = re.search(r"Ki[\s-]?67[^%]*?([0-9]+(?:\.[0-9]+)?)\s*%", text, re.I | re.S)
    if m:
        ki = float(m.group(1))
    else:
        p = re.findall(r"([0-9]+(?:\.[0-9]+)?)\s*%", text)
        ki = float(p[-1]) if p else 0.0
    return pos, neg, ki


def predict_with_gpt(img_path: Path):
    start = time.time()
    img_b64 = base64.b64encode(img_path.read_bytes()).decode()
    mime = "jpeg" if img_path.suffix.lower() in {'.jpg', '.jpeg'} else "png"

    r = client.chat.completions.create(
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

    duration = time.time() - start
    content = r.choices[0].message.content
    usage = r.usage
    pos, neg, ki = extract_cell_counts_and_index(content)

    return pos, neg, ki, content, usage.prompt_tokens, usage.completion_tokens, usage.total_tokens, duration

def analyze_10_samples(dataset: Path, out_parent: Path, n: int = 10) -> None:
    timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    output_dir = out_parent / f"output_time_analysis_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "ki67_10_samples_analysis.csv"
    resp_path = output_dir / "ki67_10_samples_responses.txt"

    images = [
        p for p in sorted(dataset.iterdir())
        if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
        and (dataset / f"{p.stem}.json").is_file()
    ][:n]

    if not images:
        print("No images found.")
        return

    times, prompt_t, compl_t, total_t = [], [], [], []

    with csv_path.open("w", newline="", encoding="utf-8") as csvf, resp_path.open("w", encoding="utf-8") as respf:
        writer = csv.writer(csvf)
        writer.writerow([
            "image", "input_tokens", "output_tokens", "total_tokens",
            "ki67_index", "immunopositive_cells", "immunonegative_cells"
        ])

        for idx, img in enumerate(images, 1):
            print(f"[{idx}/{len(images)}] {img.name}")
            try:
                pos, neg, ki, full, in_tok, out_tok, tot_tok, elapsed = predict_with_gpt(img)

                writer.writerow([img.name, in_tok, out_tok, tot_tok, f"{ki:.2f}", pos, neg])

                respf.write(f"\n===== {img.name} =====\n")
                respf.write(f"Time: {elapsed:.2f}s | Tokens: {tot_tok}\n")
                respf.write(full.strip() + "\n")

                times.append(elapsed)
                prompt_t.append(in_tok)
                compl_t.append(out_tok)
                total_t.append(tot_tok)
            except Exception as e:
                print(f"Error with {img.name}: {e}")

    if times:
        print("\nAVERAGE METRICS SUMMARY")
        print(f"Average time         : {sum(times)/len(times):.2f}s")
        print(f"Average input tokens : {sum(prompt_t)/len(prompt_t):.0f}")
        print(f"Average output tokens: {sum(compl_t)/len(compl_t):.0f}")
        print(f"Average total tokens : {sum(total_t)/len(total_t):.0f}")
        print(f"Results saved in     : {output_dir}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print(
            "Usage:\n"
            "  python 4.utils/calculate_time_average.py <processed_dataset> <output_parent_dir>\n"
            "Example:\n"
            "  python 4.utils/calculate_time_average.py "
            "1.data_access/data_sample/3.data_processed "
            "5.results"
        )
        sys.exit(1)

    dataset_dir = Path(sys.argv[1]).resolve()
    out_parent_dir = Path(sys.argv[2]).resolve()

    if not dataset_dir.is_dir():
        sys.exit(f"Dataset folder not found: {dataset_dir}")
    if not out_parent_dir.is_dir():
        sys.exit(f"Output parent dir not found: {out_parent_dir}")

    analyze_10_samples(dataset_dir, out_parent_dir)