import requests
from PIL import Image
import io
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

HEADERS = {
    "Authorization": f"Bearer {os.getenv('HF_TOKEN')}"
}

def generate_image(user_prompt):

    improved_prompt = f"""
    {user_prompt},
    ultra realistic professional fashion photography,
    full body runway model,
    symmetrical realistic face,
    natural skin texture with pores,
    realistic detailed eyes with reflections,
    detailed eyelashes,
    natural lips,
    realistic hands with correct fingers,
    correct human anatomy,
    sharp focus,
    RAW photo,
    85mm DSLR lens,
    studio lighting,
    high resolution,
    extremely detailed
    """

    negative_prompt = """
    blurry,
    low quality,
    distorted face,
    deformed face,
    cross eyes,
    extra fingers,
    extra arms,
    extra legs,
    bad hands,
    bad anatomy,
    mutated,
    cartoon,
    CGI,
    plastic skin,
    oversmoothed face
    """

    payload = {
        "inputs": improved_prompt,
        "parameters": {
            "negative_prompt": negative_prompt,
            "width": 768,
            "height": 1024,
            "guidance_scale": 8,
            "num_inference_steps": 30
        }
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code != 200:
        raise Exception(f"Error: {response.text}")

    image = Image.open(io.BytesIO(response.content))
    return image

