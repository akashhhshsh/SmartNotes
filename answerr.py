from transformers import pipeline
from sentence_transformers import SentenceTransformer, util

# Load models
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")
sentence_model = SentenceTransformer("all-MiniLM-L6-v2")  # Efficient sentence embeddings

def generate_detailed_answers_from_notes(lecture_notes_text, question_bank_content):
    detailed_answers = []
    questions = question_bank_content.split('\n')  # Split question bank into individual questions
    lecture_notes_paragraphs = lecture_notes_text.split("\n\n")  # Split notes into paragraphs

    # Precompute embeddings for lecture notes paragraphs
    note_embeddings = sentence_model.encode(lecture_notes_paragraphs, convert_to_tensor=True)

    for question in questions:
        if question.strip() == "":
            continue

        try:
            # Compute similarity scores for the question against all paragraphs
            question_embedding = sentence_model.encode(question, convert_to_tensor=True)
            similarities = util.pytorch_cos_sim(question_embedding, note_embeddings)

            # Adjust k to the number of available paragraphs
            available_paragraphs = len(lecture_notes_paragraphs)
            top_k = min(3, available_paragraphs)  # Use at most 3 paragraphs or fewer if notes are short

            top_k_indices = similarities.topk(k=top_k).indices  # Get the top-k most relevant paragraphs

            # Combine the most relevant paragraphs for context
            relevant_context = " ".join([lecture_notes_paragraphs[i] for i in top_k_indices])

            # Generate an answer using the QA model
            qa_result = qa_pipeline(
                question=question,
                context=relevant_context,
                max_answer_len=300,  # Allow longer answers
                handle_impossible_answer=False
            )
            detailed_answers.append({
                "query": question,
                "response": qa_result.get("answer", "No answer found.")
            })
        except Exception as e:
            detailed_answers.append({
                "query": question,
                "response": f"Error generating answer: {str(e)}"
            })

    return detailed_answers
