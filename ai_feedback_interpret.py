from new_config import get_student_details, update_module_status, reset_lesson_status
from langchain_google_genai import GoogleGenerativeAI
import json

api_key = 'AIzaSyDjs6-jQNsmYFcqK54Mk5zsPDIBwJlk29E'

def interpret_feedback(feedback):
    interpretation_prompt = f"""
    As an AI tutor, interpret the following feedback for a student's performance:

    Tutor's feedback: {feedback}

    Based on this feedback, determine if the student needs to review the module.

    Provide your interpretation in Yes or No response.
    """

    llm = GoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.7, google_api_key=api_key)
    interpretation = llm(interpretation_prompt)

    return interpretation

def apply_feedback(module_name, email):
    student_details = get_student_details(email)
    modules = json.loads(student_details['modules'])
    
    for module in modules:
        if module['module_name'] == module_name:
            exercise_lesson = next((lesson for lesson in module['lessons'] if lesson['name'] == 'Exercises'), None)
            if exercise_lesson and 'tutor_feedback' in exercise_lesson:
                feedback = exercise_lesson['tutor_feedback']
                interpretation = interpret_feedback(feedback)
                needs_review = "Yes" in interpretation
                
                if needs_review:
                    # Reset module status to require review
                    # update_module_status(email, module_name, 0)
                    for lesson in module['lessons']:
                        reset_lesson_status(email, module_name, module['lessons'].index(lesson))
                
                return needs_review
    
    return False