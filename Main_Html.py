from flask import Flask, request, jsonify, render_template, send_file
import os
import json
import google.generativeai as genai
import pandas as pd
from werkzeug.utils import secure_filename
from api_maneger import api_manager  # Custom API manager for Gemini key management

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure Google Gemini API
genai.configure(api_key=api_manager.get_random_api())  # Fetch API key from manager

# Configuration for Gemini model
MODEL_CONFIG = {
    "temperature": 0.2,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4906,
}

# Initialize Gemini model
model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=MODEL_CONFIG)

# Function to format image for Gemini input
def image_format(image_path):
    with open(image_path, "rb") as img_file:
        return [{"mime_type": "image/jpeg", "data": img_file.read()}]

# Function to extract structured data using Gemini
def extract_table_from_image(image_path):
    system_prompt = "Extract structured table data from the image and return as JSON. Include headers and values."
    user_prompt = "Extract the table with columns: Sr.No., Description, Process, Color, Qty/Assem, etc. Return JSON format."

    image_info = image_format(image_path)
    input_prompt = [system_prompt, image_info[0], user_prompt]

    try:
        response = model.generate_content(input_prompt)
        raw_output = response.text.strip()
        if raw_output.startswith("```json"):
            raw_output = raw_output[8:-3].strip()
        return raw_output
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return "{}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    extracted_json = extract_table_from_image(file_path)

    try:
        json_data = json.loads(extracted_json)
        df = pd.DataFrame(json_data)
        excel_path = os.path.join(app.config['UPLOAD_FOLDER'], "Extracted_Data.xlsx")
        df.to_excel(excel_path, index=False)
        return jsonify({'message': 'Data extracted and saved successfully', 'file_path': excel_path, 'extracted_json': extracted_json})
    except json.JSONDecodeError as e:
        return jsonify({'error': f'Failed to parse JSON: {e}'})

@app.route('/download')
def download_file():
    excel_path = os.path.join(app.config['UPLOAD_FOLDER'], "Extracted_Data.xlsx")
    return send_file(excel_path, as_attachment=True)

if __name__ == '__main__':
    app.run(Debug=True)
    # app.run(host="0.0.0.0", port=5000, debug=True)