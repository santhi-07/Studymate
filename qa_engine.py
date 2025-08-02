from sentence_transformers import SentenceTransformer, util

# Load model once
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def ask_question(question, pdf_text):
    """
    Takes a question and PDF text, finds the best matching sentence.
    Returns the best matching sentence (answer) and its index.
    """
    if not pdf_text.strip():
        return None, None

    # Split the PDF into small sentences
    sentences = [line.strip() for line in pdf_text.split('.') if line.strip()]

    # Convert to embeddings
    question_embedding = model.encode(question, convert_to_tensor=True)
    sentence_embeddings = model.encode(sentences, convert_to_tensor=True)

    # Compute similarity
    scores = util.cos_sim(question_embedding, sentence_embeddings)[0]

    # Find the best score
    best_score_idx = scores.argmax().item()
    best_answer = sentences[best_score_idx]

    return best_answer, best_score_idx
