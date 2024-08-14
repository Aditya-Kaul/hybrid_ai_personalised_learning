module = {
  "module_name": "The Machine Learning Landscape",
  "module_number": 1,
  "lessons": [
    {
      "name": "What Is Machine Learning?",
      "status": 0,
      "sub_topics":[]
    },
    {
      "name": "Why Use Machine Learning?",
      "status": 0,
       "sub_topics":[]
    },
    {
      "name": "Types of Machine Learning Systems",
      "status": 0,
      "sub_topics": [
        "Supervised/Unsupervised Learning",
        "Batch and Online Learning",
        "Instance-Based Versus Model-Based Learning"
      ]
    },
    {
      "name": "Main Challenges of Machine Learning",
      "status": 0,
      "sub_topics": [
        "Insufficient Quantity of Training Data",
        "Nonrepresentative Training Data",
        "Poor-Quality Data",
        "Irrelevant Features",
        "Overfitting the Training Data",
        "Underfitting the Training Data",
        "Stepping back"
      ]
    },
    {
      "name": "Testing and Validating",
      "status": 0,
      "sub_topics": [
        "Hyperparameter Tuning and Model Selection",
        "Data Mismatch"
      ]
    },
    {
      "name": "Exercises",
      "status": 0,
      "sub_topics": [
        "How would you define Machine Learning?",
        "Can you name four types of problems where ML shines?",
        "What is a labeled training set?",
        "What are the two most common supervised tasks?",
        "Can you name four of the main challenges in Machine Learning?",
        "What is out-of-core learning?",
        " If your model performs great on the training data but generalizes poorly to new instances, what is happening? Can you name three possible solutions?",
        "What is a test set, and why would you want to use it?",
        "What is the train-dev set, when do you need it, and how do you use it?",
        "What can go wrong if you tune hyperparameters using the test set?"
      ],
      "results": {},
      "tutor_feedback": ""
    }
  ],
  "description": "This module introduces the basics of machine learning, exploring different types, including supervised and unsupervised learning. It discusses the challenges of ML, such as overfitting and underfitting, and the importance of having a well-representative training set for successful model generalization.",
  "status": 0,
  "progress": 0
}

lesson_name = 'What Is Machine Learning?'
module_context = module['description']
lesson_context = next((lesson for lesson in module['lessons'] if lesson["name"] == lesson_name), None)

# print(lesson_context)

from new_config import reset_module_status

reset_module_status('aditya@example.com', 'The Machine Learning Landscape')