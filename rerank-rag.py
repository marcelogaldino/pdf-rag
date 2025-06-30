from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
import pymupdf 
import re
import os

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"  # Replace with your actual OpenAI API key
os.environ["CHROMA_DISABLE_TELEMETRY"] = "true"

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small") # This model is the lightest, fastest, and cheapest. It effectively replaces the old text-embedding-ada-002.
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

doc = pymupdf.open("./docs/os-sertoes.pdf")  

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
with open("rerank-rag-out.txt", "w", encoding="utf-8") as file:
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

with open("rerank-rag-out.txt", "r", encoding="utf-8") as file:
    chunks = splitter.split_text(file.read())

# Create a Chroma vector store and persist it
db = Chroma.from_texts(
    texts=chunks,
    embedding=embedding_model,
    persist_directory="./chroma_db_openai_rerank_rag"
)

# Create a retriever from the vector store
retriever = db.as_retriever(search_kwargs={"k": 15})

user_question = input("User: ")

candidate_chunks = retriever.invoke(user_question)

prompt_template = PromptTemplate.from_template(
    """
    Pergunta: {question}

    Texto candidato:
    {chunk}

    O quanto esse texto é relevante (de 1 a 10) para responder à pergunta acima? Justifique em uma frase. No final, apenas escreva o número.
    """
)

llm_chain = prompt_template | llm

scored_chunks = []

for doc in candidate_chunks:
    res = llm_chain.invoke({
        "question": user_question,
        "chunk": doc.page_content
    })

    try:
        score = int("".join(filter(str.isdigit, res)))
    except:
        score = 0

    scored_chunks.append((score, doc))

scored_chunks.sort(reverse=True, key=lambda x: x[0])

top_docs = [doc for score, doc in scored_chunks[:3]]

qa_chain = load_qa_chain(llm, chain_type="stuff")

answer = qa_chain.invoke({
    "input_documents": top_docs,
    "question": user_question
})
print("Answer: ", answer)