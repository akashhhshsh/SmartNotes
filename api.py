from flask import Flask, request, jsonify
import pdfplumber
from answer_generation_logic import generate_answers_from_notes

app = Flask(__name__)

# Global variables to store uploaded texts
notes_text = ""
question_bank_text = ""

# Endpoint to upload lecture notes
@app.route('/upload/notes', methods=['POST'])
def upload_notes():
    global notes_text
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Extract text from the PDF
    try:
        notes_text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                notes_text += page.extract_text() + "\n"
        return jsonify({"message": "Notes uploaded successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to upload question bank
@app.route('/upload/question-bank', methods=['POST'])
def upload_question_bank():
    global question_bank_text
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Extract text from the PDF
    try:
        question_bank_text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                question_bank_text += page.extract_text() + "\n"
        return jsonify({"message": "Question bank uploaded successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to generate answers
@app.route('/generate/answers', methods=['GET'])
def generate_answers():
    global notes_text, question_bank_text

    # Check if both texts are available
    if not notes_text or not question_bank_text:
        return jsonify({"error": "Both notes and question bank must be uploaded before generating answers."}), 400

    # Generate answers
    try:
        answers = generate_answers_from_notes(notes_text, question_bank_text)
        return jsonify({"message": "Answers generated successfully.", "answers": answers}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
