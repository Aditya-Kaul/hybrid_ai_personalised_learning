from new_config import modules_collection, textbook_collection, store_generated_lesson, get_generated_lesson, store_generated_quiz, get_generated_quiz
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

import json
import os
import traceback
# api_key=os.getenv("GOOGLE_API_KEY")
api_key = 'AIzaSyDjs6-jQNsmYFcqK54Mk5zsPDIBwJlk29E'
# # Set up Google API key
# genai.configure(api_key=api_key)
# genai.configure(api_key='AIzaSyDhx7RmV_n1YWz4elWDnSWqP4IuqYLxac0')


def get_or_generate_lesson(module, lesson_name, email):

    get_gen_lesson = get_generated_lesson(module['module_name'], lesson_name,email)
    get_gen_quiz = get_generated_quiz(module['module_name'], lesson_name)
    
    if(lesson_name == 'Exercises'):
        return
    if(get_gen_lesson['metadatas']):
        lesson_content = get_gen_lesson['documents'][0]
        # print(get_gen_quiz)
        return lesson_content, get_gen_quiz

    module_context = ""
    if module:
        module_context = module['description']
        lesson_context = next((lesson for lesson in module['lessons'] if lesson["name"] == lesson_name), None)
        # subtopics_str = "\n".join(f"- {topic}" for topic in sub_topics)
    # Query textbook collection for relevant chunks
    textbook_results = textbook_collection.query(
        query_texts=[f"{module['module_name']} - {lesson_name}"],
        n_results=3
    )
    textbook_context = "".join(textbook_results['documents'][0][0])

    # textbook_context = ""
    # image_info = []

    # for doc, metadata in zip(textbook_results['documents'][0], textbook_results['metadatas'][0]):
    #     textbook_context += doc + "\n"
        
    #     # Extract image information
    #     images = json.loads(metadata.get('image', '[]'))
    #     page_num = metadata.get('page', 0)
    #     for idx, img in enumerate(images):
    #         image_info.append(f"Figure {len(image_info) + 1}: Image on page {page_num + 1}")

    # image_context = "\n".join(image_info)

    template = """
    You are an expert in Machine Learning, tasked with teaching concepts from the book "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow" by Aurélien Géron.
    Use the following context to create a comprehensive and engaging lesson:

    Module Context: {module_context}
    Textbook Context: {textbook_context}
    Module: {module_name}
    Lesson: {lesson_name}
    {subtopics_section}

    Instructions:
    Please provide a thorough and in-depth explanation of the lesson topic, {subtopics_instruction} including:

    1. Key concepts and their definitions:
    - Explain each concept in detail, using analogies and real-world examples to enhance understanding
    - Highlight the importance of each concept in the broader context of machine learning

    2. Practical examples or code snippets:
    - Provide detailed, step-by-step explanations of any code snippets
    - Include comments within the code to explain the purpose of each line or block
    - Offer variations of the code to demonstrate different approaches or scenarios

    3. Relevant mathematical formulas:
    - Break down each formula, explaining the purpose and meaning of each component
    - Provide the intuition behind the mathematics
    - Show how to apply the formulas in practical scenarios

    4. Connections to other related topics in machine learning:
    - Explain how this lesson fits into the broader landscape of machine learning
    - Discuss potential applications of the concepts in real-world projects
    - Highlight any prerequisites or foundational knowledge needed for this lesson

    5. Common pitfalls and misconceptions:
    - Address frequent misunderstandings related to the topic
    - Provide tips on how to avoid common errors when implementing these concepts

    6. Historical context and recent developments:
    - Briefly discuss the evolution of the concepts covered in the lesson
    - Mention any recent advancements or research related to the topic

    7. Additional resources:
    - Recommend supplementary reading materials, research papers, or online courses
    - Suggest tools or libraries that are commonly used in relation to the topic

    8. Ethical considerations:
    - Discuss any ethical implications or considerations related to the use of these machine learning techniques

    {subtopics_coverage}

    Ensure the information is clear, accurate, and actionable for someone learning machine learning. Use a mix of text, bullet points, and code blocks to present the information in an easily digestible format. Encourage critical thinking and provide opportunities for students to reflect on the material.
    """
    subtopics_section_with_topics = """
    Lesson Subtopics:
    {subtopics_list}
    """

    subtopics_instruction_with_topics = "covering all the listed subtopics,"

    subtopics_coverage_with_topics = """
    For each of the listed subtopics, ensure that you:
    - Provide a clear and concise definition or explanation
    - Explain its importance in the context of the overall lesson and module
    - If applicable, provide examples or use cases specific to that subtopic
    - Highlight any connections to other concepts within the module or in machine learning in general
    """

    subtopics_instruction_without_topics = ""

    subtopics_coverage_without_topics = """
    In your explanation, make sure to:
    - Identify and explain the main concepts related to this lesson
    - Provide clear and concise definitions for key terms
    - Explain the importance of these concepts in the context of the overall lesson and module
    - Provide relevant examples or use cases to illustrate the concepts
    - Highlight connections between these concepts and other topics within the module or in machine learning in general
    """
    quiz_template = """
        Based on the following lesson content, generate a quiz with 5 multiple-choice questions.
        Each question should have 4 options with only one correct answer.

        Lesson Content:
        {lesson_content}

        Please generate the quiz in the following JSON format. 
        IMPORTANT: Provide ONLY the JSON array without any additional text, explanations, or formatting.
        The response should start with '[' and end with ']':
        [
            {{
                "question": "Question text here",
                "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                "correct_answer": "Correct option here"
            }}
        ]
    """
   
    # prompt = PromptTemplate(
    #     input_variables=["module_context", "textbook_context", "image_context", "module_name", "lesson_name"],
    #     template=template,
    # )

    if 'subtopics' in lesson_context:
        subtopics_list = "\n".join(f"- {topic}" for topic in lesson_context['subtopics'])
        subtopics_section = subtopics_section_with_topics.format(subtopics_list=subtopics_list)
        subtopics_instruction = subtopics_instruction_with_topics
        subtopics_coverage = subtopics_coverage_with_topics
        
    else:
        subtopics_section = ""
        subtopics_instruction = subtopics_instruction_without_topics
        subtopics_coverage = subtopics_coverage_without_topics

    formatted_template = template.format(
        module_context=module_context,
        textbook_context=textbook_context,
        module_name=module['module_name'],
        lesson_name=lesson_name,
        subtopics_section=subtopics_section,
        subtopics_instruction=subtopics_instruction,
        subtopics_coverage=subtopics_coverage
    )

    prompt = PromptTemplate(
        input_variables=["module_context", "textbook_context", "module_name",
                        "lesson_name","subtopics_section", "subtopics_instruction", "subtopics_coverage"],
        template=formatted_template,
    )

    quiz_prompt = PromptTemplate(
        input_variables=["lesson_content"],
        template=quiz_template,
    )
    try:
        print('in lllm')
        llm = GoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.7, google_api_key=api_key)
        chain = prompt | llm | StrOutputParser()
        
        # input_data = {
        # "textbook_context": textbook_context,
        # "module_name": module_name,
        # "lesson_name": lesson_name,
        # "module_context": module_context,
        # "image_context": image_context
        # }
        
        input_data = {
        "textbook_context": textbook_context,
        "module_name": module['module_name'],
        "lesson_name": lesson_name,
        "module_context": module_context
        }
        # print('is there a problem++++++++++ again', input_data)
        response_lesson_content = chain.invoke(input=input_data)
        # print(response_lesson_content)
        quiz_input_data = {
            "lesson_content": response_lesson_content
        }
        quiz_chain = quiz_prompt | llm | StrOutputParser()
        quiz_content = quiz_chain.invoke(input=quiz_input_data)
        print(quiz_content, type(quiz_content))
        quiz_json = json.loads(quiz_content) 
            
        store_generated_lesson(module['module_name'], lesson_name, response_lesson_content, email)
        store_generated_quiz(module['module_name'], lesson_name, quiz_content)
        return response_lesson_content, quiz_json

    except Exception as e:
        print(f"Error occurred: {e}")
        print(traceback.format_exc())
        raise


import streamlit as st
import fitz

def display_lesson_with_images(lesson_content, pdf_path):
    # Split the lesson content into paragraphs
    paragraphs = lesson_content.split('\n\n')
    
    doc = fitz.open(pdf_path)
    
    for paragraph in paragraphs:
        # Check if the paragraph references a figure
        if "Figure" in paragraph and "page" in paragraph.lower():
            st.write(paragraph)
            
            # Extract the page number
            page_num = int(paragraph.split("page")[1].split()[0].strip()) - 1
            
            # Get the page
            page = doc[page_num]
            
            # Get images on the page
            images = page.get_images()
            
            if images:
                # For simplicity, we'll just display the first image on the page
                img = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_bytes = img.tobytes()
                st.image(img_bytes, caption=f"Image from page {page_num + 1}")
        else:
            st.write(paragraph)
    
    doc.close()