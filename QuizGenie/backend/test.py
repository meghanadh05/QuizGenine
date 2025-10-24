# test_quiz.py
from src.generate_quiz import generate_quiz
import json

if __name__ == "__main__":
    print("--- Testing Quiz Generation ---")
    # Since this script is running, load_dotenv() inside generate_quiz.py will work correctly.
    topic = "Linear Regression in Machine Learning"
    quiz_result = generate_quiz(topic, top_k=2)

    # Pretty-print the JSON output
    print(json.dumps(quiz_result, indent=2))
    print("--- Test Complete ---")