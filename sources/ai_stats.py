import os
import time
import PIL.Image
import re
import uuid
from google import genai

'''
Function to collect data from Gemini
Usage: python gemini_test.py
Enter your API-KEY
'''

# CONFIGURATION
API_KEY = "API-KEY-HERE"
MODEL_NAME = "gemini-3-flash-preview"
IMAGE_FOLDER = "images"

# GENERATE UNIQUE FILENAME
SESSION_ID = uuid.uuid4().hex[:8]
OUTPUT_FILE = f"results_session_{SESSION_ID}.txt"

# TEST DATA
test_samples = [
    {"filename": "practice_1.jpeg", "correct_answer": "B", "id": "Practice 1"},
    {"filename": "practice_2.jpeg", "correct_answer": "A", "id": "Practice 2"},
    {"filename": "task_1.jpeg", "correct_answer": "B", "id": "Task 1"},
    {"filename": "task_2.jpeg", "correct_answer": "C", "id": "Task 2"},
    {"filename": "task_3.png", "correct_answer": "A", "id": "Task 3"},
    {"filename": "task_4.png", "correct_answer": "C", "id": "Task 4"},
    {"filename": "task_5.png", "correct_answer": "A", "id": "Task 5"},
    {"filename": "task_6.png", "correct_answer": "C", "id": "Task 6"},
    {"filename": "task_7.jpeg", "correct_answer": "C", "id": "Task 7"},
    {"filename": "task_8.png", "correct_answer": "A", "id": "Task 8"},
    {"filename": "task_9.png", "correct_answer": "C", "id": "Task 9"},
    {"filename": "task_10.jpeg", "correct_answer": "B", "id": "Task 10"},
]


def extract_letter(text):
    if not text:
        return "Error"
    matches = re.findall(r'\b([A-C])\b', text.upper())
    if matches:
        return matches[-1]
    return "Error"


def run_test():
    try:
        client = genai.Client(api_key=API_KEY)
    except Exception as e:
        print(f"Connection Error: {e}")
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        f_out.write(f"--- Session: {SESSION_ID} | Model: {MODEL_NAME} ---\n")
        f_out.write(f"{'ID':<15} | {'Result':<10} | {'Time':<8} | {'Answer'}\n")
        f_out.write("-" * 65 + "\n")

        print(f"--- TEST STARTED | FILE: {OUTPUT_FILE} ---")

        score = 0
        total = 0
        chat = client.chats.create(model=MODEL_NAME)

        for sample in test_samples:
            image_path = os.path.join(IMAGE_FOLDER, sample["filename"])
            if not os.path.exists(image_path):
                print(f"File not found: {image_path}")
                continue

            total += 1
            try:
                img = PIL.Image.open(image_path)

                if sample['id'] == "Practice 1":
                    prompt = ("You are participating in a mental rotation cognitive test. "
                              "Look at the image provided. "
                              "The 'TEST' square shows a pattern. "
                              "Only ONE of the options (A, B, or C) is a valid rotation of the TEST pattern. "
                              "Analyze the grid, corners, and color sequences carefully. "
                              "MANDATORY: Return ONLY the letter (A, B, or C) as your answer. "
                              "First question is a practice: Q: Which of these images (A, B, C) is a 90° clockwise rotation of the TEST image?")
                elif sample['id'] == "Practice 2":
                    prompt = ("Second question is a practice: Q: Which of these images (A, B, C) is a 180° clockwise rotation of the TEST image? "
                              "Look at the image provided. "
                              "The 'TEST' square shows a pattern. "
                              "Only ONE of the options (A, B, or C) is a valid rotation of the TEST pattern. "
                              "Analyze the grid, corners, and color sequences carefully. "
                              "MANDATORY: Return ONLY the letter (A, B, or C) as your answer. ")

                else:
                    prompt = (
                        "Q: Which of these images (A, B, C) is a rotation of the TEST image?"
                        "You are participating in a mental rotation cognitive test. "
                        "Look at the image provided. "
                        "The 'TEST' square shows a pattern. "
                        "Only ONE of the options (A, B, or C) is a valid rotation of the TEST pattern. "
                        "Analyze the grid, corners, and color sequences carefully. "
                        "MANDATORY: Return ONLY the letter (A, B, or C) as your answer at the end of your massage."
                    )

                start_time = time.time()
                response = chat.send_message(message=[img, prompt])
                elapsed = time.time() - start_time

                ai_text = response.text.strip()
                safe_output = ai_text.encode('ascii', 'ignore').decode('ascii')
                print(f"\n[{sample['id']}] AI Output:\n{safe_output}")

                ai_answer = extract_letter(ai_text)
                correct = sample["correct_answer"]
                is_correct = (ai_answer == correct)

                if is_correct:
                    score += 1

                status = "PASS" if is_correct else "FAIL"
                print(f"--> RESULT: {status} (Got: {ai_answer}, Expected: {correct})\n")

                # Пишем результат в файл
                f_out.write(f"{sample['id']:<15} | {status:<10} | {elapsed:.2f}s   | Got {ai_answer} (Exp {correct})\n")
                f_out.flush()

                if sample['id'] == "Practice 1":
                    chat.send_message(message="The correct answer for the first practice was B.")
                elif sample['id'] == "Practice 2":
                    chat.send_message(message="The correct answer for the second practice was A.")

                time.sleep(2)

            except Exception as e:
                print(f"Error on {sample['id']}: {e}")

        f_out.write("-" * 65 + "\n")
        f_out.write(f"Final Score: {score}/{total}\n")
        print(f"\nFINISHED. Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    run_test()
