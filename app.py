import streamlit as st
import json
import os
from PyPDF2 import PdfReader
import fitz  # PyMuPDF
from datetime import datetime
from helper import save_highlighted_pdf, ask_question_huggingface

# Load users
if os.path.exists("users.json"):
    with open("users.json", "r") as f:
        users = json.load(f)
else:
    users = {}

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Login/Register
st.title("📘 StudyMate")
menu = st.sidebar.selectbox("Choose Option", ["Login", "Register"])

if menu == "Login":
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

    if login_btn and username and password:
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"✅ Welcome {username}!")
        else:
            st.error("❌ Invalid username or password")

elif menu == "Register":
    st.subheader("📝 Register")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    register_btn = st.button("Register")

    if register_btn and new_username and new_password:
        if new_username in users:
            st.warning("⚠️ Username already exists!")
        else:
            users[new_username] = {"password": new_password}
            with open("users.json", "w") as f:
                json.dump(users, f)
            st.success("✅ Registered successfully! You can now log in.")

# Main App
if st.session_state.logged_in:
    st.header("📄 Ask Questions from Your PDF")
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

    if uploaded_file:
        subject = st.text_input("Enter Subject")
        question = st.text_input("Ask a Question")
        ask_btn = st.button("Ask")

        pdf_reader = PdfReader(uploaded_file)
        all_text = ""
        for page in pdf_reader.pages:
            all_text += page.extract_text() + "\n"

        if ask_btn and question:
            answer = ask_question_huggingface(question, all_text)

            st.markdown(f"### ✅ Answer:\n**{answer}**")

            # Highlight in PDF and save
            highlighted_pdf_path = f"highlighted_{uploaded_file.name}"
            save_highlighted_pdf(uploaded_file, answer, highlighted_pdf_path)

            with open(highlighted_pdf_path, "rb") as f:
                st.download_button("📥 Download Highlighted PDF", f, file_name=highlighted_pdf_path)

            # Save history
            history_file = f"{st.session_state.username}_history.json"
            entry = {
                "subject": subject,
                "question": question,
                "answer": answer,
                "time": str(datetime.now())
            }
                # Save history
            history_file = f"{st.session_state.username}_history.json"
            entry = {
                "subject": subject,
                "question": question,
                "answer": answer,
                "time": str(datetime.now()),
                "filename": uploaded_file.name
            }

            # Load existing history or create new
            if os.path.exists(history_file):
                with open(history_file, "r") as f:
                    history = json.load(f)
            else:
                history = []

            # Append entry
            history.append(entry)

            # Save updated history
            with open(history_file, "w") as f:
                json.dump(history, f, indent=2)

    # Show history
    st.sidebar.title("📚 Q&A History")
    history_file = f"{st.session_state.username}_history.json"
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history = json.load(f)
            subjects = list(set([h["subject"] for h in history]))
            selected_subject = st.sidebar.selectbox("Select Subject", subjects)
            for h in history:
                if h["subject"] == selected_subject:
                    st.sidebar.markdown(f"**Q:** {h['question']}")
                    st.sidebar.markdown(f"**A:** {h['answer']}")
                    st.sidebar.markdown(f"🕒 {h['time']}")
                    st.sidebar.markdown("---")
