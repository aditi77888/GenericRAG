import streamlit as st


def render():

    return st.file_uploader(

        "",

        accept_multiple_files=True,

        type=[
            "pdf",
            "docx",
            "txt",
            "csv",
            "png",
            "jpg",
            "jpeg",
            "md"
        ]
    )