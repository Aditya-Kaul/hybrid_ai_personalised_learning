import chromadb
from chromadb.utils import embedding_functions
import json
import ast
import re
import hashlib
from PyPDF2 import PdfReader
from langchain_community.document_loaders import PyMuPDFLoader
import fitz 
import streamlit as st
import os

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")

# Use the default embedding function
embedding_function = embedding_functions.DefaultEmbeddingFunction()

# Collections
modules_collection = client.get_or_create_collection("machine_learning_modules", embedding_function=embedding_function)
textbook_collection = client.get_or_create_collection("textbook_collections", embedding_function=embedding_function)
lessons_collection = client.get_or_create_collection("generated_lessons", embedding_function=embedding_function)
module_exercises_collection = client.get_or_create_collection("module_exercises", embedding_function=embedding_function)
students_collection = client.get_or_create_collection("students", embedding_function=embedding_function)
tutors_collection = client.get_or_create_collection("tutors", embedding_function=embedding_function)

def register_student(name, email, password):
    existing_student = students_collection.get(
        where={"email": email}
    )
    if existing_student['metadatas']:
        return False  # Student already exists

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    with open('structure_student.json', 'r') as f:
        modules = json.load(f)
    # student_metrics =  {
    #         "login_frequency": 0,
    #         "time_on_platform": 0,
    #         "recent_performances": [],
    #         "overall_engagement_level": 0
    #     }
    students_collection.add(
        documents=[name],
        metadatas=[{
            "name": name,
            "email": email,
            "password": hashed_password,
            "modules": json.dumps(modules),
            # "student_metrics": json.dumps(student_metrics)
        }],
        ids=[email]
    )
    return True

def authenticate_student(email, password):
    result = students_collection.get(where={"email": email})
    if result['metadatas']:
        stored_password = result['metadatas'][0]['password']
        return stored_password == hashlib.sha256(password.encode()).hexdigest()
    return False

def get_student_details(email):
    result = students_collection.get(where={"email": email})
    if result['metadatas']:
        student_data = result['metadatas'][0]
        return student_data
    return None

def create_tutor(name, email, password):
    # Check if tutor already exists
    existing_tutor = tutors_collection.get(
        where={"email": email}
    )
    if existing_tutor['metadatas']:
        return False  # Tutor already exists

    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Add the new tutor to the collection
    tutors_collection.add(
        documents=[name],
        metadatas=[{
            "name": name,
            "email": email,
            "password": hashed_password
        }],
        ids=[email]
    )
    return True

def authenticate_tutor(email, password):
    result = tutors_collection.get(
        where={"email": email}
    )
    if result['metadatas']:
        stored_password = result['metadatas'][0]['password']
        hashed_input_password = hashlib.sha256(password.encode()).hexdigest()
        return stored_password == hashed_input_password
    return False


def submit_exercise(email, module_id, exercise_id, submission):
    module_exercises_collection.add(
        documents=[json.dumps(submission)],
        metadatas=[{
            "student_email": email,
            "module_id": module_id,
            "exercise_id": exercise_id,
            "status": "submitted"
        }],
        ids=[f"{email}_{module_id}_{exercise_id}"]
    )

def get_student_exercises(email):
    return module_exercises_collection.get(where={"student_email": email})['metadatas']


def safe_eval(s):
    try:
        return ast.literal_eval(s)
    except:
        return s

def clean_json_string(s):
    # Remove any leading/trailing whitespace and quotes
    s = s.strip().strip('"\'')
    # Replace any single quotes with double quotes for valid JSON
    s = re.sub(r"(?<!\\)'", '"', s)
    # Remove any leading/trailing brackets if they're not balanced
    if s.startswith('[') and not s.endswith(']'):
        s = s[1:]
    if s.endswith(']') and not s.startswith('['):
        s = s[:-1]
    return s

def parse_quiz_content(quiz_content):
    # First, try to parse the string as-is
    try:
        quiz_json = json.loads(quiz_content)
        if isinstance(quiz_json, str):
            quiz_json = safe_eval(quiz_json)
        return quiz_json
    except json.JSONDecodeError:
        pass

    # If that fails, try to extract JSON-like content
    json_match = re.search(r'\[[\s\S]*\]', quiz_content)
    if json_match:
        quiz_json_str = json_match.group(0)
        try:
            quiz_json = json.loads(quiz_json_str)
            if isinstance(quiz_json, str):
                quiz_json = safe_eval(quiz_json)
            return quiz_json
        except json.JSONDecodeError:
            pass

def chunk_pdf(pdf_path, chunk_size=1000):
    reader = PdfReader(pdf_path)
    chunks = []
    current_chunk = ""
    for page in reader.pages:
        text = page.extract_text()
        words = text.split()
        for word in words:
            if len(current_chunk) + len(word) > chunk_size:
                chunks.append(current_chunk.strip())
                current_chunk = word + " "
            else:
                current_chunk += word + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def pdf_loader(pdf_path):
    loader = PyMuPDFLoader(pdf_path)
    pages = loader.load()

    doc = fitz.open(pdf_path)
    
    content = []
    for i, page in enumerate(doc):
        text = pages[i].page_content
        images = page.get_images()
        content.append({"text": text, "images": images, "page": i+1})
    
    doc.close()
    return content

