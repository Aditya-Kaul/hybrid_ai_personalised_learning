import streamlit as st
import json
import logging
logging.basicConfig(level=logging.DEBUG)

@st.experimental_dialog(f"Quiz")
def quiz():
    if 'quiz_questions' not in st.session_state:
        st.error("No quiz questions available. Please go back to the lesson and regenerate the content.")
        return
    
    quiz_questions = st.session_state.quiz_questions
    print(type(quiz_questions))
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False

    for i, question in enumerate(quiz_questions):
        st.subheader(f"Question {i+1}")
        st.write(question['question'])
        options = question['options']
        user_answer = st.radio(f"Select your answer for question {i+1}:", options, key=f"q{i}")
        st.session_state.user_answers[i] = user_answer

    if st.button("Submit Quiz"):
        score = 0
        for i, question in enumerate(quiz_questions):
            if st.session_state.user_answers.get(i) == question['correct_answer']:
                score += 1
        
        st.session_state.quiz_score = score
        st.session_state.quiz_submitted = True

    if st.session_state.get('quiz_submitted', False):
        st.write(f"Your score: {st.session_state.quiz_score}/{len(quiz_questions)}")
        if st.session_state.quiz_score >= len(quiz_questions) * 0.7:  # 70% passing score
            st.success("Congratulations! You passed the quiz.")
            # update_lesson_status(module_number, lesson_index, 1)
            if st.button("Continue to Next Lesson"):
                # st.session_state.lesson += 1
                # del st.session_state.quiz_questions
                del st.session_state.user_answers
                del st.session_state.quiz_submitted
                st.rerun()
        else:
            st.error("You didn't pass the quiz. Please review the lesson and try again.")
            if st.button("Retake Quiz"):
                del st.session_state.user_answers
                del st.session_state.quiz_submitted
                st.rerun()