import streamlit as st
import logging

logging.basicConfig(level=logging.DEBUG)
class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({
            "title": title,
            "function": func
        })

    def run(self):
        if 'page' not in st.session_state:
            st.session_state.page = 'login'
            logging.debug(f"setting page logggin")

        if st.session_state.page == 'login':
            app = [app for app in self.apps if app['title'] == 'Login'][0]
            logging.debug(f"INSIDE logggin")
        elif st.session_state.page == 'home':
            app = [app for app in self.apps if app['title'] == 'Home'][0]
            logging.debug(f"INSIDE HOME")
        elif st.session_state.page == 'lesson':
            app = [app for app in self.apps if app['title'] == 'Lesson'][0]
            logging.debug(f"INSIDE LESSON")
        else:
            app = [app for app in self.apps if app['title'] == 'Tutor'][0]
            logging.debug(f"INSIDE TUTOR")
        
        app['function']()
        
        # app['function']()