from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
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
with open("parent-rag-out.txt", "w", encoding="utf-8") as file:
    for page in doc:  
        text = page.get_text().encode("utf8")  
        cleaned = clean_text(text)  
        file.write(cleaned + "\n")  

# Split the text into chunks
parent_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ".", " ", ""]
)

with open("parent-rag-out.txt", "r", encoding="utf-8") as file:
    parent_docs = parent_splitter.split_text(file.read())

child_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

child_docs = []
parent_map = {}

for i, parent_text in enumerate(parent_docs):
    parent_id = f"parent_{i}"
    
    chunks = child_splitter.split_text(parent_text)
    
    for j, chunk in enumerate(chunks):
        child_docs.append({
            "text": chunk,
            "metadata": {
                "parent_id": parent_id,
                "chunk_index": j
            }
        })

    parent_map[parent_id] = parent_text

texts = [doc["text"] for doc in child_docs]
metadatas = [doc["metadata"] for doc in child_docs]

# Create a Chroma vector store and persist it
db = Chroma.from_texts(
    texts=chunks,
    embedding=embedding_model,
    metadatas=metadatas,
    persist_directory="./chroma_db_openai_parent_rag"
)

# Create a retriever from the vector store
retriever = db.as_retriever(search_kwargs={"k": 4})

user_question = input("User: ")

# Retorna chunks curtos
result_chunks = retriever.get_relevant_documents(user_question)

# Recupera os parent_ids dos resultados
parent_ids = list({doc.metadata["parent_id"] for doc in result_chunks})

# Pega os textos grandes originais
parents = [parent_map[pid] for pid in parent_ids]

qa_chain = load_qa_chain(llm, chain_type="stuff")

#resposta = qa_chain.run(input_documents=parents, question=query)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True  # para debug e análise
)

answer = qa_chain.invoke(input_documents=parents, question=user_question)
print("Answer: ", answer['result'])