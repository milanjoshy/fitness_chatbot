# rag_engine.py

import os
import fitz  # PyMuPDF for PDF
import pandas as pd  # for Excel
import docx  # for Word
import sqlite3
import numpy as np
import faiss
from datetime import datetime
from sentence_transformers import SentenceTransformer
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or "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"
MODEL = "llama-3.3-70b-versatile"
client = Groq(api_key=GROQ_API_KEY)

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_pdf(file_path):
    text = ""
    doc = fitz.open(file_path)
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_excel(file_path):
    text = ""
    xls = pd.ExcelFile(file_path)
    for sheet_name in xls.sheet_names:
        df = xls.parse(sheet_name)
        text += df.astype(str).to_string(index=False)
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def load_knowledge_base():
    docs = []

    if os.path.exists("knowledge_base/fitness_data.txt"):
        with open("knowledge_base/fitness_data.txt", "r", encoding="utf-8") as f:
            docs += f.readlines()

    uploads_folder = "knowledge_base/uploads"
    if os.path.exists(uploads_folder):
        for file in os.listdir(uploads_folder):
            file_path = os.path.join(uploads_folder, file)
            try:
                if file.endswith(".pdf"):
                    docs.append(extract_text_from_pdf(file_path))
                elif file.endswith(".xlsx"):
                    docs.append(extract_text_from_excel(file_path))
                elif file.endswith(".docx"):
                    docs.append(extract_text_from_docx(file_path))
            except Exception as e:
                print(f"Error processing {file}: {e}")

    embeddings = embedding_model.encode(docs)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    return docs, index, embeddings

def save_chat_history(user_email, user_msg, bot_msg):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            user_msg TEXT,
            bot_msg TEXT,
            timestamp TEXT
        )
    """)
    cursor.execute("INSERT INTO history (email, user_msg, bot_msg, timestamp) VALUES (?, ?, ?, ?)",
                   (user_email, user_msg, bot_msg, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_chat_history(user_email):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_msg, bot_msg, timestamp FROM history WHERE email = ? ORDER BY id DESC LIMIT 10", (user_email,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_response(query, profile):
    docs, index, _ = load_knowledge_base()
    query_embed = embedding_model.encode([query])
    D, I = index.search(np.array(query_embed), k=3)

    retrieved_chunks = "\n".join([docs[i] for i in I[0]])

    user_context = f"""
    User Profile:
    Name: {profile.get("name")}
    Age: {profile.get("age")}
    Gender: {profile.get("gender")}
    Weight: {profile.get("weight")}
    Height: {profile.get("height")}
    Goal: {profile.get("goal")}
    Experience: {profile.get("experience")}
    Diet: {profile.get("diet")}
    """

    system_prompt = """
    You are FitBot, a helpful and expert fitness assistant.
    You provide personalized advice based on the user's profile and relevant documents.
    Always sound friendly and motivational.
    """

    user_prompt = f"""
    {user_context}

    Based on the retrieved information:
    {retrieved_chunks}

    User Question: {query}
    """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()}
        ]
    )

    answer = response.choices[0].message.content
    save_chat_history(profile.get("email"), query, answer)
    return answer
