# import packages

import streamlit as st # type: ignore
from streamlit_extras.add_vertical_space import add_vertical_space # type: ignore
from PyPDF2 import PdfReader # type: ignore
from langchain.text_splitter import RecursiveCharacterTextSplitter # type: ignore
from langchain.embeddings.openai import OpenAIEmbeddings # type: ignore
from langchain.vectorstores import FAISS # type: ignore
import pickle
from dotenv import load_dotenv
import os
from langchain.llms import OpenAI # type: ignore
from langchain.chains.question_answering import load_qa_chain # type: ignore

# Sidebar contents for the Streamlit app
with st.sidebar:
    st.title("AskPDF")
    st.markdown('''
    ## About
    This app is an LLM-powered chatbot built using:
    - [Streamlit](https://streamlit.io)
    - [LangChain](https://www.langchain.com)
    - [OpenAI](https://openai.com)
                ''')
    add_vertical_space(5)
    st.write(
        'Made with ❤️ by [Bhupendrasinh Thakre] (https://www.linkedin.com/in/bcthakre/)')

def main():
    """Main function to run the Streamlit app."""
    
    st.header("Chat with your pdf 📜")

    # Allow users to upload a PDF file
    pdf = st.file_uploader("Upload a PDF file", type="pdf")

    # Load environment variables from .env file
    load_dotenv()

    if pdf is not None:
        # Read the uploaded PDF file
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # Split the text from PDF into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_text([text])

        # Load or generate embeddings for the chunks of text
        store_name = pdf.name[:-4]
        if os.path.exists(f"{store_name}.pkl"):
            with open(f"{store_name}.pkl", 'rb') as f:
                VectorStore = pickle.load(f)
        else:
            embeddings = OpenAIEmbeddings()
            VectorStore = FAISS.from_texts(chunks, embeddings)
            with open(f"{store_name}.pkl", 'wb') as f:
                pickle.dump(VectorStore, f)

        # Accept user's question and fetch relevant document sections
        query = st.text_input("Ask your question here")
        if query:
            docs = VectorStore.similarity_search(query, k=3)
            
            # Use OpenAI model to fetch answers based on user's question and relevant sections
            llm = OpenAI()
            chain = load_qa_chain(llm, chain_type="stuff")
            response = chain.run(input_documents=docs, question=query)

            st.write(response)

if __name__ == '__main__':
    # Run the main function if the script is executed as the main module
    main()
