import os
from groq import Groq

MODEL = "llama-3.3-70b-versatile"
MAX_CONTEXT_CHARS = 12000

SUPPORTED_LANGUAGES = [
    "English", "Hindi", "Gujarati", "Marathi", "Tamil",
    "Telugu", "Bengali", "French", "Spanish", "German", "Arabic"
]


def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set. Get a free key at https://console.groq.com")
    return Groq(api_key=api_key)


def answer_questions(document_text: str, user_question: str, chat_history: list[dict], language: str = "English") -> str:
    client = get_groq_client()

    context = document_text[:MAX_CONTEXT_CHARS]
    if len(document_text) > MAX_CONTEXT_CHARS:
        context += "\n\n[Document truncated for length...]"

    system_prompt = f"""You are an expert academic assistant. You have been given a document (question paper, notes, or text).

Your jobs:
1. If the user asks to answer questions from the document — identify every question in the document and provide clear, accurate answers.
2. If the user asks what the document is about — give a concise summary: topic, subject, difficulty level, number of questions.
3. For any other question — answer it strictly based on the document content.

🌐 IMPORTANT: You MUST respond entirely in **{language}**. Every single word of your response must be in {language}, including explanations, numbering, and labels.

Always be clear, structured, and student-friendly. Use numbered lists for multiple answers.

--- DOCUMENT CONTENT START ---
{context}
--- DOCUMENT CONTENT END ---
"""

    messages = [{"role": "system", "content": system_prompt}]

    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": user_question})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=4096,
    )

    return response.choices[0].message.content


def summarize_document(document_text: str, language: str = "English") -> str:
    client = get_groq_client()
    context = document_text[:MAX_CONTEXT_CHARS]

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": f"You are an academic assistant. Summarize the given document briefly: what subject it covers, type of document (question paper / notes / text), estimated difficulty, and number of questions if any. You MUST respond entirely in {language}.",
            },
            {"role": "user", "content": f"Summarize this document:\n\n{context}"},
        ],
        temperature=0.2,
        max_tokens=512,
    )

    return response.choices[0].message.content