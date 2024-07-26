import streamlit as st
from config import get_student_progress

def app():
    st.set_page_config(page_title="Tutor AI - Teacher Dashboard", layout="wide")
    # st.markdown(custom_css, unsafe_allow_html=True)

    st.title("Teacher Dashboard")

    # Mock student list - in a real app, this would come from a database
    students = ['student1', 'student2', 'student3']

    for student in students:
        st.subheader(f"Progress for {student}")
        progress = get_student_progress(student)
        for module, percentage in progress.items():
            st.write(f"{module}: {percentage}%")
            st.progress(percentage / 100.0)

    if st.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()