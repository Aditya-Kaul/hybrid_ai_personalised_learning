from config import get_module_by_name, get_module_exercise, reset_lesson_status, update_module_progress, update_module_status

from langchain_google_genai import GoogleGenerativeAI
api_key = 'AIzaSyDjs6-jQNsmYFcqK54Mk5zsPDIBwJlk29E'

def interpret_feedback(module_name):
    exercise_data = get_module_exercise(module_name)
    feedback = exercise_data['metadatas'][0].get('tutor_feedback', '')
    print('FEEEDBACK',feedback)
    # Use GPT to interpret the feedback
    interpretation_prompt = f"""
    As an AI tutor, interpret the following feedback for a student's performance in the '{module_name}' module:

    Tutor's feedback: {feedback}

    Based on this feedback, If the student needs to review the module.

    Provide your interpretation in Yes or No response.
    """

    # Use your existing GPT setup to get the interpretation
    llm = GoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.7, google_api_key=api_key)
    interpretation = llm(interpretation_prompt)

    return interpretation

def apply_feedback(module_name):
    interpretation = interpret_feedback(module_name)
    print(interpretation)
    exercise_data = get_module_exercise(module_name)
    module_number = exercise_data['metadatas'][0]['module_number']
    module_details = get_module_by_name(f'module_{module_number}')
    # Extract key information from the interpretation
    needs_review = "Yes" in interpretation
    if needs_review:
        # Reset module status to require review
        update_module_status(module_name, 0)
        update_module_progress(module_name, 0)
        reset_lesson_status(module_number,0)

    return needs_review