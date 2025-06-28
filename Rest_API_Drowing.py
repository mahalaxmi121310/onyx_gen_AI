from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import tempfile
import shutil
import os
import json
import time
import uvicorn
from PIL import Image
from pdf2image import convert_from_path
import google.generativeai as genai
from api_maneger import Drowing_Prompts  # Your prompt module

# ----------------- Configuration -----------------
genai.configure(api_key="AIzaSyAZuAsU0IfNMNdTNy3tWnb9TC_7f-MfBQk")
PROMPT = Drowing_Prompts

app = FastAPI()

# ----------------- JSON Fixer -----------------
def fix_incomplete_json(json_string):
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        print("⚠️ Detected incomplete JSON. Attempting repair...")
        try:
            json_string = json_string.rstrip(",")
            json_string += "}" if not json_string.endswith("}") else ""
            return json.loads(json_string)
        except json.JSONDecodeError:
            print("❌ JSON still invalid.")
            return None

# ----------------- Gemini Classifier -----------------
def classify_image_with_gemini(image_path, retries=3):
    model = genai.GenerativeModel("gemini-1.5-pro", generation_config={
        "temperature": 0.2,
        "max_output_tokens": 8192
    })

    for attempt in range(retries):
        try:
            with Image.open(image_path) as img:
                response = model.generate_content([img, PROMPT])

            full_response = response.candidates[0].content.parts[0].text.strip()

            if full_response.startswith("```json"):
                full_response = full_response[7:-3]  # Strip ```json ... ```

            print("🔍 Extracted JSON:\n", full_response)
            return fix_incomplete_json(full_response)

        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            time.sleep(5)

    return None

# ----------------- Upload Endpoint -----------------
@app.post("/process-drawing/")
async def process_drawing(file: UploadFile = File(...)):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ext = file.filename.lower().split('.')[-1]
            temp_path = os.path.join(tmpdir, file.filename)

            with open(temp_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

            if ext == "pdf":
                images = convert_from_path(temp_path)
                image_path = os.path.join(tmpdir, "page_1.png")
                images[0].save(image_path, "PNG")
            else:
                image_path = temp_path

            structured_data = classify_image_with_gemini(image_path)

            if structured_data:
                structured_data["file_name"] = file.filename 
                return JSONResponse(content=structured_data)
            else:
                return JSONResponse(status_code=500, content={"error": "Gemini failed to return valid JSON."})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ----------------- Health Check -----------------
@app.get("/")
def root():
    return {"message": "API is up. Use POST /process-drawing/ with PDF or image file."}

if __name__ == "__main__": 
    uvicorn.run("Rest_API_Drowing:app", host="0.0.0.0", port=8000, reload=False)

