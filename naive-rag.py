from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
import pymupdf 
import re
import os

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"  # Replace with your actual OpenAI API key
os.environ["CHROMA_DISABLE_TELEMETRY"] = "true"

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small") # This model is the lightest, fastest, and cheapest. It effectively replaces the old text-embedding-ada-002.
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

doc = pymupdf.open("/docs/PATH_TO YOUR_PDF")  

# Clean the text by removing unwanted lines
def clean_text(text):
    text = text.decode("utf8")  
    lines = text.splitlines()
    cleaned = []

    for line in lines:
        line_strip = line.strip()

        
        if re.match(r'^.*Os sertoes\s*-\s*BBB\s*-\s*\d+ª\s*PROVA\.indd(\s+\d+)?$', line_strip):
            continue

        
        if re.match(r'^\s*\d{1,2}/\d{1,2}/\d{2,4}\s+\d{2}:\d{2}$', line_strip):
            continue

        cleaned.append(line)

    return '\n'.join(cleaned)

# Open the PDF and process each page
with open("naive-rag-out.txt", "w", encoding="utf-8") as file:
    for page in doc:  
        text = page.get_text().encode("utf8")  
        cleaned = clean_text(text)  
        file.write(cleaned + "\n")  

# Split the text into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    separators=["\n\n", "\n", ".", " ", ""]
)

with open("naive-rag-out.txt", "r", encoding="utf-8") as file:
    chunks = splitter.split_text(file.read())

# Create a Chroma vector store and persist it
db = Chroma.from_texts(
    texts=chunks,
    embedding=embedding_model,
    persist_directory="./chroma_db_openai"
)

# Create a retriever from the vector store
retriever = db.as_retriever(search_kwargs={"k": 3})

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True  # para debug e análise
)

user_question = input("User: ")
answer = qa_chain.invoke(user_question)
print("Answer: ", answer['result'])