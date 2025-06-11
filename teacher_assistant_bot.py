import os
import re
import sys
import json
import faiss
import base64
import requests
from uuid import uuid4
from bs4 import BeautifulSoup
from langchain_nomic import NomicEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from course_data_extracter import CourseDataRetriever
from discourse_data_extractor import DisourseDataExtractor
from langchain_community.docstore.in_memory import InMemoryDocstore
from dotenv import load_dotenv
load_dotenv() 
os.environ["NOMIC_API_KEY"] = os.getenv("NOMIC_API_KEY")
class TeacherAssistant:
  def __init__(self) -> None:
      self.aipipe_api_key = os.getenv("AIPIPE_API_KEY")
      self.embeddings = NomicEmbeddings(model="nomic-embed-text-v1.5")
   # Load environment variables from .env file
      # self.course_data=CourseDataRetriever()
      # self.discourse_data = DisourseDataExtractor()
      # self.discourse_knowledge =self.add_knowledge_to_discourse_vector_store(self.discourse_data.discourse_extracted_data())
      self.discourse_knowledge =self.add_knowledge_to_discourse_vector_store()
      self.ds_course_vector_store = self.add_knowledge_to_ds_course_vector_store()


      # self.scraped_dscourse_data = None
      # self.ds_course_vector_store = None

  # async def setup(self):
  #       # run any async calls here
  #       self.scraped_dscourse_data = await self.course_data.scrape_tds_pages()
  #       self.ds_course_vector_store = self.add_knowledge_to_ds_course_vector_store(
  #           self.scraped_dscourse_data
  #       )

  def create_vector_store_for_ds_course(self):
    index = faiss.IndexFlatL2(len(self.embeddings.embed_query("hello world")))

    vector_store = FAISS(
        embedding_function=self.embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )
    return vector_store

  def create_vector_store_for_discourse_data(self):
    index = faiss.IndexFlatL2(len(self.embeddings.embed_query("hello world")))
    vector_store = FAISS(
        embedding_function=self.embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )
    return vector_store

  def add_knowledge_to_discourse_vector_store(self):
    with open("discourse_data.txt", "r", encoding="utf-8") as f:
        scraped_data = json.load(f)
    vector_store = self.create_vector_store_for_discourse_data()
    documents = []
    for link, data in scraped_data.items():
        text = str(data)
        content = f"url:{link}\nData:\n{text}"
        documents.append(Document(page_content=content))
    uuids = [str(uuid4()) for _ in range(len(documents))]
    vector_store.add_documents(documents=documents, ids=uuids)
    return vector_store

  def add_knowledge_to_ds_course_vector_store(self):
    with open("data_science_course_valid.json", "r", encoding="utf-8") as f:
        scraped_data = json.load(f)
    vector_store = self.create_vector_store_for_discourse_data()
    documents = []
    for link, data in scraped_data.items():
        text = str(data)
        content = f"url:{link}\nData:\n{text}"
        documents.append(Document(page_content=content))
    uuids = [str(uuid4()) for _ in range(len(documents))]

    vector_store.add_documents(documents=documents, ids=uuids)
    return vector_store

  def ds_course_context(self,question):
    context=self.ds_course_vector_store.similarity_search(question,k=3)
    return context

  def discourse_context(self,question):
    context=self.discourse_knowledge.similarity_search(question,k=3)
    return context

  def build_image_message(self, image_path):
        ext = os.path.splitext(image_path)[-1].lower()
        mime_type = "image/png" if ext == ".png" else "image/jpeg"
        with open(image_path, "rb") as img_file:
            b64 = base64.b64encode(img_file.read()).decode("utf-8")
        return f"data:{mime_type};base64,{b64}"

  def extract_answer_links_json(self,text: str) -> dict:
    candidates = re.findall(r"\{[^{}]*?(?:\{[^{}]*?\}[^{}]*?)*\}", text, re.DOTALL)
    for block in candidates:
        try:
            obj = json.loads(block)
            if isinstance(obj, dict) and "answer" in obj and "links" in obj:
                return obj
        except json.JSONDecodeError:
            continue
    raise ValueError("No valid JSON with 'answer' and 'links' found in response.")

# inside your TeacherAssistant.teacher_assistant_:
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"]


    result = extract_answer_links_json(raw)
    return result

  def teacher_assitant_(self,question,image_path=None):
    url = "https://aipipe.org/openrouter/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {self.aipipe_api_key}",
        "Content-Type": "application/json",
    }

    ds_course_context_=self.ds_course_context(question)
    discourse_context= self.discourse_context(question)

    print(discourse_context)
    image_prompt = f"""
          You will be given an image along with a question. Your task is to analyze the image and answer the question accurately.

          Use the following sources of knowledge to guide your response:

          1. **Data Science course materials** from Sanand (Data Science lectures).
          2. **Discourse forum discussions** related to the course.

          Always respond in a polite and easy-to-understand manner. Focus only on topics related to Data Science. If the question is unrelated, do not respond.

          Use the provided course and forum context to enrich your answer when applicable.

          ---

          **Data Science Course Details:**
          {ds_course_context_}

          **Discourse Forum Data:**
          {discourse_context}


          ----

          **Return format (always JSON):Final result should be in given json fomrat mind it**
          {{
            "answer": "<your answer here>",
            "links": [
              {{
                "url": "<relevant URL 1>",
                "text": "<brief description of link 1>"
              }},
              {{
                "url": "<relevant URL 2>",
                "text": "<brief description of link 2>"
              }}
            ]
          }}
          """


    text_prompt=f"""role: You are an IITM teaching assistant.

            knowledge: You have access to:
              1. Data Science course materials from Sanand (Data Science lectures).
              2. Discourse forum data related to the course.

            Your primary objective is to answer students’ Data Science questions using the provided course details and Discourse data. Always respond politely and in simple English for easy understanding. If a question is not related to Data Science, do not answer it.

            Data Science course details:
            {ds_course_context_}

            Discourse forum data:
            {discourse_context}

            Return format (always JSON) Final result should be in given json fomrat mind it:
            {{
              "answer": "<your answer here>",
              "links": [
                {{
                  "url": "<relevant URL 1>",
                  "text": "<brief description of link 1>"
                }},
                {{
                  "url": "<relevant URL 2>",
                  "text": "<brief description of link 2>"
                }}
              ]
            }}
            """



    if image_path:
        messages = [

          {"role": "assistant", "content": image_prompt},
          {
            "role": "user",
            "content": [
                { "type": "text", "text": question },
                { "type": "image_url", "image_url": { "url": self.build_image_message(image_path) } }
            ]
        }
    ]

    else:
        messages = [
                  {"role": "assistant", "content": text_prompt},
                  {"role": "user", "content": question}
              ]


    # print(ds_course_context_)
    # print(discourse_context)


    payload = {
        "model":"openai/gpt-4.1-nano",
        "temperature": 0.1,
        "messages": messages
    }

    # 4. Send the POST and parse JSON
    try:
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return e

    data = resp.json()
    response = data["choices"][0]["message"]["content"]
    try :
      result = self.extract_answer_links_json(response)
      return result
    except:
      self.teacher_assitant_(question,image_path)