import streamlit as st

try:
    st.set_page_config(layout="wide", page_title="Streamlit Calculator")
except Exception as e:
    # set_page_config may raise if called multiple times; safe to log
    try:
        print('Component:', e)
    except Exception:
        pass

st.title("Hello, Streamlit!")
st.write("Welcome to the Streamlit Calculator.")
