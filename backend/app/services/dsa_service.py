import uuid
import asyncio
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.providers.ollama_provider import OllamaProvider
from app.agents.teacher_agent import TeacherAgent
from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.schemas.dsa import TopicResponse, ProblemResponse, ExplanationResponse, ComplexitySchema, DryRunStepSchema


# Static data catalog representing standard DSA Topics and Problems
DSA_TOPICS = [
    {
        "id": "arrays",
        "name": "Arrays & Hashing",
        "slug": "arrays",
        "description": "Fundamental array operations, hash maps, sliding windows, and set lookups."
    },
    {
        "id": "linked-lists",
        "name": "Linked Lists",
        "slug": "linked-lists",
        "description": "Singly and doubly linked lists traversal, insertion, and deletion algorithms."
    },
    {
        "id": "trees",
        "name": "Trees & Graphs",
        "slug": "trees",
        "description": "Binary trees representation, depth first searches (DFS), and graphs traversal algorithms."
    }
]

DSA_PROBLEMS = [
    {
        "id": "two-sum",
        "topic_slug": "arrays",
        "title": "Two Sum",
        "difficulty": "easy",
        "description": "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`. You may assume that each input would have exactly one solution, and you may not use the same element twice.",
        "starter_code": {
            "python": "def twoSum(nums: list[int], target: int) -> list[int]:\n    # Write your code here\n    pass\n",
            "javascript": "function twoSum(nums, target) {\n    // Write your code here\n    \n}\n",
            "java": "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        // Write your code here\n        return new int[0];\n    }\n}\n",
            "cpp": "class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        // Write your code here\n        return {};\n    }\n};\n"
        }
    },
    {
        "id": "valid-anagram",
        "topic_slug": "arrays",
        "title": "Valid Anagram",
        "difficulty": "easy",
        "description": "Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`, and `false` otherwise. An Anagram is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.",
        "starter_code": {
            "python": "def isAnagram(s: str, t: str) -> bool:\n    # Write your code here\n    pass\n",
            "javascript": "function isAnagram(s, t) {\n    // Write your code here\n    \n}\n",
            "java": "class Solution {\n    public boolean isAnagram(String s, String t) {\n        // Write your code here\n        return false;\n    }\n}\n",
            "cpp": "class Solution {\npublic:\n    bool isAnagram(string s, string t) {\n        // Write your code here\n        return false;\n    }\n};\n"
        }
    },
    {
        "id": "reverse-linked-list",
        "topic_slug": "linked-lists",
        "title": "Reverse Linked List",
        "difficulty": "easy",
        "description": "Given the head of a singly linked list, reverse the list, and return the reversed list.",
        "starter_code": {
            "python": "# Definition for singly-linked list.\n# class ListNode:\n#     def __init__(self, val=0, next=None):\n#         self.val = val\n#         self.next = next\ndef reverseList(head: Optional[ListNode]) -> Optional[ListNode]:\n    # Write your code here\n    pass\n",
            "javascript": "function reverseList(head) {\n    // Write your code here\n    \n}\n"
        }
    }
]


class DSAService:
    """Service managing topics, problems, and teaching mentors."""

    def _get_ai_provider(self):
        """Dynamic resolution of LLM provider: defaults to OpenAI, falls back to local Ollama."""
        if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("sk-proj-xxxx") and settings.OPENAI_API_KEY != "MOCK_KEY" and settings.OPENAI_API_KEY.strip():
            return OpenAIProvider(model="gpt-4o-mini")
        else:
            return OllamaProvider(model="codellama")

    def get_topics(self) -> List[TopicResponse]:
        """Fetch all supported DSA Topic categories."""
        return [TopicResponse(**topic) for topic in DSA_TOPICS]

    def get_topic_by_slug(self, slug: str) -> Optional[TopicResponse]:
        """Fetch details of a specific Topic category by slug."""
        for topic in DSA_TOPICS:
            if topic["slug"] == slug:
                return TopicResponse(**topic)
        return None

    def get_problems(self, topic_slug: Optional[str] = None) -> List[ProblemResponse]:
        """Fetch filterable coding challenges list."""
        problems = DSA_PROBLEMS
        if topic_slug:
            problems = [p for p in problems if p["topic_slug"] == topic_slug]
        return [ProblemResponse(**p) for p in problems]

    def get_problem_by_id(self, problem_id: str) -> Optional[ProblemResponse]:
        """Fetch a specific coding challenge by ID."""
        for p in DSA_PROBLEMS:
            if p["id"] == problem_id:
                return ProblemResponse(**p)
        return None

    async def explain_concept_for_problem(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        problem_id: str,
        code: str,
        language: str
    ) -> ExplanationResponse:
        """Call TeacherAgent to analyze a user's code solution and update progress in the database."""
        from sqlalchemy.ext.asyncio import AsyncSession
        import uuid
        from app.repositories.dsa_progress_repo import DSAProgressRepository

        problem = self.get_problem_by_id(problem_id)
        if not problem:
            raise NotFoundError(f"Problem '{problem_id}' not found.")

        provider = self._get_ai_provider()
        teacher = TeacherAgent(provider)
        
        explanation_data = await teacher.explain_concept(
            problem_name=problem.title,
            code=code,
            language=language
        )

        complexity_data = explanation_data.get("complexity", {})
        dry_run_list = explanation_data.get("dry_run", [])

        # Format complexity child schema
        complexity = ComplexitySchema(
            time_complexity=complexity_data.get("time_complexity", "O(N)"),
            time_explanation=complexity_data.get("time_explanation", "Standard traversal."),
            space_complexity=complexity_data.get("space_complexity", "O(1)"),
            space_explanation=complexity_data.get("space_explanation", "No extra allocation.")
        )

        # Format dry run steps array
        dry_run = [
            DryRunStepSchema(
                step=step.get("step", idx + 1),
                line_number=step.get("line_number", 1),
                description=step.get("description", ""),
                variables_state=step.get("variables_state", "")
            )
            for idx, step in enumerate(dry_run_list)
        ]

        # Log User progress in database
        dsa_repo = DSAProgressRepository(db)
        await dsa_repo.upsert_progress(
            user_id=user_id,
            problem_id=problem_id,
            topic_slug=problem.topic_slug,
            status="solved",  # Requesting AI tutor trace constitutes completion of this learning step
            language=language,
            code=code
        )

        return ExplanationResponse(
            concept_name=explanation_data.get("concept_name", problem.title),
            explanation=explanation_data.get("explanation", ""),
            complexity=complexity,
            dry_run=dry_run
        )

