import os
from groq import Groq

# Model to use — llama-3.3-70b is free and very capable
MODEL = "llama-3.3-70b-versatile"

# Max chars of document context to send (keeps tokens under limit)
MAX_CONTEXT_CHARS = 12000


def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set. Get a free key at https://console.groq.com")
    return Groq(api_key=api_key)


def answer_questions(document_text: str, user_question: str, chat_history: list[dict]) -> str:
    """
    Chat with the document. Supports:
    - "What is this document about?" → summary
    - "Answer all questions in this paper" → full Q&A
    - Any custom question about the document
    """
    client = get_groq_client()

    # Trim document context if too long
    context = document_text[:MAX_CONTEXT_CHARS]
    if len(document_text) > MAX_CONTEXT_CHARS:
        context += "\n\n[Document truncated for length...]"

    system_prompt = f"""You are an expert academic assistant. You have been given a document (question paper, notes, or text).

Your jobs:
1. If the user asks to answer questions from the document — identify every question in the document and provide clear, accurate answers.
2. If the user asks what the document is about — give a concise summary: topic, subject, difficulty level, number of questions.
3. For any other question — answer it strictly based on the document content.

Always be clear, structured, and student-friendly. Use numbered lists for multiple answers.

--- DOCUMENT CONTENT START ---
{context}
--- DOCUMENT CONTENT END ---
"""

    messages = [{"role": "system", "content": system_prompt}]

    # Include chat history for multi-turn conversation
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    # Add the latest user message
    messages.append({"role": "user", "content": user_question})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=4096,
    )

    return response.choices[0].message.content


def summarize_document(document_text: str) -> str:
    """Quick summary of the uploaded document."""
    client = get_groq_client()
    context = document_text[:MAX_CONTEXT_CHARS]

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an academic assistant. Summarize the given document briefly: what subject it covers, type of document (question paper / notes / text), estimated difficulty, and number of questions if any.",
            },
            {"role": "user", "content": f"Summarize this document:\n\n{context}"},
        ],
        temperature=0.2,
        max_tokens=512,
    )

    return response.choices[0].message.content
