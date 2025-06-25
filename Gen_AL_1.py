import google.generativeai as genai
import json
import pandas as pd
from PIL import Image
import io
import re
import os


def flatten_json(nested_json, parent_key="", sep="_"):
    """Recursively flattens nested JSON into a flat dictionary."""
    flattened_dict = {}

    def _flatten(obj, key):
        if isinstance(obj, dict):
            for k, v in obj.items():
                _flatten(v, f"{key}{sep}{k}" if key else k)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                _flatten(v, f"{key}{sep}{i}")
        else:
            flattened_dict[key] = obj

    _flatten(nested_json, parent_key)
    return flattened_dict


def extract_data_from_image(image_path, api_key, output_excel):
    """Extracts structured data from an image using Gemini API and stores it in an Excel file."""
    genai.configure(api_key=api_key)

    # Load image
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
    image = Image.open(io.BytesIO(image_data))

    # Define prompt
    system_prompt = """
    You specialize in understanding any photo, extracting data, arranging it, and giving them specific labels if labels are not present.
    """
    user_prompt = """
    Extract the data and arrange it in a structured manner and give output in a JSON format.
    """

    # Call the API
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([system_prompt, user_prompt, image])

    # Extract text and clean JSON formatting
    structured_data = response.text.strip()
    structured_data = re.sub(r'```json|```', '', structured_data).strip()

    # Convert to JSON
    try:
        json_data = json.loads(structured_data)
    except json.JSONDecodeError:
        json_data = {}

    # Debugging: Print JSON response
    print("Extracted JSON Data:", json.dumps(json_data, indent=4))

    # Flatten JSON data
    flattened_data = [flatten_json(json_data)] if isinstance(json_data, dict) else []

    # Convert to DataFrame and save to Excel
    if flattened_data:
        df = pd.DataFrame(flattened_data)

        # Debugging: Check DataFrame
        print("DataFrame Preview:", df.head())

        try:
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            print(f"✅ Data successfully saved to {output_excel}")
        except Exception as e:
            print(f"❌ Error while saving Excel file: {e}")

        # Check if file was created
        if os.path.exists(output_excel):
            print(f"✅ Excel file '{output_excel}' has been created successfully!")
        else:
            print(f"❌ Excel file '{output_excel}' was NOT created. Check write permissions or file path.")
    else:
        print("No valid data to save.")

    return json_data


if __name__ == "__main__":
    api_key = "AIzaSyCCMYyicdsYdfQGRjDr3HAs0ncPFcIdIpE"
    image_path = "C:\\Users\\rohan\\Downloads\\WhatsApp Image 2025-02-20 at 12.52.22_c5a99f58.jpg"
    output_excel = "extracted_data.xlsx"
    extracted_data = extract_data_from_image(image_path,api_key, output_excel)


    # Print structured JSON output
    print(json.dumps(extracted_data, indent=4))
