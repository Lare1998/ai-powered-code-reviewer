import os
import re
import ast
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CodeIssue:
    """Represents a single issue found during code review."""
    def __init__(self, line_number: int, issue_type: str, description: str, suggestion: str):
        self.line_number = line_number
        self.issue_type = issue_type
        self.description = description
        self.suggestion = suggestion

    def __repr__(self):
        return f"Line {self.line_number}: [{self.issue_type}] {self.description} -> {self.suggestion}"

class CodeReviewer:
    """
    Main class for performing automated code reviews.
    Analyzes Python code for style, potential bugs, and complexity.
    """
    def __init__(self, max_line_length: int = 100, max_complexity: int = 10):
        self.max_line_length = max_line_length
        self.max_complexity = max_complexity
        self.issues: List[CodeIssue] = []

    def review_file(self, file_path: str) -> List[CodeIssue]:
        """Reads a file and performs a complete review."""
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
            
        return self.review_code(source_code)

    def review_code(self, source_code: str) -> List[CodeIssue]:
        """Performs review on a string of source code."""
        self.issues = []
        lines = source_code.split('\n')
        
        self._check_line_lengths(lines)
        self._check_naming_conventions(lines)
        self._analyze_ast(source_code)
        
        return self.issues

    def _check_line_lengths(self, lines: List[str]):
        """Checks if any lines exceed the maximum allowed length."""
        for i, line in enumerate(lines):
            if len(line) > self.max_line_length:
                self.issues.append(CodeIssue(
                    line_number=i + 1,
                    issue_type="Style",
                    description=f"Line exceeds {self.max_line_length} characters ({len(line)}).",
                    suggestion="Break the line into multiple shorter lines."
                ))

    def _check_naming_conventions(self, lines: List[str]):
        """Checks for basic PEP 8 naming conventions using regex."""
        class_pattern = re.compile(r'^class\s+[a-z_]')
        func_pattern = re.compile(r'^def\s+[A-Z]')
        
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if class_pattern.match(stripped_line):
                self.issues.append(CodeIssue(
                    line_number=i + 1,
                    issue_type="Naming",
                    description="Class name should use CamelCase.",
                    suggestion="Rename the class using CamelCase (e.g., MyClass)."
                ))
            elif func_pattern.match(stripped_line):
                self.issues.append(CodeIssue(
                    line_number=i + 1,
                    issue_type="Naming",
                    description="Function name should use snake_case.",
                    suggestion="Rename the function using snake_case (e.g., my_function)."
                ))

    def _analyze_ast(self, source_code: str):
        """Uses the ast module to find deeper structural issues."""
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            self.issues.append(CodeIssue(
                line_number=e.lineno or 0,
                issue_type="Syntax",
                description=f"Syntax error: {e.msg}",
                suggestion="Fix the syntax error to allow further analysis."
            ))
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._check_function_complexity(node)
                self._check_mutable_default_args(node)

    def _check_function_complexity(self, node: ast.FunctionDef):
        """Estimates cyclomatic complexity of a function."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.And, ast.Or, ast.ExceptHandler)):
                complexity += 1
                
        if complexity > self.max_complexity:
            self.issues.append(CodeIssue(
                line_number=node.lineno,
                issue_type="Complexity",
                description=f"Function '{node.name}' is too complex (score: {complexity}).",
                suggestion="Refactor the function into smaller, more manageable pieces."
            ))

    def _check_mutable_default_args(self, node: ast.FunctionDef):
        """Checks for dangerous mutable default arguments like lists or dicts."""
        for arg in node.args.defaults:
            if isinstance(arg, (ast.List, ast.Dict, ast.Set)):
                self.issues.append(CodeIssue(
                    line_number=node.lineno,
                    issue_type="Bug Risk",
                    description=f"Function '{node.name}' uses a mutable default argument.",
                    suggestion="Use 'None' as the default and initialize the mutable object inside the function."
                ))

    def generate_report(self) -> str:
        """Generates a formatted string report of all found issues."""
        if not self.issues:
            return "✅ Code review passed! No issues found."
            
        report = [f"❌ Found {len(self.issues)} issues during code review:\n"]
        for issue in sorted(self.issues, key=lambda x: x.line_number):
            report.append(f"- {issue}")
            
        return "\n".join(report)

if __name__ == "__main__":
    # Example usage
    sample_code = '''
def bad_function(my_list=[]):
    for i in range(10):
        if i % 2 == 0:
            if i > 5:
                print("Complex!")
    return my_list

class bad_class:
    pass
'''
    reviewer = CodeReviewer(max_complexity=2)
    reviewer.review_code(sample_code)
    print(reviewer.generate_report())
