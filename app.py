__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from multiapp import MultiApp
import streamlit as st
import home
import lesson
import login
import tutor_dashboard

app = MultiApp()

# Add all your application here
app.add_app("Login", login.app)
app.add_app("Home", home.app)
app.add_app("Lesson", lesson.app)
app.add_app("Tutor",tutor_dashboard.app)

# The main app
app.run()

