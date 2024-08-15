import json
import streamlit as st
from ai_feedback_interpret import apply_feedback
from new_config import get_module_exercise, get_module_status, check_module_completion, get_student_details
# import logging

# logging.basicConfig(level=logging.DEBUG)

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
    .course-info p {
        font-size: 16px;
        color: #777;
    }
    .module {
        background-color: #ffffff;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        height: 255px;
    }
    .module > .desc  {
        overflow: scroll;
        height: 160px;
    }
    .module h3 {
        font-size: 20px;
        color: #333;
    }
    .module p {
        font-size: 14px;
        color: #555;
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
    .st-c2 {
        background-color: #007d69 !important;
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
def calculate_progress(module):
    completed_lessons = sum(1 for lesson in module['lessons'] if lesson['status'] == 1)
    total_lessons = len(module['lessons'])
    return completed_lessons / total_lessons

def navigation():
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("🏠 Home",key="home_home",):
            st.session_state.page = 'home'
            st.rerun()
    with col5:
        if st.button("🚪 Logout",key="home_logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
            
def show_feedback_notifications(modules):
    for module in modules:
        module_name = module['module_name']
        exercise_data = get_module_exercise(module_name)
        
        if 'tutor_feedback' in exercise_data['metadatas'][0] and not st.session_state.get(f'feedback_viewed_{module_name}', False):
        # if 'tutor_feedback' in exercise_data['metadatas'][0]:
            notification_container = st.empty()
            tutor_feedback = exercise_data['metadatas'][0]['tutor_feedback']
            notification_html = f"""
            <div class="feedback-notification" id="notification_{module_name}">
                <span class="close-button" onclick="this.parentElement.style.display='none';">&times;</span>
                <h4>New Feedback Available for {module_name}!</h4>
                <p>Your tutor has provided feedback on this module. Click 'View Feedback' to see details.</p>
            </div>
            """
            notification_container.markdown(notification_html, unsafe_allow_html=True)
            
            if st.button(f"View Feedback for {module_name}"):
                st.session_state[f'feedback_viewed_{module_name}'] = True
                needs_review = apply_feedback(module_name)
                # print(needs_review)
                # if needs_review:
                st.info(f"Based on the tutor's feedback, you need to review the {module_name} module. Here is tutor feedback: {tutor_feedback}")

                notification_container.empty()

def app():
    # logging.debug("Entering app function in home.py")
    try:
        # Set page config
        student_details = get_student_details(st.session_state.email)
        modules = json.loads(student_details['modules'])
        st.set_page_config(page_title="AIML Tutor", layout="wide")
        st.markdown(custom_css, unsafe_allow_html=True)
        if 'email' not in st.session_state or st.session_state.user_type != 'student':
            st.warning("Please login as a student")
            st.session_state.page = 'login'
            st.rerun()
        st.session_state.student_details = student_details

        st.title(f"Welcome, {student_details['name']}!")    
        navigation()
        # logging.debug(f"Home: Modules retrieved: {modules}")
        
        # show_feedback_notifications(modules)
        # Header
        st.markdown('<div class="header"><span class="logo-title"> 🛡️ AIML Tutor </span><span class="user-info">{}</span></div>'.format(student_details['name']), unsafe_allow_html=True)
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
        # Main content
        st.title('All "Machine Learning" Courses')
        st.write(f"Your personalized course has {len(modules)} modules")
        cols = st.columns(3)
        
        # print( student_progress.get('Classification', {}), 'some progress')
        for idx, module in enumerate(modules):
            module_progress = module['progress']

            with cols[idx % 3]:
                module_number = idx + 1
                # module_status = get_module_status(module_number)

                # if module['status'] == 1 or (module['module_number'] == 1) or (module['module_number'] > 1 and check_module_completion(module['module_name'],student_details['email'])):
                #     button_disabled = False
                # else:
                #     button_disabled = True

                previous_module_completed = True if module_number == 1 else check_module_completion(modules[idx-1]['module_name'], student_details['email'])
        
                button_disabled = not (module['status'] == 1 or module_number == 1 or (module_number > 1 and previous_module_completed))
                
                print(f"Module {module_number} - {module['module_name']}:")
                print(f"  Status: {module['status']}")
                print(f"  Previous module completed: {previous_module_completed}")
                print(f"  Button disabled: {button_disabled}")

                st.markdown(f"""
                <div class="module">
                    <h3>{idx + 1}. {module['module_name']}</h3>
                    <div class="desc">{module['description']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(module_progress)
                if st.button(f"Start Module {module_number}", disabled=button_disabled):
                # if st.button(f"Start Module {module_number}"):
                    st.session_state.current_module = module
                    st.session_state.lesson = 0
                    st.session_state.page = 'lesson'
                    # logging.debug(f"Session state after setting module: {st.session_state}")
                    st.rerun()
    except Exception as e:
        print(f"Error in home app: {str(e)}")
        # logging.error(f"Error in home app: {str(e)}")
        st.error("An error occurred while loading the modules. Please try again later.")