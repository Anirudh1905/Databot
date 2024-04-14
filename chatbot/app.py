from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama

import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# Langsmith tracking
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

# prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Please response to the user queries"),
        ("user", "Question:{question}"),
    ]
)

# streamlit framework
st.title("Chatbot with 2 models")
input_text = st.text_input("Search the topic u want")
model_options = ["LLama", "GPT"]
selected_model = st.selectbox("Select a model", model_options)
st.write("You selected:", selected_model)

# llm model
if selected_model == "LLama":
    llm = Ollama(model="llama2")
else:
    llm = ChatOpenAI(model="gpt-3.5-turbo")

output_parser = StrOutputParser()
chain = prompt | llm | output_parser

if input_text:
    st.write(chain.invoke({"question": input_text}))
