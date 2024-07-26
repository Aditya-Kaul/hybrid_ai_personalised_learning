import streamlit as st
from config import get_modules, get_module_by_name, get_module_status, check_module_completion
import logging

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

</style>

"""

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


def app():
    # logging.debug("Entering app function in home.py")
    try:
        # Set page config
        st.set_page_config(page_title="Tutor AI", layout="wide")
        st.markdown(custom_css, unsafe_allow_html=True)

        navigation()
        modules = get_modules()
        # logging.debug(f"Home: Modules retrieved: {modules}")
        
        
        # Header
        st.markdown('<div class="header"><span class="logo-title"> 🛡️ Tutor AI </span><span class="user-info">reetadityakoul@gmail.com</span></div>', unsafe_allow_html=True)

        # Main content
        st.title('All "Machine Learning" Courses')
        st.write(f"Your personalized course has {len(modules)} modules")
        
        cols = st.columns(3)
        for idx, module in enumerate(modules):
            with cols[idx % 3]:
                module_number = idx + 1
                module_status = get_module_status(module_number)

                if module_status == 1 or (module_number == 1) or (module_number > 1 and check_module_completion(module_number - 1)):
                    status_text = "Unlocked"
                    button_disabled = False
                else:
                    status_text = "Locked"
                    button_disabled = True

                st.markdown(f"""
                <div class="module">
                    <h3>{idx + 1}. {module['module_name']}</h3>
                    <div class="desc">{module['description']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Start Module {module_number}", disabled=button_disabled):
                    st.session_state.current_module = module
                    st.session_state.lesson = 0
                    st.session_state.page = 'lesson'
                    # logging.debug(f"Session state after setting module: {st.session_state}")
                    st.rerun()
    except Exception as e:
        logging.error(f"Error in home app: {str(e)}")
        st.error("An error occurred while loading the modules. Please try again later.")