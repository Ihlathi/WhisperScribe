from openai import OpenAI
import json

results = ""

with open("current_reading_session.txt", "r", encoding='utf-8') as file:
    reading_session_content = file.read()

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

def make_quiz(content):
    global results
    messages = [
        {"role": "system", "content": 
         """You are an AI that helps create reading comprehension quizzes for the user based upon the section of the book they just read. 
         You return back usually around 10 - 20 questions ranging from details about the reading to broader perspectives about parts. Min questions is 5.
         You return multiple-choice questions in the form of a question and 4 possible answers, as well as the correct answer. 
         You do not include the answer letters in each answer, however your answer options should be A through D. For the correct answer, you only include the letter of the correct answer (A through D). Explanation is a brief explanation why the correct answer is so."""},
        {"role": "user", "content": f"Based on the following text, write your quiz: {content}"}
    ]

    quiz_schema = {
        "type": "json_schema",
        "json_schema": {
            "name": "quiz",
            "schema": {
                "type": "object",
                "properties": {
                    "quiz": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "question": {"type": "string"},
                                "answer a": {"type": "string"},
                                "answer b": {"type": "string"},
                                "answer c": {"type": "string"},
                                "answer d": {"type": "string"},
                                "correct answer": {"type": "string"},
                                "explanation": {"type": "string"}
                            },
                            "required": ["question", "answer a", "answer b", "answer c", "answer d", "correct answer", "explanation"]
                        },
                        "minItems": 5,
                    }
                },
                "required": ["quiz"]
            },
        }
    }

    response = client.chat.completions.create(
        model="meta-llama-3.1-8b-instruct",
        messages=messages,
        response_format=quiz_schema,
    )

    results = json.loads(response.choices[0].message.content)

def do_quiz(results):
    if isinstance(results, str):
        results = json.loads(results)

    questions = results["quiz"]

    # for each quiz question
    for index, question_data in enumerate(questions, start=1):
        print(f"Question {index}: {question_data['question']}")
        print(f"A. {question_data['answer a']}")
        print(f"B. {question_data['answer b']}")
        print(f"C. {question_data['answer c']}")
        print(f"D. {question_data['answer d']}")

        # get answer
        user_answer = input("Your answer (A, B, C, D): ").strip().upper()

        # check answer
        correct_answer = question_data["correct answer"].upper()
        if user_answer == correct_answer:
            print("Correct!")
        else:
            print(f"Incorrect. The correct answer is {correct_answer}.")

        # explanation
        print(f"Explanation: {question_data['explanation']}")
        print("-" * 40)


if __name__ == "__main__":
    make_quiz(reading_session_content)
    do_quiz(results)