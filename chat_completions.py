import os
from typing import Tuple, List, Optional
import base64
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI
from utils import convert_and_resize_image

load_dotenv(override=True)


google_api_key = os.getenv('GOOGLE_API_KEY')
openai_api_key = os.getenv("OPENAI_API_KEY")



def recognize_text_from_single_image(image, client, model_used) -> str:
    """Extract text from a single uploaded image using Gemini vision model."""
    if image is None:
        return ""
    
    try:
        # Load and convert image - handle both file path and PIL Image
        if isinstance(image, str):
            # Convert and resize image
            img = convert_and_resize_image(image)
        else:
            img = image
            # If it's already a PIL Image, still convert to RGB and resize
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        
        # Convert PIL Image to base64 as PNG
        buffered = BytesIO()
        img.save(buffered, format="PNG", quality=85)
        img_base64 = base64.standard_b64encode(buffered.getvalue()).decode("utf-8")
        
        prompt = "Please recognize all text in this image, maintaining the original format and line breaks. Only output the recognized text content, do not add any explanations."
        
        # Create message with image in the correct format for Gemini OpenAI compatibility
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_base64}"
                        }
                    }
                ]
            }
        ]
        
        # Use the client to send the image along with the prompt to the model for text recognition

        response = client.chat.completions.create(
            model=model_used,
            messages=messages
        )
        recognized_text = response.choices[0].message.content
        return recognized_text if recognized_text else ""
    
    except Exception as e:
        return f"[Error recognizing text from image: {str(e)}]"


def recognize_text_from_images(images: Optional[List], client: OpenAI, model_used: str) -> str:
    """Extract text from multiple images in order."""
    if not images or len(images) == 0:
        return "Please upload at least one image"
    
    try:
        all_texts = []
        # Handle case where Gallery returns list of dicts with 'name' key or list of file paths
        image_list = []
        for img in images:
            if isinstance(img, dict):
                # Gallery might return dict with 'name' or 'path' key
                img_path = img.get('name') or img.get('path') or img
            else:
                img_path = img
            if img_path:
                image_list.append(img_path)
        
        if not image_list:
            return "Please upload at least one image"
        
        for idx, image in enumerate(image_list, 1):
            if image is None:
                continue

            text = recognize_text_from_single_image(image, client, model_used)
            if text and "[Error" not in text:
                all_texts.append(text)
        
        if not all_texts:
            return "Failed to recognize text from any images"
        
        # Combine all recognized texts with a separator
        combined_text = "\n\n--- Page Break ---\n\n".join(all_texts)
        return combined_text
    
    except Exception as e:
        return f"Error recognizing text: {str(e)}"


def analyze_essay(essay_text: str, client: OpenAI, model_used: str, temp: float) -> str:
    """Analyze the essay using OpenAI client pattern to call Gemini API."""
    if not essay_text or essay_text.strip() == "":
        return "Please upload an image and recognize text first"
    
    try:
        
        # System and user messages (similar to OpenAI client messages pattern)
        system_prompt = "You are an experienced primary school German teacher, skilled at reviewing and guiding primary school students to write German essays for the lang-gymnasium entrance exam."
        
        user_prompt = f"""Please analyze this primary school student's essay and provide structured feedback. Please output in the following format:

## 1. Word Errors
(List all misspellings and inappropriate word usage, and provide the correct spelling/wording)

## 2. Grammar Errors
(List all grammar errors and explain how to correct them)

## 3. Expression Optimization Suggestions
(Provide specific optimization suggestions suitable for primary school students' expression level, making the expression more vivid, accurate, and appropriate for primary school language characteristics)

## 4. Overall Evaluation
(Briefly evaluate the overall quality of the essay)

Please ensure the feedback is clear, specific, and suitable for primary school students to understand.

Essay Content:
{essay_text}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        response = client.chat.completions.create(
            model=model_used,
            messages=messages,
            max_completion_tokens=2000,
            temperature=temp,
        )
        
        analysis_result = response.choices[0].message.content
        return analysis_result if analysis_result else "Analysis failed, please try again"
    
    except Exception as e:
        return f"Error analyzing essay: {str(e)}"


def process_essay(images: Optional[List], model: str) -> Tuple[str, str]:
    """Process the uploaded images: recognize text from all images in order and analyze essay."""
    if model.startswith("gemini"):
        GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
        client = OpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key)
        temp = 0.7
    elif model.startswith("gpt"):
        client = OpenAI()
        temp = 1
    else:
        return "Unsupported model selected", "Please select a supported model"
    model_used = model

    # Step 1: Recognize text from all images in order
    recognized_text = recognize_text_from_images(images, client, model_used)
    
    # Step 2: Analyze the essay if text was recognized
    if recognized_text and recognized_text != "Please upload at least one image" and "Failed to recognize" not in recognized_text and "[Error" not in recognized_text:
        analysis = analyze_essay(recognized_text, client, model_used, temp)
    else:
        analysis = "Please successfully recognize text from images before analysis"
    
    return recognized_text, analysis