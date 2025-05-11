
import os, re, io
import json
import random
import requests
import time
import replicate

from PIL import Image

import base64
from io import BytesIO


class HuggingFaceInference:
    def __init__(self, prompts):
        self.IMG_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
        self.TEXT_API_URL = "https://api-inference.huggingface.co/models/microsoft/Phi-3.5-mini-instruct"
        self.headers = {"Authorization": "Bearer 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"}
        self.replicate_key = "<Replicate_API_KEY>" # not in use, to use: you can replace _get_image_from_huggingface with _get_image_from_replicate_url
        os.environ["REPLICATE_API_TOKEN"] = self.replicate_key # this is for replicate library
        self.images_path = "images"
        self.prompts = prompts
        if not os.path.exists(self.images_path):
            os.makedirs(self.images_path)
    
    # get image from huggingface api
    def _get_image_from_huggingface(self, payload):
        response = requests.post(self.IMG_API_URL, headers=self.headers, json=payload,timeout=600)
        return response.content

    # get image from replicate api
    def _get_image_from_replicate(self, payload):
        payload = { 
            "input":{
            "seed": payload["parameters"]["seed"],
            "prompt": payload["inputs"],
            "go_fast": True,
            "guidance": 3.5,
            "megapixels": "1",
            "num_outputs": 1,
            "aspect_ratio": "9:16",
            "output_format": "png",
            "output_quality": 80,
            "prompt_strength": 0.8,
            "num_inference_steps": 28,
            "disable_safety_checker": True
            }
        }
        try: 
            time.sleep(3) 
            output = replicate.run(
                    "black-forest-labs/flux-dev",
                    input=payload["input"]
            )

            if len(output) == 0:
                return None
            time.sleep(5)
            img_response = requests.get(output[0])
            return img_response.content
        except Exception as e:
            print("Failed to get image:", e)
            return None

    def _get_bytes_from_base64(self, base64_data: str):
        if base64_data.startswith('data:'):
            base64_data = base64_data.split(',')[1]
        
        webp_data = base64.b64decode(base64_data) 
        # image = Image.open(BytesIO(webp_data)) # Open the webp image from memory
        # image = image.convert("RGBA") # Convert to RGBA for PNG format 
        return webp_data 

    def _get_image_from_replicate_url(self, payload):
        try:
            time.sleep(3) 
            response = requests.post(
                "https://api.replicate.com/v1/models/black-forest-labs/flux-dev/predictions",
                headers={
                "Authorization": f"Bearer {self.replicate_key}",
                "Content-Type": "application/json",
                "Prefer": "wait"
            },
            json={
                "input": {
                    "seed": payload["parameters"]["seed"],
                    "prompt": payload["inputs"],
                    "go_fast": True,
                    "guidance": 3.5,
                    "megapixels": "1",
                    "num_outputs": 1,
                    "aspect_ratio": "9:16",
                    "output_format": "webp",
                    "output_quality": 80,
                    "prompt_strength": 0.8,
                    "num_inference_steps": 28,
                    "disable_safety_checker": True
                    }
                }
            )
            time.sleep(5)
            response_json = response.json()
            output = response_json['output'][0]
            img_bytes = self._get_bytes_from_base64(output) 
            return img_bytes 
        except Exception as e:
            print(e)
            return None

    def _get_text(self, payload):
        response = requests.post(self.TEXT_API_URL, headers=self.headers, json=payload)
        return response.json()
 
    def _extract_json(self, response):
        try:
            pattern = r'(?:(?<=^)|(?<=\s))["\'`]{3}(?:json\s*|\s*)(.*?)["\'`]{3}(?=(?:\s|$))'

            match = re.search(pattern, response, re.DOTALL) 
            if match:
                json_str = match.group(1).strip() 
                data = json.loads(json_str) 
                return data
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", e)
        
        return None
 
    def get_json_response(self, request_text):
        seed = random.randint(0, 1000000)
        payload = {
            "inputs": f"<|user|>\n{request_text}<|end|>\n<|assistant|>\n",
            "parameters": {
            "max_new_tokens": 1024,
            "return_full_text": False,
            "temperature": 0.8,
            "seed": seed
            } 
        } 
        
        response = self._get_text(payload)
        generated_text = response[0]['generated_text'] 
        response_json = self._extract_json(generated_text) 

        return response_json
    
    def get_and_save_image(self, image_desc, file_path, seed=None):
        if seed is None:
            seed = random.randint(0, 1000000)
        print(f"Generating image `{image_desc}` ...")
        image_bytes = self._get_image_from_huggingface({
            "inputs": image_desc,
            "parameters": {
            "width": 1080, 
            "height": 1920, 
            "seed": seed
            } 
        }) 
        if len(image_bytes) < 100:
            print("Failed to generate image.")
            print("--"*10)
            print(image_bytes)
            print("--"*10)
            return 
        image = Image.open(io.BytesIO(image_bytes))
        image.save(file_path)
        print(f"Image saved at: {file_path}") 