
from code_reviewer.reviewer import CodeReviewSystem
import os
import json

if __name__ == "__main__":
    print("Starting AI-Powered Code Reviewer application...")

    # Create a dummy Python file for review
    dummy_code = """
def calculate_sum(a, b):
    # This function adds two numbers
    return a + b

def process_data(data):
    try:
        result = data["value"] / data["divisor"]
    except:
        print("An error occurred")
        result = 0
    return "The result is {}".format(result)

class MyClass:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello, {self.name}!"
"""
    
    dummy_file_path = "dummy_code_to_review.py"
    with open(dummy_file_path, "w") as f:
        f.write(dummy_code)

    reviewer = CodeReviewSystem()
    review_report = reviewer.review_file(dummy_file_path)
    
    print("\nCode Review Report:")
    print(json.dumps(review_report, indent=2))
    os.remove(dummy_file_path)

    print("AI-Powered Code Reviewer application finished.")

# Update on 2023-01-02 00:00:00