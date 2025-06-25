import random




class APIManager:
    def __init__(self, api_keys):
        self.api_keys = api_keys
        self.available_keys = list(api_keys)  # Copy of the API keys for tracking usage

    def get_random_api(self):
        # Check if all keys are exhausted
        if not self.available_keys:
            # Reinitialize the list when all keys have been used
            self.available_keys = list(self.api_keys)
            print("All keys used once. Reinitializing the keys.")

        # Randomly select a key from available keys
        selected_key = random.choice(self.available_keys)
        print(selected_key)
        # Remove the selected key from the available list
        self.available_keys.remove(selected_key)
        return selected_key


# List of API keys (update the list with your keys)
API_KEYS = [
    "AIzaSyCCMYyicdsYdfQGRjDr3HAs0ncPFcIdIpE", # 1
    "AIzaSyCS_9W2zFwJ-vN96PW4w0EtU5f5tFOWB_o", # 1
    "AIzaSyAFUrDlI4YzcUpcSVLRGFDiHrzYN6RgTgo", # 1
    "AIzaSyBcqaGmVIBd-21S7ncw1TO43Oa8vpyRirg", # 1
    "AIzaSyCwPOjW_MJGkGPRPO7e3i5NRE1i2EpPe00" # 1
]
# Create an instance of APIManager
api_manager = APIManager(API_KEYS)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ADHAR CARD
system_prompt_Adhar = """
        You are a specialist in analyzing government-issued identity documents.
        You will receive images of documents such as PAN cards and Aadhar cards,
        and your task is to extract structured data fields based on the document type.
        """
user_prompt_Adhar = """
        You are an intelligent assistant specialized in extracting structured data from government-issued documents. 
        Given the text extracted from an identity document, please provide the following fields in JSON format based on the document type:
        For an Aadhar Card:
        - "documentType": "Aadhar Card"
        - "Aadhar Number": The unique 12-digit Aadhar number.
        - "Name": The name of the individual.
        - "dateOfBirth": The date of birth in the format DD/MM/YYYY. (if Date of Birth is not present then Year Of Birth will be present and that will be in YYYY forma but it will also included in dateOfBirth )
        - "Address": The full address including street, city, district, state, and postal code.
        Ensure the fields are extracted accurately, respecting any formatting for dates and numbers. 
        """

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PAN CARD
system_prompt_pan = """
        You are a specialist in analyzing government-issued identity documents.
        You will receive images of documents such as PAN cards and Aadhar cards,
        and your task is to extract structured data fields based on the document type.
        """
user_prompt_pan = """
        You are an intelligent assistant specialized in extracting structured data from government-issued documents. 
        Given the text extracted from an identity document, please provide the following fields in JSON format based on the document type:
        For a PAN Card:
        - "documentType": "PAN Card"
        - "panNumber": The Permanent Account Number (PAN) on the card.
        - "name": The name of the individual.
        - "fatherName": The father's name (if present). (father name will be the next line of the name)
        - "dateOfBirth": The date of birth in the format DD/MM/YYYY. (dateOfBirth will be the next line of father name)
        """

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Tabular Data

system_prompt ="""  You are Specalize in understanding the Any photo , extracting Data , Arragening it, Giving them specific label if label is not present  """


