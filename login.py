import streamlit as st

def app():
    st.set_page_config(page_title="Tutor AI - Login")
    # st.markdown(custom_css, unsafe_allow_html=True)

    st.title("Login to Tutor AI")

    tab1, tab2 = st.tabs(["Student Login", "Tutor Login"])

    with tab1:
        st.header("Student Login")
        student_name = st.text_input("Student Name", key="student-name")
        student_id = st.text_input("Student ID", key="student-id")
        module_convener = st.text_input("Module Convener", key="module-convener")

        
        if st.button("Login as Student"):
            if student_name and student_id and module_convener:
                st.session_state['student_name'] = student_name
                st.session_state['student_id'] = student_id
                st.session_state['module_convener'] = module_convener
                st.success("Logged in successfully as Student")
                st.session_state['page'] = 'home'
                st.rerun()
            else:
                st.error("Please fill out all fields")

    with tab2:
        st.header("Tutor Login")
        tutor_name = st.text_input("Tutor Name", key="tutor_name_login")
        tutor_email = st.text_input("University Email", key="tutor-email")
        
        if st.button("Login as Tutor"):
            if tutor_name and tutor_email:
                st.session_state.tutor_name = tutor_name
                st.session_state.tutor_email = tutor_email
                st.success("Logged in successfully as Tutor")
                st.session_state['page'] = 'tutor'
                st.rerun()
            else:
                st.error("Invalid tutor credentials")

# streamlit run app.py --server.runOnSave true