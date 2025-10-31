import streamlit as st

try:
    st.set_page_config(layout="wide", page_title="Streamlit Calculator")
except Exception as e:
    # set_page_config may raise if called multiple times; safe to log
    try:
        print('Component:', e)
    except Exception:
        pass

# Preserve existing title
st.title("Hello, Streamlit!")

# Sidebar layout
st.sidebar.title("Calculator")
st.sidebar.write("Use the sidebar to navigate the app.")
page = st.sidebar.selectbox("Choose view", ("Calculator", "History"))

# Main area
st.header("Streamlit Calculator")
st.write("Welcome to the Streamlit Calculator.")
st.write(f"Selected page: {page}")

# Example placeholder imports (commented out)
# from components.my_component import MyComponent  # component class placeholder
# from utils.helpers import format_value  # utility function placeholder

# TODO: integrate custom components and utility functions here
