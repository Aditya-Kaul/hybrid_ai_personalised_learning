import streamlit as st

def exercise_form(exercises):
    with st.form(key='questions_form'):

        for question, key in enumerate(exercises):
            response = st.text_area(question, key=key)
        
        submit_button = st.form_submit_button(label='Submit')

        # Check if form is submitted
        if submit_button:
            st.success("Thanks for your responses!")