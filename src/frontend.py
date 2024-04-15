import streamlit as st
import requests

st.title("Databot")
uploaded_file = st.file_uploader(
    "Upload your pdf you want to ask questions from", type="pdf"
)
question = st.text_input("Ask your questions here")
model_options = ["Llama", "GPT"]
selected_model = st.selectbox("Select a model", model_options)
st.write("Model selected:", selected_model)

if question and uploaded_file:
    data = {"question": question, "model": selected_model}
    response = requests.post(
        "http://databot-service:80/", params=data, files={"file": uploaded_file}
    )
    st.write(response.json()["answer"])
