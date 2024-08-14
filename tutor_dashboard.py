import streamlit as st
from new_config import get_modules, get_module_exercise, update_module_feedback, students_collection
import random
import json

custom_css = """
<style>
    #MainMenu { display: none !important; }
    footer { display: none !important;  }
    header { display: none !important; }
    @media{
        .st-emotion-cache-13ln4jf { 
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
        }
    }
    .st-emotion-cache-13ln4jf { 
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
    }
"""

def navigation():
    col1, col2, col3, col4, col5 = st.columns(5)
    with col5:
        if st.button("🚪 Logout",key="home_logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def get_student_data():
    return students_collection.get()['metadatas']

def display_student_profile(student):
    st.subheader(f"Student Profile: {student['name']}")
    st.write(f"Email: {student['email']}")
    st.write(f"Enrolled: {student['enrolled']}")
    st.write(f"Overall Progress: {student['progress']}%")
    st.progress(student['progress'] / 100)

    # Here you can add the existing implementation for displaying modules, exercises, etc.
    modules = get_modules()
    completed_modules = sum(1 for module in modules if module['status'] == 1)
    total_modules = len(modules)

    with st.expander("Module Progress"):
        col1, col2, col3 = st.columns(3)
        col1.metric("Number of Modules", total_modules)
        col2.metric("Modules Completed", completed_modules)
        col3.metric("Modules Remaining", total_modules - completed_modules)

    st.subheader("Exercises Submitted")
    for module in modules:
        if module['status'] == 1:
            ex = get_module_exercise(module_name=module['module_name'])
            with st.expander(module['module_name']):
                st.write(f"Submission date: {random.randint(1, 28)}/{random.randint(1, 12)}/2024")
                st.write(f"Score: {random.randint(70, 100)}%")
                
                st.subheader("Questions and Answers")
                for idx, (question, answer) in enumerate(json.loads(ex['metadatas'][0]["results"]).items()):
                    st.write(f"Q{idx+1}: {question}")
                    st.text_area(f"Answer {idx+1}", value=answer, key=f"{module['module_name']}_{idx}", disabled=True)
                
                with st.form(f"feedback_form_{module['module_name']}"):
                    feedback = st.text_area(f"Provide feedback for {module['module_name']}")
                    submit = st.form_submit_button("Submit Feedback")
                    if submit:
                        update_module_feedback(module['module_name'], feedback)
                        st.success("Feedback submitted successfully!")


def app():
    # Sample data (replace with your actual data)
    print(get_student_data())
    st.markdown(custom_css, unsafe_allow_html=True)
    modules = get_modules()
    completed_modules = 0
    total_modules = len(modules)
    current_module = None
    found_current_module = False
    current_module_progress = 0
    exercises = []
    submitted_exercises = []
    # print(module_exercise['metadatas'][0])

    for module in modules:
        if module['status'] == 1:
            completed_modules += 1
            # print(type(module_exercise))
            # exercises.append(json.loads(module_exercise))
            ex = get_module_exercise(module_name=module['module_name'])
            submitted_exercises.append(ex['metadatas'][0])
            found_current_module = False
        else:
            if not found_current_module:
                current_module = module['module_name']
                current_module_progress = module['progress']
                found_current_module = True


    navigation()
    st.title("Tutor Dashboard")

    with st.expander("Student Progress"):
        st.subheader("Current Module")
        st.write(current_module)
        
        st.subheader("Progress of Current Module")
        st.progress(current_module_progress / 100)
        st.write(f"{current_module_progress}%")
        
        st.subheader("Overall Progress")
        col1, col2, col3 = st.columns(3)
        col1.metric("Number of Modules", total_modules)
        col2.metric("Modules Completed", completed_modules)
        col3.metric("Modules Remaining", total_modules - completed_modules)
    st.subheader("Exercises Submitted")

    for i, exercise in enumerate(submitted_exercises):
        
        with st.expander(exercise["module_name"]):
            st.write(f"Submission date: {random.randint(1, 28)}/{random.randint(1, 12)}/2024")
            st.write(f"Score: {random.randint(70, 100)}%")
            
            st.subheader("Questions and Answers")
            for idx, (question, answer) in enumerate(json.loads(exercise["results"]).items()):
                st.write(f"Q{idx+1}: {question}")
                st.text_area(f"Answer {idx+1}", value=answer, key=f"{exercise['module_name']}_{idx}", disabled=True)
            # rating = st.slider("Rate the student's performance (1-5):",  1,5,10)
            # if st.button(f"Provide feedback for {exercise['module_name']}"):
            with st.form("my_form_tutor"):
                feedback = st.text_area(f"Provide feedback for {exercise['module_name']}", key=f"feedback_{exercise['module_name']}")
                submit = st.form_submit_button("Submit Feedback")
                if submit:
                    update_module_feedback(exercise['module_name'],feedback)
                    
                    st.success("Feedback submitted successfully!")

    # Additional features for better user experience
    st.sidebar.title("Quick Actions")
    if st.sidebar.button("Send message to student"):
        st.sidebar.text_area("Message:")
        st.sidebar.button("Send")

    if st.sidebar.button("Schedule a meeting"):
        st.sidebar.date_input("Select date")
        st.sidebar.time_input("Select time")
        st.sidebar.button("Confirm meeting")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Student Information")
    st.sidebar.write("Name: Tim Cube")
    st.sidebar.write("Email: Tim.cub@exeter.ac.uk")
    st.sidebar.write("Enrolled: 15/08/2024")