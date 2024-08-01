# import streamlit as st
custom_css = """ 
<style>
    #MainMenu { display: none !important; }
    footer { display: none !important;  }
    header { display: none !important; }
    .st-emotion-cache-1jicfl2 { 
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
</style>
"""

import streamlit as st

from config import authenticate_student, authenticate_tutor, register_student

def app():
    st.set_page_config(page_title="Tutor AI - Login/Register", layout="wide")
    st.markdown(custom_css, unsafe_allow_html=True)

    st.title("Tutor AI - Login/Register")

    tab1, tab2, tab3 = st.tabs(["Student Login", "Student Registration", "Tutor Login"])

    with tab1:
        st.header("Student Login")
        email = st.text_input("Email", key="email_id")
        password = st.text_input("Password",type="password", key="password_")
        
        if st.button("Login as Student"):
            if authenticate_student(email, password):
                st.session_state.user_type = 'student'
                st.session_state.email = email
                st.session_state.password = password
                st.success("Logged in successfully as Student")
                st.session_state['page'] = 'home'
                st.rerun()
            else:
                st.error("Invalid student credentials")

    with tab2:
        st.header("Student Registration")
        student_name = st.text_input("Enter your name", key="new_username")
        email_id = st.text_input("Enter your Email ID", key="student_email_id")
        new_password = st.text_input("Choose a Password", type="password", key="new_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

        if st.button("Register"):
            if new_password != confirm_password:
                st.error("Passwords do not match")
            elif register_student(student_name, email_id, new_password):
                st.success("Registration successful! You can now log in.")
            else:
                st.error("Registration failed. Username or Student ID may already exist.")

    with tab3:
        st.header("Tutor Login")
        tutor_name = st.text_input("Tutor Name", key="tutor_n")
        tutor_email = st.text_input("Email", key="tutor_e")
        tutor_password = st.text_input("Password", type='password', key="tutor_p")
        
        if st.button("Login as Tutor"):
            if authenticate_tutor(tutor_name, tutor_email, tutor_password):
                st.session_state.tutor_name = tutor_name
                st.session_state.tutor_email = tutor_email
                st.success("Logged in successfully as Tutor")
                st.session_state['page'] = 'tutor'
                st.rerun()
            else:
                st.error("Invalid tutor credentials")

    if 'user' in st.session_state:
        if st.session_state.user_type == 'student':
            st.success(f"Welcome, Student {st.session_state.user}!")
            if st.button("Go to Courses"):
                st.session_state.page = 'home'
                st.rerun()
        elif st.session_state.user_type == 'tutor':
            st.success(f"Welcome, Tutor {st.session_state.user}!")
            if st.button("View Student Progress"):
                st.session_state.page = 'tutor_dashboard'
                st.rerun()
# # streamlit run app.py --server.runOnSave true