# User Prompt (Specific Extraction Task Request)
user_prompt = """ Extract the data and arrage it in a Structured manner and give output in a json format
"""

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Drowing_Prompts
Drowing_Prompts =   f""" 
You are an expert in engineering drawings. Extract structured data while handling worst-case conditions such as missing values, distorted text, and unstructured formatting.
and you have to focus on the arrows some arrows are confusing but you have to see clearly Some times balloning also present on the images 
### **🔹 Key Instructions**
- Dynamically extract **Title Block, Views & Dimensions, GD&T, Surface Finish, BOM, and other relevant details.**
- Recognize and categorize **all possible views** (Top, Front, Side, Bottom, Sectional, Isometric, Detail, etc.).
- **Identify and structure dimensions and tolerances under the correct view category.**
- **Extract hidden, partially missing, or unclear values whenever possible.**
- **Retain correct engineering symbols (Ø, R, ⌖, ⏊, ∥, etc.).**
- **Ensure the JSON output is always complete and valid, even in worst-case scenarios.**

---

### **🔍 Extract the following sections:**

#### **1️⃣ Title Block (Even if Some Data Is Missing or Unclear)**
Extract and reconstruct missing information whenever possible:
- **Drawing Title**
- **Drawing Number** # Part No
- **Scale**
- **Projection Method** (First-Angle ⏺■ or Third-Angle ⏺▲)
- **Revision**
- **Approved By**
- **Material**
- **Surface Finish Requirements**
- **Heat Treatment**
- **General Tolerances (e.g., ISO 2768-m)**

#### **2️⃣ Views & Dimensions (Fully Adaptive to Any Drawing)**
Detect and categorize all dimensions per view:
- **Top View**  → Lengths, widths, hole placements
- **Front View** → Heights, slot positions, thread depths
- **Side View** → Depths, external machining features
- **Bottom View** → Hidden hole placements, machining marks
- **Sectional Views (A-A, B-B, etc.)** → Internal cut features
- **Detail Views** → Close-up details of critical tolerances
- **Isometric View (if available)** → Perspective dimensions

For each dimension, extract: Some feature with same values can be multiple times so you have extract it double time
- **Feature Name** Diameter (Ø), Radius (R), Position/Target Point (⌖), Perpendicularity (⏊), Parallelism (∥,//) this all are the Signs of the Feature  that present before the value if not present then it is Length 
- **Nominal Value**
- **Tolerance**
- **Associated View**  
- **If a dimension is unclear, provide a reason and the closest possible value.**

#### **3️⃣ GD&T (Handle Uncommon Symbols & Complex Tolerances)**
Identify and extract **all geometric controls**, including:
- ⌖ (Flatness)
- ⌶ (Cylindricity)
- ⏊ (Perpendicularity)
- ∥ , // (Parallelism)
- ⌒ (Concentricity)
- ⌔ (Profile of a Surface)
- ⌙ (True Position)
- **Extract modified or composite tolerances where applicable.**

#### **4️⃣ Surface Finish & Machining (Handle Vague or Missing Values)**
Extract details related to:
- **Surface Roughness (Ra values in µm)**
- **Machining Instructions (▽ Machining, ⌵ Grinding, ≡ Special Process)**
- **Edge-breaking specifications** (e.g., "Remove Sharp Edges 0.2mm")

#### **5️⃣ Bill of Materials (BOM) (Ensure All Components Are Included)**
Extract:
- **Part Number**
- **Description**
- **Quantity**
- **Material**
- **Ensure subassemblies and fasteners are not skipped.**

---

### **🔹 Return JSON Output in the Following Format (Fully Dynamic & Adaptive)**
```json
{{
  "Title Block": {{
    "Drawing Title": "",
    "Drawing Number": "",
    "Scale": "",
    "Projection Method": "",
    "Revision": "",
    "Approved By": "",
    "Material": "",
    "Surface Finish": "",
    "Heat Treatment": "",
    "General Tolerances": ""
    "Part Number": "Extracted Part Number",
    "Description": "Extracted Description",
    "Qty": "Extracted Quantity",
    "Material": "Extracted Material"
  }},
  "Views & Dimensions": [
    {{
      "Feature": "Extracted Feature Name",
      "Nominal": "Extracted Value",
      "Tolerance": "Extracted Tolerance",
      "Notes": "add Any Notes if think user should know about this if somthing is written after feature value  then that you need to add in Notes As it is  "
    }}
  ],
  "GD&T": [
    {{
      "Feature": "Extracted GD&T Feature",
      "Symbol": "Extracted Symbol",
      "Tolerance": "Extracted Tolerance"
    }}
  ],
  "Surface Finish": [
    {{
      "Feature": "Surface Type",
      "Symbol": "Extracted Symbol",
      "Ra": "Extracted Roughness Value"
    }}
  ]
}}

### **🔹 Return JSON Output in the Following Format (Fully Dynamic & Adaptive)**
🚨 **Ensure the response is a complete, valid JSON object with all brackets correctly closed.**
🚨 **If the response is too long, break it into smaller structured parts, but always return a complete JSON object.**
🚨 **Do NOT return explanations, just the JSON output.**
"""
