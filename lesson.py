import streamlit as st
from ai_feedback_interpret import apply_feedback
from config import get_module_exercise, get_student_details, update_lesson_status, check_module_completion, update_module_progress, update_module_status, store_module_exercise, update_student_progress
from lesson_generator import display_lesson_with_images, get_or_generate_lesson
from chat_bot_dialog import chat_bot
from quiz_dialog import quiz
from module_exercise import exercise_form
import logging
import json
logging.basicConfig(level=logging.DEBUG)

custom_css = """
<style>
    #MainMenu { display: none !important; }
    footer { display: none !important;  }
    header { display: none !important; }
    .st-emotion-cache-1jicfl2 { 
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
    }
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

    .st-c2 {
        background-color: #007d69 !important;
    }

    .feedback-notification {
        background-color: #f0f8ff;
        border-left: 6px solid #4CAF50;
        margin-bottom: 15px;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        animation: slideIn 0.5s ease-out;
    }

    @keyframes slideIn {
        from {
            transform: translateX(-100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    .feedback-notification h4 {
        margin: 0;
        color: #4CAF50;
    }

    .feedback-notification p {
        margin: 5px 0 0 0;
        color: #333;
    }

    .close-button {
        float: right;
        cursor: pointer;
        color: #aaa;
    }

    .close-button:hover {
        color: #333;
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

# def show_feedback_notification():
#     notification_container = st.empty()
#     notification_html = """
#     <div class="feedback-notification">
#         <span class="close-button" onclick="this.parentElement.style.display='none';">&times;</span>
#         <h4>New Feedback Available!</h4>
#         <p>Your tutor has provided feedback on your recent module. Click 'View Feedback' to see details.</p>
#     </div>
#     """
#     notification_container.markdown(notification_html, unsafe_allow_html=True)
    
    # if st.button("View Feedback"):
    #     notification_container.empty()
    #     return True
    # return False

def calculate_progress(module, student_progress):
    # completed_lessons = sum(1 for lesson in module['lessons'] if lesson['status'] == 1)
    # total_lessons = len(module['lessons'])
    # return completed_lessons / total_lessons
    progress = json.loads(student_progress)
    module_progress = progress.get(module['module_name'], {})
    completed_lessons = sum(1 for status in module_progress.values() if status == 1)
    total_lessons = len(module.get('lessons', []))
    if total_lessons > 0:
        return completed_lessons / total_lessons 
    else:
        return 0
    
def refresh():
    student_details = get_student_details(st.session_state.email)
    st.session_state.student_details = student_details


