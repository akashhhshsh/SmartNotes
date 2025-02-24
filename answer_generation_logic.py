# answer_generation_logic.py
import re
from openai import OpenAI

# Initialize the OpenAI client for Mistral
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="nvapi-vAjsaPigf9i0Uwdu_eqBzYacToVfdZCpKh1AhMTSnxIlxXosMVd3saEWj", #Add your own API Key from build.nvidia.com
)


def get_mistral_response(question, context):
    """
    Call Mistral's API to generate an answer based on the question and context.
    """
    prompt = f"Answer the question based on the following context: \n{context}\n\nQuestion: {question}"

    # Requesting completion from Mistral
    completion = client.chat.completions.create(
        model="nv-mistralai/mistral-nemo-12b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
    )

    # Attempt to extract the response properly
    try:
        response_content = completion.choices[0].message.content
        return response_content
    except Exception as e:
        return f"Error extracting response: {str(e)}"



def generate_answers_from_notes(notes_text, question_bank_text):
    """
    Generate answers for each question from the uploaded notes.
    """
    answers = []
    questions = question_bank_text.split('\n')

    for question in questions:
        if question.strip() == "":
            continue
        
        # Extract context from the notes for this question
        context = find_context_in_notes(notes_text, question)

        # Get the answer from Mistral
        answer = get_mistral_response(question, context)

        answers.append({
            "question": question,
            "answer": answer
        })
    
    return answers

def find_context_in_notes(notes_text, question):
    """
    Extract relevant context from the notes for the given question.
    """
    question_keywords = re.findall(r'\w+', question.lower())
    potential_matches = []

    # Loop through the notes and find lines that match any of the question keywords
    for line in notes_text.split("\n"):
        if any(keyword in line.lower() for keyword in question_keywords):
            potential_matches.append(line.strip())

    if not potential_matches:
        return "No relevant information found."

    return " ".join(potential_matches)
