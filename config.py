import chromadb
from chromadb.utils import embedding_functions
import json
import ast
import re
import hashlib
from PyPDF2 import PdfReader
from langchain_community.document_loaders import PyMuPDFLoader
import fitz 

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
    students_collection.add(
        documents=[name],
        metadatas=[{
            "name": name,
            "email": email,
            "password": hashed_password,
            "progress": json.dumps({}),
            "generated_lessons": json.dumps([]),
            "completed_exercises": json.dumps([])
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
        # Ensure 'progress' exists, even if empty
        if 'progress' not in student_data:
            student_data['progress'] = {}
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

def authenticate_tutor(name, email, password):
    result = tutors_collection.get(
        where={"email": email}
    )
    if result['metadatas']:
        stored_password = result['metadatas'][0]['password']
        hashed_input_password = hashlib.sha256(password.encode()).hexdigest()
        return stored_password == hashed_input_password
    return False

def update_student_progress(email, module_name, lesson_name, status):
    student = get_student_details(email)
    if student:
        progress = student.get('progress', {})
        progress = json.loads(progress)
        if module_name not in progress:
            progress[module_name] = {}
        progress[module_name][lesson_name] = status
        students_collection.update(
            ids=[email],
            metadatas=[{"progress": json.dumps(progress)}]
        )
        return True
    return False

# def update_student_lesson_content(module_name, lesson_name, student_email):
#     student = get_student_details(student_email)
#     if student and f"{module_name}_{lesson_name}" in student.get('generated_lessons', {}):
#         return student['generated_lessons'][f"{module_name}_{lesson_name}"]
    
#     # Generate new content (you'll need to implement this function)
#     content = generate_lesson_content(module_name, lesson_name)
    
#     # Store the generated content for the student
#     students_collection.update(
#         ids=[student_email],
#         metadatas=[{
#             "generated_lessons": {
#                 **student.get('generated_lessons', {}),
#                 f"{module_name}_{lesson_name}": content
#             }
#         }]
#     )
    
#     return content

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

def update_module_status(module_number, status):
    modules_collection.update(
        ids=[f"module_{module_number}"],
        metadatas=[{"status": status}]
    )

def update_module_progress(module_number, progress):
    modules_collection.update(
        ids=[f"module_{module_number}"],
        metadatas=[{"progress": progress}]
    )

def get_module_status(module_number):
    result = modules_collection.get(ids=[f"module_{module_number}"])
    if result['metadatas']:
        return result['metadatas'][0].get('status', 0)
    return 0

def update_lesson_status(module_number, lesson_index, status):
    module = get_module_by_name(f"module_{module_number}")
    if module:
        lessons = module['lessons']
        if 0 <= lesson_index < len(lessons):
            lessons[lesson_index]['status'] = status
            modules_collection.update(
                ids=[f"module_{module_number}"],
                metadatas=[{"lessons": json.dumps(lessons),}]
            )

def reset_lesson_status(module_number, status):
    module = get_module_by_name(f"module_{module_number}")
    if module:
        for lesson in module['lessons']:
            lesson['status'] = status
        modules_collection.update(
                ids=[f"module_{module_number}"],
                metadatas=[{"lessons": json.dumps(module['lessons']),}] )


def update_module_feedback(module_name, feedback):
    print(module_name)
    print('in config for Feedbacl', feedback)
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

def check_module_completion(module_number):
    module = get_module_by_name(f"module_{module_number}")
    if module:
        lessons = module['lessons']
        return all(lesson['status'] in (1, '1') for lesson in lessons)
    return False

def get_module_exercise(module_name):
    mex = module_exercises_collection.get(
        ids=[f"exercises_{module_name}"]
    )
    return mex

def store_module_exercise(module_name, new_result):
    entry_id = f"exercises_{module_name}"
    
    existing_entry = module_exercises_collection.get(ids=[entry_id])
    
    if existing_entry['ids']:
        results = json.dumps(new_result)
        
        module_exercises_collection.update(
            ids=[f"exercises_{module_name}"],
            metadatas=[{"results": results}]
        )
    else:
        print(f"Entry for module '{module_name}' not found.")
        

# Initialization code
pdf_path = 'data/Text Book/Hands-On Machine Learning_Text_Book.pdf'

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
    print('from config file')
    modules = textbook_collection.get()
    print(f"Retrieved {len(modules)} modules")