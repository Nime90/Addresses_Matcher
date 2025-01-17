import streamlit as st


def run():
    st.title("Welcome to the Location Matcher! :wave:")
    st.header(":toolbox: Our Services")

    st.subheader("Close Name Matcher")
    st.text("Tool that compare in a automated way the names of the streets")

    st.subheader("The Geo Locator")
    st.text("This tool find the lat and lon for each address and match the ones that are closer" )
    
    st.subheader("The Match Assistant!(Gemini)")
    st.text( "This tool uses Gemini AI to match the addresses")

    st.subheader("The Match Assistant!(OpenAI)")
    st.text( "This tool uses ChatGpt AI to match the addresses")


if __name__ == "__main__":
    run()
