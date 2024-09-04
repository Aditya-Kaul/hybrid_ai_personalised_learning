from multiapp import MultiApp
import streamlit as st
import home
import lesson
import login
import tutor_dashboard
# import sys

# import pysqlite3

# sys.modules['sqlite3'] = pysqlite3

# from google.cloud import storage
# BUCKET_NAME = 'streamlit_chromadb_bucket'
# storage_client = storage.Client()
# bucket = storage_client.bucket(BUCKET_NAME)

# def save_to_gcs(data, filename):
#     blob = bucket.blob(filename)
#     blob.upload_from_string(data)

# def load_from_gcs(filename):
#     blob = bucket.blob(filename)
#     return blob.download_as_text()

app = MultiApp()

# Add all your application here
app.add_app("Login", login.app)
app.add_app("Home", home.app)
app.add_app("Lesson", lesson.app)
app.add_app("Tutor",tutor_dashboard.app)

# The main app
app.run()

