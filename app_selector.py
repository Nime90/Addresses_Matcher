import streamlit as st
from apps import (
    welcome,
    get_close_match,
    match_using_gemini,
    match_using_openAI,
    matching_geoloc
    )

pages = [
    {"title": "Welcome", "function": welcome.run},
    {"title": "Close Name Matcher", "function": get_close_match.run},
    {"title": "The Geo Locator", "function": matching_geoloc.run},
    {"title": "The Match Assistant!(Gemini)", "function": match_using_gemini.run},
    {"title": "The Match Assistant!(OpenAI)", "function": match_using_openAI.run}
]

st.set_page_config(page_title="AAA", page_icon="🦾", layout="wide")
st.sidebar.title("AAA 🦾")
st.sidebar.markdown("Just some AAA stuff. *Choose an app from the menu*")

page = st.sidebar.selectbox("App", pages, format_func=lambda page: page["title"])

page["function"]()