def load_data_to_chroma():
    with open('structure.json', 'r') as f:
        modules = json.load(f)
    
    for module in modules:
        doc = {
            "module_name": module["module_name"],
            "module_number": str(module["module_number"]),
            "description": module["description"],
            "lessons": json.dumps(module["lessons"]),
            "status": module["status"],
            "progress": 0
        }
        
        modules_collection.add(
            documents=[doc["description"]],
            metadatas=[doc],
            ids=[f"module_{module['module_number']}"]
        )
    
def load_module_exercises():
    with open('exercises.json', 'r') as f:
        e_modules = json.load(f)
    
    for module in e_modules:
        doc = {
            "module_name": module["module_name"],
            "module_number": module['module_number'],
            "exercises": json.dumps(module["exercises"])
        }
        
        module_exercises_collection.add(
            documents=[doc["module_name"]],
            metadatas=[doc],
            ids=[f"exercises_{module['module_name']}"]
        )

def load_textbook_to_chroma(pdf_path):
    chunks = chunk_pdf(pdf_path)
    for i, chunk in enumerate(chunks):
        textbook_collection.add(
            documents=[chunk],
            metadatas=[{"source": "textbook", "chunk_id": i}],
            ids=[f"textbook_chunk_{i}"]
        )

def load_textbook_to_chroma(pdf_path):
    chunks = pdf_loader(pdf_path)
    for i, chunk in enumerate(chunks):
        textbook_collection.add(
            documents=[chunk['text']],
            metadatas=[{"source": "textbook", "image": json.dumps(chunk['images']),"page": chunk["page"], }],
            ids=[f"textbook_chunk_{i}"]
        )

def store_generated_lesson(module_name, lesson_name, content, email):
    lessons_collection.add(
        documents=[content],
        metadatas=[{"type": "lesson", "module_name": module_name, "lesson_name": lesson_name}],
        ids=[f"{email}_{module_name}_{lesson_name}"]
    )


def get_generated_lesson(module_name, lesson_name, email):
    lc = lessons_collection.get(ids=[f"{email}_{module_name}_{lesson_name}"])
    return lc

def store_generated_quiz(module_name, lesson_name, quiz_content):
    lessons_collection.add(
        documents=[json.dumps(quiz_content)],
        metadatas=[{"type": "quiz", "module_name": module_name, "lesson_name": lesson_name}],
        ids=[f"quiz_{module_name}_{lesson_name}"]
    )

def get_generated_quiz(module_name, lesson_name):
    quiz_result = lessons_collection.get(
        ids=[f"quiz_{module_name}_{lesson_name}"]
    )
    if quiz_result['documents']:
        quiz_content = parse_quiz_content(quiz_result['documents'][0])
        return quiz_content
    else:
        return quiz_result

def get_modules():
    results = modules_collection.get()
    modules = []
    for metadata in results['metadatas']:
        module = metadata.copy()
        module['lessons'] = json.loads(module['lessons'])
        modules.append(module)
    sorted_modules = sorted(modules, key=lambda m: int(m['module_number']))
    return sorted_modules

def get_module_by_name(module_name):
    results = modules_collection.get(
        ids=[module_name]
    )

    if results['metadatas']:
        module = results['metadatas'][0].copy()
        module['lessons'] = json.loads(module['lessons'])
        return module
    return None

def update_module_status(module_name, email):
    result = students_collection.get(
        ids=[email]
    )
    student_data = result['metadatas'][0]
    modules = json.loads(student_data['modules'])
    for module in modules:
        if module['module_name'] == module_name:
            module['status'] = 1
            break
 
    students_collection.update(
        ids=[email],
        metadatas=[{"modules": json.dumps(modules)}]
    )

def get_module_status(module_number):
    # not required
    result = modules_collection.get(ids=[f"module_{module_number}"])
    if result['metadatas']:
        return result['metadatas'][0].get('status', 0)
    return 0

def update_lesson_status(email, module_name, lesson_index, status):
    student_details = get_student_details(email)
    modules = json.loads(student_details['modules'])
    for module in modules:
        if module['module_name'] == module_name:
            module['lessons'][lesson_index]['status'] = status
            completed_lessons = sum(1 for lesson in module['lessons'] if lesson['status'] == 1)
            module['progress'] = completed_lessons / len(module['lessons'])
            break
    students_collection.update(
        ids=[email],
        metadatas=[{"modules": json.dumps(modules)}]
    )

# def update_lesson_status(email, module_name, lesson_index, status):
#     try:
#         student_details = get_student_details(email)
#         if not student_details:
#             print(f"No student found with email: {email}")
#             return False

#         modules = json.loads(student_details['modules'])

#         for module in modules:
#             if module['module_name'] == module_name:
#                 # Update the lesson status
#                 if 0 <= lesson_index < len(module['lessons']):
#                     module['lessons'][lesson_index]['status'] = status
                    
