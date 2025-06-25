import google.generativeai as genai
from PIL import Image
import json
import pandas as pd
from pdf2image import convert_from_path  # Converts PDF to images
import time
import atexit
import gc
import os
import sys  # To force exit and prevent GRPC shutdown error
from api_maneger import Drowing_Prompts

# Set Gemini API Key
genai.configure(api_key="AIzaSyAlRgR9ATHo1HJM1an0RREbO8FHYbNXpG0")

# Strict Engineering Drawing Prompt
PROMPT = Drowing_Prompts

# Function to process an engineering drawing image
def classify_image_with_gemini(image_path, retries=3):
    model = genai.GenerativeModel("gemini-1.5-pro", generation_config={
        "temperature": 0.2,
        "max_output_tokens": 8192
    })

    for attempt in range(retries):
        try:
            with Image.open(image_path) as img:
                response = model.generate_content([img, PROMPT])

            # Extract JSON content correctly
            full_response = response.candidates[0].content.parts[0].text.strip()

            # Remove markdown block (```json ... ```)
            if full_response.startswith("```json"):
                full_response = full_response[7:-3]  # Remove first 7 and last 3 characters

            print("🔍 Processed JSON String:\n", full_response)

            return fix_incomplete_json(full_response)

        except AttributeError as e:
            print(f"❌ ERROR: API Response Structure Changed: {e}")
            print("Full API Response:", response)
            return "{}"
        except Exception as e:
            print(f"⚠️ API call failed (Attempt {attempt + 1}/{retries}): {e}")
            time.sleep(10)

    print("❌ ERROR: Gemini API failed after multiple attempts.")
    return "{}"

# Function to fix incomplete JSON responses
def fix_incomplete_json(json_string):
    try:
        return json.loads(json_string)  # If JSON is valid, return it
    except json.JSONDecodeError:
        print("⚠️ Detected incomplete JSON. Attempting repair...")
        try:
            json_string = json_string.rstrip(",")  # Remove trailing commas
            json_string += "}" if not json_string.endswith("}") else ""  # Try closing JSON
            return json.loads(json_string)
        except json.JSONDecodeError:
            print("❌ ERROR: JSON Repair Failed.")
            return None  # Return None if still broken

# Function to process an engineering drawing (PDF or Image)
def process_engineering_drawing(input_path):
    if input_path.lower().endswith(".pdf"):
        images = convert_from_path(input_path)
        image_path = "converted_page_1.png"
        images[0].save(image_path, "PNG")
    else:
        image_path = input_path

    structured_data = classify_image_with_gemini(image_path, retries=2)

    if structured_data:
        generate_inspection_checklist(structured_data)

# Function to generate an inspection checklist
def generate_inspection_checklist(structured_data, output_path="Eng//RDH4250019 Proximity Sensor Flange.xlsx"):
    try:
        df = pd.DataFrame(structured_data.get("Views & Dimensions", []))
        df.to_excel(output_path, index=False)
        print(f"✅ Inspection checklist saved as {output_path}")
    except Exception as e:
        print("❌ ERROR: Failed to generate checklist:", e)

# Ensuring API Shutdown to Prevent GRPC Timeout
def shutdown_api():
    try:
        print("🔄 Cleaning up resources...")
        gc.collect()  # Force garbage collection to release memory
        print("✅ API resources cleaned up successfully.")

        # **Force exit to prevent GRPC timeout**
        print("🔴 Forcing process exit to prevent GRPC timeout...")
        sys.exit(0)  # Ensure no hanging GRPC threads
    except Exception as e:
        print(f"⚠️ Failed to clean up API resources: {e}")

# Register cleanup function
atexit.register(shutdown_api)

# Run with PDF or Image
input_path = "D:\\PycharmProjects\\ONYX_Gen-AI\\Eng\\31.5.2025\\M-25-011384.pdf"
process_engineering_drawing(input_path)
