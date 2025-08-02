import requests
import fitz  # PyMuPDF
import tempfile

# Hugging Face Q&A Function
def ask_question_huggingface(question, context):
    API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
    headers = {"Authorization": f"Bearer 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"}  # Replace this
    payload = {"inputs": {"question": question, "context": context}}

    response = requests.post(API_URL, headers=headers, json=payload)
    result = response.json()

    if isinstance(result, dict) and 'answer' in result:
        return result['answer']
    elif isinstance(result, list) and 'answer' in result[0]:
        return result[0]['answer']
    else:
        return "Sorry, I couldn't find an answer."

# Highlight the answer in PDF
def save_highlighted_pdf(uploaded_file, answer, output_path):
    import tempfile
    import fitz  # PyMuPDF

    if not answer or answer.strip() == "":
        return  # No answer to highlight

    # Reset file pointer to beginning before reading
    uploaded_file.seek(0)

    # Save uploaded PDF to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.write(uploaded_file.read())
    temp_file.close()

    doc = fitz.open(temp_file.name)

    if len(doc) == 0:
        raise ValueError("The uploaded PDF has no pages. Please upload a valid PDF.")

    found = False

    for page in doc:
        text_instances = page.search_for(answer)
        for inst in text_instances:
            highlight = page.add_highlight_annot(inst)
            highlight.update()
            found = True

    if found:
        doc.save(output_path)
    else:
        doc.save(output_path)  # Save original PDF without highlight

    doc.close()