def app():
    # logging.debug("Entering app function in lesson.py")
    try:
        st.set_page_config(page_title="Tutor AI", layout="wide")
        navigation()
        st.markdown(custom_css, unsafe_allow_html=True)

        # Header
        st.markdown('<div class="header"><span class="logo-title"> 🛡️ Tutor AI </span><span class="user-info">Aditya Koul</span></div>', unsafe_allow_html=True)

        # Main content
        if 'current_module' not in st.session_state:
            st.warning("Please select a module from the home page.")
            return

        module = st.session_state.current_module

        # exercise_data = get_module_exercise(module['module_name'])
        # has_new_feedback = 'tutor_feedback' in exercise_data['metadatas'][0] and not st.session_state.get('feedback_viewed', False)
        # print('tutor_feedback' in exercise_data['metadatas'][0])
        # print(st.session_state.get('feedback_viewed', False))
        # if has_new_feedback:
        #     view_feedback = show_feedback_notification()
        #     if view_feedback:
        #         st.session_state.feedback_viewed = True
        #         needs_review = apply_feedback(module['module_name'])
                
        #         if needs_review:
        #             st.warning("Based on the tutor's feedback, you need to review this module.")
                    
        
        st.title(module['module_name'])
        st.write(f"{len(module['lessons'])} Lessons")
        student_details = st.session_state.student_details
        print(student_details.get('progress', {}))
        student_progress = student_details.get('progress', {})
        progress = calculate_progress(module, student_progress)
        update_module_progress(module['module_number'],progress)
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
                    print('IN Exercises+++++++++++++EXERCISEDSSSS')
                    res = get_module_exercise(module['module_name'])
                    ex_exists = 'results' in res['metadatas'][0]
                    mex = json.loads(res['metadatas'][0]['exercises'])
                    # exercise_form(mex)
                    responses = {}
                    if ex_exists:
                        results = json.loads(res['metadatas'][0]['results'])
                        with st.form(key='questions_form'):
                            for index,question in enumerate(mex):
                                key = f"response_{index}"
                                default_value = results.get(question, "")
                                responses[question] = st.text_area(question,value=default_value, key=key)
                            submit_button = st.form_submit_button(label='Submit')
                            if submit_button:
                                store_module_exercise(module['module_name'],responses)
                                st.success("Thanks for your responses!")
                                update_lesson_status(module['module_number'], st.session_state.current_lesson_index, 1)
                                if check_module_completion(module['module_number']):
                                    update_module_status(module['module_number'], 1)
                                    st.success(f"Module {module['module_number']} completed! Next module unlocked.")
                    else:
                        with st.form(key='questions_form'):
                            for index,question in enumerate(mex):
                                key = f"response_{index}"
                                responses[question] = st.text_area(question, key=key)
                            submit_button = st.form_submit_button(label='Submit')
                            
                            if submit_button:
                                store_module_exercise(module['module_name'],responses)
                                print(responses)
                                st.success("Thanks for your responses!")
                                update_lesson_status(module['module_number'], st.session_state.current_lesson_index, 1)
                                if check_module_completion(module['module_number']):
                                    update_module_status(module['module_number'], 1)
                                    st.success(f"Module {module['module_number']} completed! Next module unlocked.")
                else:
                    if st.session_state.get('generate_content', False):
                        with st.spinner('Generating lesson content...'):
                            lesson_content, quiz_content = get_or_generate_lesson(module['module_name'], st.session_state.current_lesson['name'],student_details['email'])
                             
                            # pdf_path = '/Users/adityakoul/Documents/ml kb/Text Book/Hands-On Machine Learning.pdf'
                            # display_lesson_with_images(lesson_content, pdf_path)
                            st.session_state.current_lesson['content'] = lesson_content
                            st.session_state.quiz_questions = quiz_content
                            st.session_state.generate_content = False
                            
                            if 'messages' in st.session_state:
                                del st.session_state.messages
                    
                    st.markdown(f"""
                    <div class="module-content">
                        <h3>{st.session_state.current_lesson['name']}</h3>
                        <p>{st.session_state.current_lesson['content']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    col_complete, col_qa, col_quiz = st.columns(3)
                    with col_complete:
                        if st.button("Mark as Complete",key="mark_complete_in_col"):
                            if 'quiz_submitted' in st.session_state:
                                if st.session_state.quiz_submitted == True:
                                    update_lesson_status(module['module_number'], st.session_state.current_lesson_index, 1)
                                    st.toast('Hooray! Lesson completed!!', icon='🎉')
                                    # del st.session_state.quiz_submitted
                                    print('LESSON COMPLETED')
                                    update_student_progress(student_details['email'], module['module_name'], st.session_state.current_lesson['name'], 1)
                                    refresh()
                                    student_details = st.session_state.student_details
                                    student_progress = student_details.get('progress', {})
                                    progress = calculate_progress(module, student_progress)
                                    print(progress)
                                    st.success("Lesson marked as complete!")
                                    st.rerun()
                            else:
                                print('Please pass quiz to complete.')
                                st.error('Please pass quiz to complete.', icon="⚠️")
                                # st.toast('Please pass quiz to complete.', icon="⚠️")
                            if check_module_completion(module['module_number']):
                                update_module_status(module['module_number'], 1)
                                st.success(f"Module {module['module_number']} completed! Next module unlocked.")
                            
                    with col_qa:
                        if st.button("Open Q&A Chat",key="open_dialog"):
                            # st.session_state.qa_chat_open = True
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