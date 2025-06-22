import os
import re
import base64
import time
from openai import OpenAI
from dotenv import load_dotenv 

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise ValueError("OPENAI_API_KEY not found in environment. Did you create the .env file?")

client = OpenAI(api_key=api_key)

with open(os.path.join(os.path.dirname(__file__), "system_prompt.txt"), "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

with open(os.path.join(os.path.dirname(__file__), "user_prompt.txt"), "r", encoding="utf-8") as f:
    USER_PROMPT = f.read() 

def extract_predicted_index(text: str) -> float:
    preferred_pattern = re.compile(
        r"Ki[\s-]?67[^%]*?([0-9]+(?:\.[0-9]+)?)\s*%", flags=re.IGNORECASE | re.DOTALL
    )
    m = preferred_pattern.search(text)
    if m:
        return float(m.group(1))
    percentages = re.findall(r"([0-9]+(?:\.[0-9]+)?)\s*%", text)
    if percentages:
        return float(percentages[-1])
    raise ValueError("Could not find a Ki-67 value in the response:\n" + text)


def predict_with_timing(img_path: str):
    with open(img_path, "rb") as f:
        img_bytes = f.read()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    ext = os.path.splitext(img_path)[1].lower()
    mime = "jpeg" if ext in [".jpg", ".jpeg"] else "png"

    # Iniciar cronómetro
    start = time.time()

    # Ejecutar la predicción
    response = client.chat.completions.create(
        model="gpt-4.1-mini-2025-04-14",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": USER_PROMPT},
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/{mime};base64,{img_b64}"}}
                ]
            }
        ],
        temperature=0,
        seed=64,
        max_tokens=1024
    )

    # Detener cronómetro
    duration = time.time() - start

    content = response.choices[0].message.content
    index = extract_predicted_index(content)

    # Tokens usados
    usage = response.usage
    prompt_tokens = usage.prompt_tokens
    completion_tokens = usage.completion_tokens
    total_tokens = usage.total_tokens

    print(f"Predicción completada.")
    print(f"Ki-67 Index: {index:.2f}%")
    print(f"Tiempo de ejecución: {duration:.2f} segundos")
    print(f"Tokens usados: prompt={prompt_tokens}, completion={completion_tokens}, total={total_tokens}\n")

    return index, content

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print(
            "Usage:\n"
            "  python 3.vlm_processing/2.ki67_single_image.py <image_path>\n"
            "Example:\n"
            "  python 3.vlm_processing/2.ki67_single_image.py "
            "1.data_access/data_sample/3.data_processed/8.jpg"
        )
        sys.exit(1)

    image_path = sys.argv[1]
    predict_with_timing(image_path)
