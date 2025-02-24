from flask import Flask, request, jsonify
import pdfplumber

app = Flask(__name__)

# Endpoint to upload lecture notes
@app.route('/upload/notes', methods=['POST'])
def upload_notes():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Extract text from the PDF
    notes_text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            notes_text += page.extract_text() + "\n"

    # Logic to save or process notes_text can be added here
    return jsonify({"message": "Notes uploaded successfully.", "content": notes_text}), 200

# Endpoint to upload question bank
@app.route('/upload/question-bank', methods=['POST'])
def upload_question_bank():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Extract text from the PDF
    question_bank_text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            question_bank_text += page.extract_text() + "\n"

    # Logic to save or process question_bank_text can be added here
    return jsonify({"message": "Question bank uploaded successfully.", "content": question_bank_text}), 200

# Endpoint to generate answers
@app.route('/generate/answers', methods=['GET'])
def generate_answers():
    # Logic to process PDFs and generate answers
    return jsonify({"message": "Answers generated successfully."}), 200

if __name__ == '__main__':
    app.run(debug=True)
