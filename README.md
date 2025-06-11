# 🤖 AI Teaching Assistant for Data Science 🧠📚

An intelligent assistant that answers **Data Science** questions using course content and Discourse discussions. Built with **FastAPI**, **LangChain**, **FAISS**, and **Nomic Embeddings**. Supports both text and image-based queries, and returns structured JSON results.

---

## 🚀 Features

✅ Context-aware answers using:
- 📘 **Course materials**  
- 💬 **Discourse forum** data  

✅ Smart vector-based search using FAISS  
✅ Accepts **text or image** input queries  
✅ Returns clean, structured **JSON** like:

```json
{
  "answer": "...",
  "links": [
    { "url": "...", "text": "..." }
  ]
}
```

---

## 📦 Requirements

- 🐍 Python **3.8+**
- 📄 See [`requirements.txt`](./requirements.txt) for full dependencies

---

## ⚙️ Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd TDS_TA
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file:**
   ```env
   NOMIC_API_KEY=your_nomic_api_key
   AIPIPE_API_KEY=your_aipipe_api_key
   ```

5. **Ensure your data files exist:**
   - `data_science_course_valid.json`
   - `discourse_data.txt`

---

## ▶️ Running the API

Start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --reload
```

---

## 📬 Usage

### 🔹 POST `/ask`
Submit `multipart/form-data` with:
- `question` (text)
- `image` (optional image file)

### 🔹 POST `/ask_json`
Submit JSON with:
```json
{
  "question": "Your question?"
}
```

---

## 🧪 Example Call Image Part Commented

```bash
curl -X POST https://shriyasingh48-tds-fastapi.hf.space/ask \
  -F question="What is regression in ML?"
```

---

## 🛡 License

[MIT License](LICENSE)

---

## ✨ Powered By

- [LangChain](https://www.langchain.com/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [Nomic AI](https://www.nomic.ai/)
- [FastAPI](https://fastapi.tiangolo.com/)
