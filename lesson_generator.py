from config import modules_collection, textbook_collection, store_generated_lesson, get_generated_lesson, store_generated_quiz, get_generated_quiz
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

import json
import os
# api_key=os.getenv("GOOGLE_API_KEY")
api_key = 'AIzaSyDhx7RmV_n1YWz4elWDnSWqP4IuqYLxac0'
# # Set up Google API key
# genai.configure(api_key=api_key)
# genai.configure(api_key='AIzaSyDhx7RmV_n1YWz4elWDnSWqP4IuqYLxac0')


def generate_lesson(module_name, lesson_name):
        # Query modules collection for module context
    module_results = modules_collection.query(
        query_texts=[f"{module_name} - {lesson_name}"],
        n_results=1
    )
    
    module_context = ""
    if module_results['metadatas']:
        context = module_results['metadatas'][0]
        module_context = context[0]['description']

    # Query textbook collection for relevant chunks
    textbook_results = textbook_collection.query(
        query_texts=[f"{module_name} - {lesson_name}"],
        n_results=3
    )
    textbook_context = "".join(textbook_results['documents'][0][0])

    template = """
    You are an expert in Machine Learning, tasked with teaching concepts from the book 
    "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow" by Aurélien Géron.
    Use the following context to create a detailed lesson:

    Module Context:
    {module_context}

    Textbook Context:
    {textbook_context}

    Module: {module_name}
    Lesson: {lesson_name}

    Please provide a thorough explanation of the lesson topic, including:
    1. Key concepts and their definitions
    2. Practical examples or code snippets where applicable
    3. Any relevant mathematical formulas
    4. Connections to other related topics in machine learning

    Ensure the information is clear, accurate, and actionable for someone learning machine learning.
    """
    quiz_template = """
        Based on the following lesson content, generate a quiz with 5 multiple-choice questions.
        Each question should have 4 options with only one correct answer.

        Lesson Content:
        {lesson_content}

        Please generate the quiz in the following JSON format, and ONLY provide the JSON array without any additional text:
        [
            {{
                "question": "Question text here",
                "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                "correct_answer": "Correct option here"
            }}
        ]
    """
    prompt = PromptTemplate(
        input_variables=["module_context", "textbook_context", "module_name", "lesson_name"],
        template=template,
    )

    quiz_prompt = PromptTemplate(
        input_variables=["lesson_content"],
        template=quiz_template,
    )
    try:
        # Initialize the GoogleGenerativeAI model with required parameters
        get_gen_lesson = get_generated_lesson(module_name, lesson_name)
        get_gen_quiz = get_generated_quiz(module_name, lesson_name)
        if(lesson_name == 'Exercises'):
            return
        if(get_gen_lesson['metadatas']):
            print('in non gen')
            lesson_content = get_gen_lesson['documents'][0]
            return lesson_content, get_gen_quiz
            
        else:
            print('in lllm')
            llm = GoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.7, google_api_key=api_key)

            chain = prompt | llm | StrOutputParser()
            input_data = {
            "textbook_context": textbook_context,
            "module_name": module_name,
            "lesson_name": lesson_name,
            "module_context": module_context,
            }
            response_lesson_content = chain.invoke(input=input_data)
            quiz_input_data = {
                "lesson_content": response_lesson_content
            }
            quiz_chain = quiz_prompt | llm | StrOutputParser()
            quiz_content = quiz_chain.invoke(input=quiz_input_data)

            quiz_json = json.loads(quiz_content)
            store_generated_lesson(module_name, lesson_name, response_lesson_content)
            store_generated_quiz(module_name, lesson_name, quiz_content)
            print("SOMETHING IS HAPPENING -- 22")
            return response_lesson_content, quiz_json

    except Exception as e:
        print(f"Error occurred: {e}")
        raise
