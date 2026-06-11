# CodeGuru AI API Documentation

Base Endpoint: `/api/v1`

---

## 🔐 Authentication Endpoints (`/auth`)

### 1. Register Account
- **Endpoint**: `POST /auth/register`
- **Payload**:
  ```json
  {
    "email": "developer@example.com",
    "password": "securepassword123"
  }
  ```
- **Response (201)**:
  ```json
  {
    "id": "uuid-string",
    "email": "developer@example.com",
    "is_active": true,
    "is_superuser": false
  }
  ```

### 2. Login & Token Retrieval
- **Endpoint**: `POST /auth/login`
- **Payload**:
  ```json
  {
    "email": "developer@example.com",
    "password": "securepassword123"
  }
  ```
- **Response (200)**:
  ```json
  {
    "access_token": "jwt-access-token",
    "refresh_token": "jwt-refresh-token",
    "token_type": "bearer"
  }
  ```

### 3. Refresh Access Token
- **Endpoint**: `POST /auth/refresh`
- **Payload**:
  ```json
  {
    "refresh_token": "jwt-refresh-token"
  }
  ```
- **Response (200)**: New access and refresh token pair.

---

## 👤 Users & Profile (`/users`)

### 1. Fetch Current User Profile
- **Endpoint**: `GET /users/me`
- **Headers**: `Authorization: Bearer <token>`
- **Response (200)**: User model details including linked profile object.

### 2. Update Profile Metadata
- **Endpoint**: `PUT /users/me/profile`
- **Headers**: `Authorization: Bearer <token>`
- **Payload**:
  ```json
  {
    "first_name": "Jane",
    "last_name": "Doe",
    "bio": "Staff AI Engineer",
    "skills": ["Python", "Rust", "TypeScript"]
  }
  ```
- **Response (200)**: Updated profile model values.

---

## 🔍 Code Reviews (`/reviews`)

### 1. Request Code Review
- **Endpoint**: `POST /reviews/`
- **Headers**: `Authorization: Bearer <token>`
- **Payload**:
  ```json
  {
    "code": "def fib(n): return n if n < 2 else fib(n-1)+fib(n-2)",
    "language": "python"
  }
  ```
- **Response (201)**: Merged analysis report from Reviewer and Debugger agents including score, bug logs, and refactored code.

---

## 🎓 DSA Mentor (`/dsa`)

### 1. List Topics
- **Endpoint**: `GET /dsa/topics`
- **Response (200)**: Array of supported topics (e.g. Arrays, Trees, Linked Lists).

### 2. Fetch Coding Challenges
- **Endpoint**: `GET /dsa/problems`
- **Params**: `topic_slug` (optional filter)
- **Response (200)**: Array of problem definition templates and language starter templates.

### 3. Get Code Concept Explanation
- **Endpoint**: `POST /dsa/problems/{problem_id}/explain`
- **Headers**: `Authorization: Bearer <token>`
- **Payload**:
  ```json
  {
    "code": "def twoSum(nums, target): ...",
    "language": "python"
  }
  ```
- **Response (200)**: Step-debugger tracing states, complexities, and textual explanation report.

---

## 📊 Learning Analytics (`/analytics`)

### 1. Fetch Analytics Overview
- **Endpoint**: `GET /analytics/overview`
- **Headers**: `Authorization: Bearer <token>`
- **Response (200)**: High-level dashboard stats, active streak records, Recharts score progress timeline, and contribution heatmaps.

---

## 💬 Technical Mock Interviews (`/interview`)

### 1. Start Mock Interview
- **Endpoint**: `POST /interview/start`
- **Headers**: `Authorization: Bearer <token>`
- **Payload**:
  ```json
  {
    "topic": "System Design",
    "difficulty": "hard"
  }
  ```
- **Response (201)**: Returns the initialized `InterviewSession` detailing topic, difficulty, and the first interviewer question.

### 2. List Interview Sessions
- **Endpoint**: `GET /interview/sessions`
- **Headers**: `Authorization: Bearer <token>`
- **Params**: `skip` (optional, default 0), `limit` (optional, default 20)
- **Response (200)**: Array of historical mock interview sessions.

### 3. Fetch Session Details
- **Endpoint**: `GET /interview/{session_id}`
- **Headers**: `Authorization: Bearer <token>`
- **Response (200)**: Returns full session details including the chat log message list, score, and scorecard feedback if completed.

### 4. Send Message / Answer Question
- **Endpoint**: `POST /interview/{session_id}/message`
- **Headers**: `Authorization: Bearer <token>`
- **Payload**:
  ```json
  {
    "message": "I would use a distributed Redis lock to ensure consistency..."
  }
  ```
- **Response (200)**: Appends user's reply, queries the AI Interviewer agent, appends the next follow-up query, and returns the updated session state.

### 5. End & Grade Mock Session
- **Endpoint**: `POST /interview/{session_id}/end`
- **Headers**: `Authorization: Bearer <token>`
- **Response (200)**: Marks the session completed (`is_completed: true`), queries the AI Interviewer agent for final evaluations, saves the scorecard metrics (strengths, weakness areas, code snippets, study tips), and returns the completed session.

---

## 🤖 Multi-Agent Orchestration & Routing (`/coordinator`)

### 1. Route & Execute Prompt
- **Endpoint**: `POST /coordinator/route`
- **Headers**: `Authorization: Bearer <token>`
- **Payload**:
  ```json
  {
    "user_input": "explain two-sum solution: def twoSum(): pass",
    "session_id": null
  }
  ```
- **Response (200)**:
  ```json
  {
    "intent": "dsa",
    "reasoning": "User asked about two-sum coding challenges.",
    "response": "I've compiled a trace report and Big-O analysis for your Two Sum solution.",
    "data": {
      "concept_name": "Two Sum",
      "explanation": "Find two numbers in array adding to target.",
      "complexity": {
        "time_complexity": "O(N)",
        "time_explanation": "Single hashmap pass.",
        "space_complexity": "O(N)",
        "space_explanation": "Hashmap stores elements."
      },
      "dry_run": [
        {
          "step": 1,
          "line_number": 2,
          "description": "Initialize empty map.",
          "variables_state": "map={}"
        }
      ]
    }
  }
  ```


