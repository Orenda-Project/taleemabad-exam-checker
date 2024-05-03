import json

import google.generativeai as genai

extracted_messages = process_images.data.extracted_exam
answer_key_extracted = process_images.data.extracted_answer_key

gemini_api_key = "gemini_api_key"

genai.configure(api_key=gemini_api_key)
model_gprov = genai.GenerativeModel("gemini-1.5-pro-latest")


def get_completion(extracted_messages):
    prompt = f"""
- RESPOND ONLY IN JSON, format defined below. You are an assessment checker. The following is a test attempted by a student. The test can have mutiple formats that may include choose the correct statement, multi choise questions, answers needed to be written in paragraph. Identify the type of each question and check if the student has given right answers or not. If you are unable to find answers in the provided data, that means the student did not write the answers, deduct marks in such scenerio and grade it accordingly. DO NOT MISS ANYTHING FROM THE DATA.

- "Attempted Exam Objects Description" (given below in triple backticks) contains OCR and description of any exam attempted by the student provided for all the answers in the attempted exam. Make sure to check "Attempted Exam Objects Description" data if answer needs to be of coloring or drawing, choosing the correct option or match the column or any other type of question. Do check it for OCR as well for better understanding. Check "Attempted Exam Objects" data for all the information of the exam, do not miss any question/answer in your response, not even a single one. Everything is present in this data regarding the exam. Do loose marking for lower grade and strict marking for grades above 6.

- "Answer Sheet" data (given below in triple backticks) is not student's answers, I am providing it for your reference to check if the student's answers match with it. "Answer Sheet" is optional and is uploaded by the teacher which contains all the correct answers to the questions according to which you need to check the exam. NOTE: THESE ARE NOT STUDENT WRITTEN ANSWERS. Compare these answers with the student's answers and deduct marks if the answers don't match. If "Answer Sheet" is not provided, grade the test according to your own understanding.

There can be subjective questions with separate question paper, identify the type of exam accordingly. The student's answers might be attempted separately.

- Identify how many questions are there. Grade the test and write total marks obtained after calculation. The student could have choosen correct answers using ticks or encircling the correct option, or might have filled a fill in the blank sentence. There can be any type of questions, check them accordingly. DO NOT miss any question in the whole exam. Read the data carrefully. Do not miss anything from the data being provided to you, be careful. Carefully allot the final obtained marks after summing all the marks of the correct answers. There can be multiple student's exams in the data given to you. Do check them all accordingly. If the exams are of small grades, allot marks for small grammatical errors or spelling mistakes. If the conxt is right in the answer, provide full marks for loaw grade students. SUM UP THE OBTAINED MARKS CORRECTLY.

- Provide reasoning for the marks deducted and the marks alloted for each question and the whole exam.

- Return the response in the JSON in the format given below in triple backticks.


Attempted Exam Objects Description:
```
{extracted_messages}
```

Answer Sheet:
```
{answer_key_extracted}
```


JSON Response Format:
```
[

    {{
        "student_name": "student name",
        "class": "class name",
        "subject": "subject name",
        "question_answers": [
            {{
                "question": "question statement",
                "answer": "answer statement",
                "marks": "question total marks",
                "obtained_marks": "obtained marks"
                "reasoning": "reasoning for the marks deducted and the marks alloted"
            }},
            {{
                "question": "question statement",
                "answer": "answer statement",
                "marks": "question total marks",
                "obtained_marks": "obtained marks"
                "reasoning": "reasoning for the marks deducted and the marks alloted"
            }}
        ],
        "total_marks": "total marks",
        "obtained_marks": "obtained marks"
        "reasoning": "reasoning for the marks deducted and the marks alloted"
    }},

    {{
        "student_name": "student name",
        "class": "class name",
        "subject": "subject name",
        "question_answers": [
            {{
                "question": "question statement",
                "answer": "answer statement",
                "marks": "question total marks",
                "obtained_marks": "obtained marks"
                "reasoning": "reasoning for the marks deducted and the marks alloted"
            }},
            {{
                "question": "question statement",
                "answer": "answer statement",
                "marks": "question total marks",
                "obtained_marks": "obtained marks"
                "reasoning": "reasoning for the marks deducted and the marks alloted"
            }}
        ],
        "total_marks": "total marks",
        "obtained_marks": "obtained marks"
        "reasoning": "reasoning for the marks deducted and the marks alloted"
    }}
]
```"""

    response = model_gprov.generate_content([prompt])

    return response.text


response = get_completion(extracted_messages)
try:
    response = response[response.find("[") : response.rfind("]") + 1]
    response = json.loads(response)
except Exception as e:
    print(response)
    raise Exception(e)

print(response)
return response
