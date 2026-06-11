import json
import re
from typing import Any, Dict, Optional, AsyncGenerator

def generate_mock_response(
    prompt: str,
    system_instruction: Optional[str] = None,
    schema: Optional[Dict[str, Any]] = None
) -> str:
    """Generate rich, structured mock responses matching the requested schema or system instruction."""
    sys_instruction_str = (system_instruction or "").lower()
    prompt_str = prompt.lower()

    # 1. COORDINATOR AGENT ROUTING FALLBACK
    if "intent" in sys_instruction_str or (schema and "intent" in schema.get("properties", {})):
        intent = "general"
        if "review" in prompt_str or "refactor" in prompt_str or "improve" in prompt_str:
            intent = "review"
        elif "dsa" in prompt_str or "problem" in prompt_str or "two sum" in prompt_str or "binary search" in prompt_str or "sort" in prompt_str:
            intent = "dsa"
        elif "interview" in prompt_str or "mock" in prompt_str or "simulator" in prompt_str:
            intent = "interview"
        
        return json.dumps({
            "intent": intent,
            "confidence": 0.95,
            "reasoning": f"Identified {intent} intent based on keyword matching in user input.",
            "parameters": {
                "language": "python",
                "topic": "System Design" if "design" in prompt_str else "Coding",
                "difficulty": "medium"
            }
        })

    # 2.5 CODE REVIEW ENGINE SYNTHESIS FALLBACK
    if schema and "has_bugs" in schema.get("properties", {}) and "score" in schema.get("properties", {}):
        code_match = re.search(r"### Code:\n(.*)", prompt, re.DOTALL)
        code = code_match.group(1).strip() if code_match else "def bubble_sort(arr):\n    pass"
        
        has_bugs = False
        bugs = []
        if "bubble_sort" in code:
            has_bugs = True
            bugs.append({
                "line": 8,
                "severity": "error",
                "description": "Incomplete swap logic. Value of temp is assigned but the adjacent element is not updated, resulting in corrupted array states.",
                "fix": "arr[j], arr[j+1] = arr[j+1], arr[j]"
            })
            
        score = 75 if has_bugs else 90
        summary = "Integrated review: Code evaluated successfully. Pylint and Bandit checks passed with minor warnings."
        issues = [
            {
                "category": "style",
                "line": 1,
                "description": "Missing function docstring.",
                "suggestion": "Add a descriptive docstring to clarify the function purpose."
            }
        ]
        return json.dumps({
            "score": score,
            "summary": summary,
            "issues": issues,
            "has_bugs": has_bugs,
            "bugs": bugs,
            "refactored_code": code
        })

    # 2. REVIEWER AGENT FALLBACK
    if "reviewer" in sys_instruction_str or (schema and "score" in schema.get("properties", {}) and "issues" in schema.get("properties", {})):
        # Extract code if present
        code_match = re.search(r"### Code:\n(.*)", prompt, re.DOTALL)
        code = code_match.group(1).strip() if code_match else "def bubble_sort(arr):\n    pass"
        
        # Simple analysis to make mock look realistic
        score = 82
        summary = "The code has solid core logic, but it uses sub-optimal complexity and lacks formatting and error checking. We recommend refactoring to utilize modern language constructs and optimal built-in functions."
        
        issues = [
            {
                "category": "performance",
                "line": 3,
                "description": "Double nested loops result in O(N^2) time complexity. This can be optimized to O(N log N) or O(N) using more efficient algorithms or data structures.",
                "suggestion": "Consider utilizing a hash map or sorting the input first to reduce complexity."
            },
            {
                "category": "readability",
                "line": 1,
                "description": "Function name and variable naming are slightly cryptic and lack pep8/camelCase documentation.",
                "suggestion": "Rename variables to represent their actual contents and add descriptive docstrings."
            },
            {
                "category": "security",
                "line": 5,
                "description": "No parameter validations are present, exposing the system to potential type-errors or null pointer exceptions.",
                "suggestion": "Add type guards or input check constraints at the beginning of the function."
            }
        ]
        
        # Simple mock refactoring
        refactored_code = code
        if "bubble_sort" in code:
            refactored_code = "def bubble_sort(arr):\n    # Optimized using early exit flag\n    n = len(arr)\n    for i in range(n):\n        swapped = False\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n                swapped = True\n        if not swapped:\n            break\n    return arr"
        elif "calculateTotal" in code:
            refactored_code = "function calculateTotal(items, discount = 0) {\n    if (!Array.isArray(items)) return 0;\n    const subtotal = items.reduce((sum, item) => sum + (item.price || 0), 0);\n    return subtotal * (1 - discount);\n}"

        return json.dumps({
            "score": score,
            "summary": summary,
            "issues": issues,
            "refactored_code": refactored_code
        })

    # 3. DEBUGGER AGENT FALLBACK
    if "debugger" in sys_instruction_str or (schema and "has_bugs" in schema.get("properties", {})):
        # Inspect code to make a realistic report
        code_match = re.search(r"### Code:\n(.*)", prompt, re.DOTALL)
        code = code_match.group(1).strip() if code_match else ""
        
        has_bugs = False
        bugs = []
        
        if "bubble_sort" in code and "temp" in code and "arr[j+1] = temp" not in code:
            has_bugs = True
            bugs.append({
                "line": 8,
                "severity": "error",
                "description": "Incomplete swap logic. Value of temp is assigned but the adjacent element is not updated, resulting in corrupted array states.",
                "fix": "arr[j], arr[j+1] = arr[j+1], arr[j]"
            })
        elif "calculateTotal" in code and "var i" in code:
            has_bugs = True
            bugs.append({
                "line": 4,
                "severity": "warning",
                "description": "Using 'var' instead of 'let' or 'const' exposes loop index to outer function scope, causing potential variable hoisting side effects.",
                "fix": "Change 'var i = 0' to 'let i = 0'"
            })

        return json.dumps({
            "has_bugs": has_bugs,
            "bugs": bugs
        })

    # 4. TEACHER AGENT (DSA) FALLBACK
    if "dsa" in sys_instruction_str or (schema and "concept_name" in schema.get("properties", {})):
        # Extract problem name
        prob_match = re.search(r"coding challenge '(.*)'", prompt)
        concept_name = prob_match.group(1).replace("-", " ").title() if prob_match else "Algorithm Concept"
        
        return json.dumps({
            "concept_name": concept_name,
            "explanation": f"This problem focuses on optimizing searches and relational mappings. By leveraging hash lookup tables, we can bypass nested scanning loops to find target entries in a single pass.",
            "complexity": {
                "time_complexity": "O(N)",
                "time_explanation": "Each element in the collection is traversed at most once, performing hash table insertions and lookups in O(1) constant time.",
                "space_complexity": "O(N)",
                "space_explanation": "In the worst case, we store metadata for every element of the array in our auxiliary hash dictionary."
            },
            "dry_run": [
                {
                    "step": 1,
                    "line_number": 2,
                    "description": "Initialize empty hash map to store numbers and indices.",
                    "variables_state": "hash_map={}"
                },
                {
                    "step": 2,
                    "line_number": 3,
                    "description": "Iterate index i=0, value=2. Calculate complement (target - 2). Not in map.",
                    "variables_state": "i=0, val=2, complement=7, hash_map={2: 0}"
                },
                {
                    "step": 3,
                    "line_number": 3,
                    "description": "Iterate index i=1, value=7. Calculate complement (target - 7) which is 2. 2 is found in hash_map at index 0!",
                    "variables_state": "i=1, val=7, complement=2, hash_map={2: 0}"
                },
                {
                    "step": 4,
                    "line_number": 5,
                    "description": "Return indices pair [0, 1]. Execution terminates successfully.",
                    "variables_state": "result=[0, 1]"
                }
            ]
        })

    # 5. INTERVIEWER CHAT TURN FALLBACK
    if "interviewer" in sys_instruction_str and (schema and "focus_area" in schema.get("properties", {}) and "response" in schema.get("properties", {})):
        # Determine if it's the start
        if "chat history" not in prompt_str or len(prompt) < 150:
            return json.dumps({
                "response": "Hello! I am your AI interviewer today. We'll be walking through a Technical Interview. To begin, could you introduce yourself briefly and explain how you would approach designing a highly available URL shortener service?",
                "focus_area": "Introduction"
            })
        
        # Challenging follow-up question
        return json.dumps({
            "response": "That approach makes sense. How would you handle database scaling if the write traffic suddenly spikes by 10x? What caching or database partitioning techniques would you apply first?",
            "focus_area": "System Design & Scaling"
        })

    # 6. INTERVIEWER EVALUATION REPORT FALLBACK
    if "evaluating" in sys_instruction_str or (schema and "strengths" in schema.get("properties", {}) and "weakness_areas" in schema.get("properties", {})):
        return json.dumps({
            "score": 82,
            "summary": "The candidate demonstrated strong conceptual knowledge of web architectures, load balancing, and database scaling. They communicated trade-offs clearly but were slightly slow to optimize database write bottlenecks.",
            "strengths": [
                "Good explanation of horizontal database scaling.",
                "Strong use of caching layers to speed up read operations.",
                "Structured communication during system design steps."
            ],
            "weakness_areas": [
                "Could have gone deeper into write database sharding schemes.",
                "Did not fully evaluate write-through vs write-back cache consistency trade-offs."
            ],
            "correct_code_suggestions": "```python\n# Optimal Caching Pattern using Redis for read-through\nimport redis\nr = redis.Redis(host='localhost', port=6379, db=0)\n\ndef get_url(short_id):\n    # Check Cache First\n    cached = r.get(short_id)\n    if cached:\n        return cached.decode('utf-8')\n    \n    # Database Fallback\n    url = db.query_url(short_id)\n    if url:\n        r.setex(short_id, 3600, url)\n    return url\n```",
            "improvement_tips": [
                "Review distributed transaction synchronization mechanisms.",
                "Practice estimating database write sizes and network bandwidth requirements."
            ]
        })

    # 7. GENERAL CHAT CONVERSATION FALLBACK
    return "I am CodeGuru AI, your coding mentor. I can help you review code, solve DSA challenges, or prepare for technical interviews. Let me know what you would like to work on!"

async def async_stream_mock_response(prompt: str, system_instruction: Optional[str] = None) -> AsyncGenerator[str, None]:
    """Asynchronously stream mock chat responses chunk by chunk."""
    response_text = generate_mock_response(prompt, system_instruction)
    words = response_text.split(" ")
    for i in range(0, len(words), 3):
        chunk = " ".join(words[i:i+3]) + " "
        yield chunk
        import asyncio
        await asyncio.sleep(0.05)
