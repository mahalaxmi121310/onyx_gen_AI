import json

from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename

from Invoice.invoice_main import po_pdf_to_image, po_gemini_output, trim_and_convert
from KYC_doc.kyc_main import process_file
from api_maneger import system_prompt_Adhar, system_prompt_pan, user_prompt_pan, user_prompt_Adhar
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# File Upload & Processing for PAN Card
@app.route('/upload_pan', methods=['POST'])
def upload_pan():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    extracted_data = process_file(filepath, system_prompt_pan, user_prompt_pan)
    if extracted_data and extracted_data.get("documentType") == "PAN Card":
        return jsonify({'message': 'PAN Card processed successfully', 'data': extracted_data}), 200
    return jsonify({'error': 'Invalid PAN Card data'}), 400

# File Upload & Processing for Aadhar Card
@app.route('/upload_aadhar', methods=['POST'])
def upload_aadhar():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    extracted_data = process_file(filepath, system_prompt_Adhar, user_prompt_Adhar)
    if extracted_data and extracted_data.get("documentType") == "Aadhar Card":
        return jsonify({'message': 'Aadhar Card processed successfully', 'data': extracted_data}), 200
    return jsonify({'error': 'Invalid Aadhar Card data'}), 400


@app.route('/invoice', methods=['POST'])
def upload_invoice():
    app.logger.info('Invoice upload API accessed.')
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400

    filename = secure_filename(file.filename)
    pdf_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
    file.save(pdf_path)
    app.logger.info(f'Invoice PDF saved: {filename}')
    image_paths = po_pdf_to_image(pdf_path)
    output_json = po_gemini_output(image_paths[0])

    json_data = json.loads(output_json)
    return json_data

    # try:
    #     image_paths = po_pdf_to_image(pdf_path)
    #     output_json = po_gemini_output(image_paths[0])
    #
    #     json_data = json.loads(output_json)
    #     po_number = trim_and_convert(json_data.get('poNumber', ''))
    #     db_data = fetch_po_details(po_number)
    #     comparison_results, product_comparisons = compare_data(json_data, db_data)
    #
    #     return jsonify({
    #         'comparison_results': comparison_results,
    #         'product_comparisons': product_comparisons
    #     }), 200
    # except Exception as e:
    #     app.logger.error(f"Error processing invoice: {e}")
    #     return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

