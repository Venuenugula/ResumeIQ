from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class GeminiEmbeddings(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        result = []
        for text in texts:
            response = client.models.embed_content(
                model="gemini-embedding-001",
                contents=text
            )
            result.append(response.embeddings[0].values)
        return result

    def embed_query(self, text: str) -> list[float]:
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text
        )
        return response.embeddings[0].values

def build_vectorstore(resume_text: str) -> FAISS:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.create_documents([resume_text])
    embeddings = GeminiEmbeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore

def retrieve_relevant_chunks(vectorstore: FAISS, jd_text: str, k: int = 6) -> str:
    docs = vectorstore.similarity_search(jd_text, k=k)
    return "\n\n".join([doc.page_content for doc in docs])