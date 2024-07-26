import streamlit as st
from config import get_module_by_name, get_module_exercise, update_lesson_status, check_module_completion, update_module_status
from lesson_generator import generate_lesson
from chat_bot_dialog import chat_bot
from quiz_dialog import quiz
from module_exercise import exercise_form
import logging
import json
logging.basicConfig(level=logging.DEBUG)

custom_css = """
<style>
     .header {
        background-color: #007d69; 
        border: 1px solid #007d69;
        box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.3);
        padding: 10px;
        text-align: center;
        font-size: 24px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #fff;
    }
    .logo-title {
        font-size: 24px;
        font-weight: bold;
        margin-left: 10px;
    }
    .user-info {
        font-size: 14px;
        color: #fff;
    }
    .course-info {
        text-align: center;
        margin-bottom: 20px;
    }
    .course-info h2 {
        font-size: 24px;
        color: #333;
    }
    .course-meta {
        font-size: 16px;
        color: #777;
    }
    .progress-bar {
        background-color: #ddd;
        border-radius: 5px;
        overflow: hidden;
        width: 80%;
        margin: 10px auto;
        height: 10px;
    }
    .progress {
        background-color: #4caf50;
        height: 100%;
        width: 0%;
    }
    .module {
        background-color: #ffffff;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 20px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .module h3 {
        font-size: 18px;
        color: #333;
    }
    .stButton>button {
        width: 100%;
        background-color: #003c3c;
        color: #ffffff;
    }
    .stButton>button:hover {
        border: #003c3c !important;
        color: #fff !important;
    }
    .stButton>button:active {
        background-color: #003c3c !important;
        color: #fff !important;
    }
    .module-content {
        background-color: #ffffff;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .module-content h3 {
        font-size: 18px;
        color: #333;
    }
    .module-content p {
        font-size: 14px;
        color: #555;
    }
    .footer {
        text-align: center;
        font-size: 14px;
        color: #666;
        margin-top: 20px;
    }
    .footer a {
        color: #666;
        text-decoration: none;
        margin: 0 5px;
    }
</style>
"""

def navigation():
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("🏠 Home",key="l_home",):
            st.session_state.page = 'home'
            st.rerun()
    with col5:
        if st.button("🚪 Logout",key="l_logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def calculate_progress(module):
    completed_lessons = sum(1 for lesson in module['lessons'] if lesson['status'] == 1)
    total_lessons = len(module['lessons'])
    return completed_lessons / total_lessons

def app():
    # logging.debug("Entering app function in lesson.py")
    try:
        st.set_page_config(page_title="Tutor AI", layout="wide")
        navigation()
        st.markdown(custom_css, unsafe_allow_html=True)

        # Header
        st.markdown('<div class="header"><span class="logo-title"> 🛡️ Tutor AI </span><span class="user-info">reetadityakoul@gmail.com</span></div>', unsafe_allow_html=True)

        # Main content
        if 'current_module' not in st.session_state:
            st.warning("Please select a module from the home page.")
            return

        module = st.session_state.current_module
        # logging.debug(f"Current module: {module}")
        
        st.title(module['module_name'])
        st.write(f"{len(module['lessons'])} Lessons")
        progress = calculate_progress(module)
        st.progress(progress)
        st.write(f"Module Progress: {progress*100:.0f}%")

        lessons = module['lessons']
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("<h3>Lessons List</h3>", unsafe_allow_html=True)
        
            for idx, lesson in enumerate(lessons):
                st.markdown(f"""
                <div class="module">
                    <h3>{lesson['name']}</h3>
                    <span>Status: {"Completed" if lesson['status'] == 1 else "Incomplete"}</span>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Start Lesson {idx+1}", key=f"lesson_{idx+1}"):
                    st.session_state.current_lesson = lesson
                    st.session_state.current_lesson_index = idx
                    st.session_state.generate_content = True
        with col2:
            st.markdown("<h3>Module Content</h3>", unsafe_allow_html=True)
            if 'current_lesson' in st.session_state:
                if st.session_state.current_lesson['name'] == 'Exercises':
                    print('IN Exercises')
                    res = get_module_exercise(module['module_name'])
                    mex = json.loads(res['metadatas'][0]['exercises'])
                    # exercise_form(mex)
                    responses = {}
                    with st.form(key='questions_form'):
                        for index,question in enumerate(mex):
                            key = f"response_{index}"
                            responses[question] = st.text_area(question, key=key)
                        submit_button = st.form_submit_button(label='Submit')
                        if submit_button:
                            st.success("Thanks for your responses!")
                            print(responses)
                else:
                    if st.session_state.get('generate_content', False):
                        with st.spinner('Generating lesson content...'):
                            print("quiz_content")
                            lesson_content, quiz_content = generate_lesson(module['module_name'], st.session_state.current_lesson['name'])
                            print("quiz_content+++++++++>")
                            st.session_state.current_lesson['content'] = lesson_content
                            st.session_state.quiz_questions = quiz_content
                            st.session_state.generate_content = False
                    
                    st.markdown(f"""
                    <div class="module-content">
                        <h3>{st.session_state.current_lesson['name']}</h3>
                        <p>{st.session_state.current_lesson['content']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    col_complete, col_qa, col_quiz = st.columns(3)
                    with col_complete:
                        if st.button("Mark as Complete",key="mark_complete_in_col"):
                            update_lesson_status(module['module_number'], st.session_state.current_lesson_index, 1)
                            # st.success(f"Lesson marked as complete!")
                            st.toast('Hooray! Lesson completed!!', icon='🎉')
                            
                            if check_module_completion(module['module_number']):
                                update_module_status(module['module_number'], 1)
                                st.success(f"Module {module['module_number']} completed! Next module unlocked.")
                            
                    with col_qa:
                        if st.button("Open Q&A Chat",key="open_dialog"):
                            st.session_state.qa_chat_open = True
                            chat_bot()

                    with col_quiz:
                        if st.button("Quiz",key="open_quiz_dialog"):
                            quiz()

                # if st.button("Mark as Complete",key="mark_complete_outside"):
                #     st.success(f"Lesson marked as complete!")
            else:
                st.info("Select a lesson to view its content")

    except Exception as e:
        logging.error(f"Error in lesson app: {str(e)}")
        st.error("An error occurred while loading the lesson. Please try again later.")