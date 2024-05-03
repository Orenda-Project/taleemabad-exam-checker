import base64
import io

import google.generativeai as genai
import requests
from PIL import Image

image_urls = split_pdf_or_tiff_to_images.data.image_urls
answer_image_urls = split_pdf_or_tiff_to_images.data.answer_image_urls


gemini_api_key = "gemini_api_key"

genai.configure(api_key=gemini_api_key)
model_gprov = genai.GenerativeModel("gemini-1.5-pro-latest")


def encode_image(image_url):
    """
    Download and create a PIL image object
    """
    # get the image
    response = requests.get(image_url)
    image_bytes = io.BytesIO(response.content)
    # open the image with PIL
    return Image.open(image_bytes)


def process_image(image_url, prompt):
    image = encode_image(image_url)
    response = model_gprov.generate_content([prompt, image])
    return response.text


# Prompt for main image/document
main_image_prompt = """
This is an exam attempted by a student. Identify student's answer without telling if it's right or wrong. Perform OCR and Identify total marks of each question(mentioned on the image). Carefully check mcq's since the options can be circled or marked in any form by the student. DO NOT MISS ANYTHING FROM THE IMAGE. Describe the objects present within the image and do OCR on the given image, tell me exactly what the text is saying. I want the whole page to be displayed the way it is in textual form with student answers. Describe whatever else is present on the image other than text and treat the image as an exam paper. It can have tables, diagrams, mcq's, match the columns, coloured pictures etc. Do tell where the objects are located. Identify the colours of the objects. If it's a labelled diagram, do tell if the labels are correctly labelled or not. DO NOT WRITE ANYTHING ELSE if there are no objects. Do mention if the questions are unattempted. Identify all the answers after the question given by the student which can be encircled options, match the columns, writing the answers, drawing, colouring, etc. DO NOT TELL WHETHER THE ANSWER IS CORRECT OR NOT FOR ALL QUESTIONS, JUST PROVIDE DEFINITE OCR. I only need the whole exam in textual form the way it is in the image. DO NOT WRITE ANYTHING BY YOURSELF. Carefully check which options are chosen by the student. Do not grade the exam. Please be very careful with the multi choice questions. Student's marks depend on you! Do not right true answers on your own in any form. Write student written answer for every attempted question without mentioning correctness of it. Identify all parts of a question, please don't miss anything.
"""
# process_exam_images
exam_responses = []
for image_url in image_urls:
    response = process_image(image_url=image_url, prompt=main_image_prompt)
    exam_responses.append(response)


# Different prompt for answer key
answer_key_prompt = """
This is an Answer Key. Perform OCR on the image and provide the text content. Focus on identifying and transcribing any text, numbers, or symbols present in the image. Describe the layout and structure of the content, such as headers, bullet points, numbered lists, diagrams etc.
"""
# process answer images
answer_responses = []
for image_url in answer_image_urls:
    response = process_image(image_url=image_url, prompt=answer_key_prompt)
    answer_responses.append(response)

return {
    "extracted_exam": exam_responses,
    "extracted_answer_key": answer_responses,
}
