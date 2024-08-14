import streamlit as st
# import logging

# logging.basicConfig(level=logging.DEBUG)
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
            print(f"setting page logggin")
            # logging.debug(f"setting page logggin")

        if st.session_state.page == 'login':
            app = [app for app in self.apps if app['title'] == 'Login'][0]
            print(f"INSIDE logggin")
            # logging.debug(f"INSIDE logggin")
        elif st.session_state.page == 'home':
            app = [app for app in self.apps if app['title'] == 'Home'][0]
            print(f"INSIDE HOME")
            # logging.debug(f"INSIDE HOME")
        elif st.session_state.page == 'lesson':
            app = [app for app in self.apps if app['title'] == 'Lesson'][0]
            print(f"INSIDE LESSON")
            # logging.debug(f"INSIDE ")
        else:
            app = [app for app in self.apps if app['title'] == 'Tutor'][0]
            print(f"INSIDE TUTOR")
            # logging.debug(f"INSIDE TUTOR")
        
        app['function']()
        
        # app['function']()