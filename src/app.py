from tempfile import NamedTemporaryFile
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from fastapi import FastAPI, UploadFile
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# Langsmith tracking
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

app = FastAPI()


@app.post("/")
async def databot_endpoint(question: str, model: str, file: UploadFile):

    with NamedTemporaryFile(delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        file_path = tmp.name

    # load data from pdf
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    # split data in chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = text_splitter.split_documents(docs)

    # index the chunks in vector db
    db = Chroma.from_documents(documents, OpenAIEmbeddings())

    # prompt template
    prompt = ChatPromptTemplate.from_template(
        """
    Answer the following question based only on the provided context. 
    Think step by step before providing a detailed answer. 
    <context>
    {context}
    </context>
    Question: {input}"""
    )

    # select model based on input from user
    if model == "Llama":
        llm = Ollama(model="llama2")
    else:
        llm = ChatOpenAI(model="gpt-3.5-turbo")

    # create docment chain
    document_chain = create_stuff_documents_chain(llm, prompt)

    # create retriever chain
    retriever = db.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    # run the chain and retrieve the results from the context uploaded by the user
    response = retrieval_chain.invoke({"input": question})

    return response


if __name__ == "__main__":
    import uvicorn
    from app import app

    # logging.INFO("Starting Server")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