#                     # Calculate new module progress
#                     completed_lessons = sum(1 for lesson in module['lessons'] if lesson['status'] == 1)
#                     module['progress'] = (completed_lessons / len(module['lessons'])) * 100
                    
#                     # Update the student's record in the database
#                     students_collection.update(
#                         ids=[email],
#                         metadatas=[{"modules": json.dumps(modules)}]
#                     )
#                     return True
#                 else:
#                     print(f"Invalid lesson index: {lesson_index}")
#                     return False
        
#         print(f"Module not found: {module_name}")
#         return False

#     except Exception as e:
#         print(f"Error updating lesson status: {str(e)}")
#         return False
                    


def reset_lesson_status(module_number, status):
    module = get_module_by_name(f"module_{module_number}")
    if module:
        for lesson in module['lessons']:
            lesson['status'] = status
        modules_collection.update(
                ids=[f"module_{module_number}"],
                metadatas=[{"lessons": json.dumps(module['lessons']),}] )

def reset_module_status(email, module_name):
    try:
        # Get the student's details
        student_details = get_student_details(email)
        if not student_details:
            print(f"No student found with email: {email}")
            return False

        # Parse the modules JSON
        modules = json.loads(student_details['modules'])

        # Find the correct module
        for module in modules:
            if module['module_name'] == module_name:
                # Reset module status and progress
                module['status'] = 0
                module['progress'] = 0
                
                # Reset all lessons within the module
                for lesson in module['lessons']:
                    lesson['status'] = 0

                # Update the student's record in the database
                students_collection.update(
                    ids=[email],
                    metadatas=[{"modules": json.dumps(modules)}]
                )
                return True
        return False

    except Exception as e:
        print(f"Error resetting module status: {str(e)}")
        return False
    
def reset_lesson_status(email, module_name, lesson_index):
    try:
        # Get the student's details
        student_details = get_student_details(email)
        if not student_details:
            print(f"No student found with email: {email}")
            return False

        # Parse the modules JSON
        modules = json.loads(student_details['modules'])

        # Find the correct module
        for module in modules:
            if module['module_name'] == module_name:
                # Reset the lesson status
                if 0 <= lesson_index < len(module['lessons']):
                    module['lessons'][lesson_index]['status'] = 0
                    
                    # Recalculate module progress
                    completed_lessons = sum(1 for lesson in module['lessons'] if lesson['status'] == 1)
                    module['progress'] = completed_lessons / len(module['lessons'])
                    
                    # Update the student's record in the database
                    students_collection.update(
                        ids=[email],
                        metadatas=[{"modules": json.dumps(modules)}]
                    )
                    print(f"Lesson {lesson_index} in module '{module_name}' has been reset for student {email}")
                    return True
                else:
                    print(f"Invalid lesson index: {lesson_index}")
                    return False
        
        print(f"Module not found: {module_name}")
        return False

    except Exception as e:
        print(f"Error resetting lesson status: {str(e)}")
        return False
    

def update_module_feedback(module_name, feedback):
    entry_id = f"exercises_{module_name}"
    
    existing_entry = module_exercises_collection.get(ids=[entry_id])
    
    if existing_entry['ids']:
        module_exercises_collection.update(
            ids=[entry_id],
            metadatas=[{"tutor_feedback": feedback}]
        )

        mx = module_exercises_collection.get(
            ids=[entry_id]
        )
        print(mx)

def check_module_completion(module_name,email):
    student_details = get_student_details(email)
    
    modules = json.loads(student_details['modules'])
    # lessons = {}
    print(module_name)
    for module in modules:
        if module['module_name'] == module_name:
            lessons = module['lessons']
            break      
   
    return all(lesson['status'] in (1, '1') for lesson in lessons)

def get_module_exercise(module_name):
    #not needed
    mex = module_exercises_collection.get(
        ids=[f"exercises_{module_name}"]
    )
    return mex

def store_module_exercise(module_name,new_result,email):
    print(new_result)
    student_details = get_student_details(email)
    modules = json.loads(student_details['modules'])
    for module in modules:
        if module['module_name'] == module_name:
            for lesson in module['lessons']:
                if lesson["name"] == 'Exercises': 
                    lesson['results'] = new_result  
            print(module)
            break
            
    students_collection.update(
        ids=[email],
        metadatas=[{"modules": json.dumps(modules)}]
    )

# Initialization code
pdf_path = '/Users/adityakoul/Documents/ml kb/Text Book/Hands-On Machine Learning.pdf'

# if modules_collection.count() == 0:
#     print('creating json data')
#     load_data_to_chroma()

if textbook_collection.count() == 0:
    print('creating textbook data')
    load_textbook_to_chroma(pdf_path)

# if module_exercises_collection.count() == 0:
#     print('creating module exercise data')
#     load_module_exercises()

if __name__ == "__main__":
    print('from new_config file')
    modules = textbook_collection.get()
    print(f"Retrieved {len(modules)} modules")