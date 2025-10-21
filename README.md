## String Analyzer API (FastAPI)

A simple **FastAPI** app that analyzes strings and stores their computed properties such as length, word count, palindrome status, and SHA-256 hash.
It also supports query-based and natural-language filtering.

---

### Run Locally

1. **Clone the repo**

   ```bash
   git clone https://github.com/toluwaa-o/string-analyzer-api.git
   cd string-analyzer-api
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server**

   ```bash
   uvicorn main:app --reload
   ```

5. **Test the endpoints**
   Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive Swagger UI.

---

### Example: Analyze a String

**Request**

`POST /strings`

```json
{
  "value": "level up now"
}
```

**Response**

```json
{
  "id": "a0f34b8e1c4d4b93b3d8e11c64c8f6f5d3f9a6c3795b0a77a54c0f77a02f8dce",
  "value": "level up now",
  "properties": {
    "length": 12,
    "is_palindrome": false,
    "unique_characters": 10,
    "word_count": 3,
    "sha256_hash": "a0f34b8e1c4d4b93b3d8e11c64c8f6f5d3f9a6c3795b0a77a54c0f77a02f8dce",
    "character_frequency_map": {
      "l": 2,
      "e": 2,
      "v": 1,
      " ": 2,
      "u": 1,
      "p": 1,
      "n": 1,
      "o": 1,
      "w": 1
    }
  },
  "created_at": "2025-10-21T22:00:00Z"
}
```

---

### Endpoints Overview

| Method   | Endpoint                              | Description                            |
| -------- | ------------------------------------- | -------------------------------------- |
| `POST`   | `/strings`                            | Analyze and store a string             |
| `GET`    | `/strings/{string_value}`             | Get analysis for a specific string     |
| `GET`    | `/strings`                            | List all analyzed strings with filters |
| `GET`    | `/strings/filter-by-natural-language` | Filter using natural language queries  |
| `DELETE` | `/strings/{string_value}`             | Delete a stored string                 |