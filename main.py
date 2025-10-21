from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Optional
import hashlib

app = FastAPI(title="String Analyzer API", version="1.0")

db: Dict[str, Dict] = {}


class StringRequest(BaseModel):
    value: str = Field(..., description="String to analyze")


class StringProperties(BaseModel):
    length: int
    is_palindrome: bool
    unique_characters: int
    word_count: int
    sha256_hash: str
    character_frequency_map: Dict[str, int]


class StringResponse(BaseModel):
    id: str
    value: str
    properties: StringProperties
    created_at: datetime


def analyze_string(value: str) -> StringProperties:
    """Compute all required properties for the given string."""
    value_clean = value.strip()
    sha256_hash = hashlib.sha256(value_clean.encode()).hexdigest()

    # Palindrome check (case-insensitive)
    normalized = ''.join(c.lower() for c in value_clean if c.isalnum())
    is_palindrome = normalized == normalized[::-1]

    # Frequency map
    freq_map = {}
    for char in value_clean:
        freq_map[char] = freq_map.get(char, 0) + 1

    return StringProperties(
        length=len(value_clean),
        is_palindrome=is_palindrome,
        unique_characters=len(set(value_clean)),
        word_count=len(value_clean.split()),
        sha256_hash=sha256_hash,
        character_frequency_map=freq_map,
    )


@app.post("/strings", response_model=StringResponse, status_code=201)
def create_string(req: StringRequest):
    if not req.value or not isinstance(req.value, str):
        raise HTTPException(
            status_code=400, detail="Invalid or missing 'value' field")

    properties = analyze_string(req.value)
    if properties.sha256_hash in db:
        raise HTTPException(status_code=409, detail="String already exists")

    record = {
        "id": properties.sha256_hash,
        "value": req.value,
        "properties": properties.dict(),
        "created_at": datetime.utcnow(),
    }
    db[properties.sha256_hash] = record
    return record


@app.get("/strings/filter-by-natural-language")
def filter_by_natural_language(query: str):
    """Basic heuristic parser for natural language filtering."""
    q = query.lower()
    filters = {}

    if "palindromic" in q or "palindrome" in q:
        filters["is_palindrome"] = True
    if "single word" in q or "one word" in q:
        filters["word_count"] = 1
    if "longer than" in q:
        try:
            num = int(''.join(c for c in q.split(
                "longer than")[1] if c.isdigit()))
            filters["min_length"] = num + 1
        except Exception:
            pass
    if "containing the letter" in q:
        try:
            char = q.split("containing the letter")[1].strip().split()[0]
            print(char)
            filters["contains_character"] = char
        except Exception:
            pass
    elif "containing the" in q and "vowel" in q:
        filters["contains_character"] = "a"

    if not filters:
        raise HTTPException(
            status_code=400, detail="Unable to parse natural language query")

    results = []
    for record in db.values():
        p = record["properties"]
        if "is_palindrome" in filters and p["is_palindrome"] != filters["is_palindrome"]:
            continue
        if "word_count" in filters and p["word_count"] != filters["word_count"]:
            continue
        if "min_length" in filters and p["length"] <= filters["min_length"]:
            continue
        if "contains_character" in filters and filters["contains_character"] not in record["value"]:
            continue
        results.append(record)

    return {
        "data": results,
        "count": len(results),
        "interpreted_query": {
            "original": query,
            "parsed_filters": filters
        }
    }


@app.get("/strings/{string_value}", response_model=StringResponse)
def get_string(string_value: str):
    sha256_hash = hashlib.sha256(string_value.encode()).hexdigest()
    record = db.get(sha256_hash)
    if not record:
        raise HTTPException(status_code=404, detail="String not found")
    return record


@app.get("/strings")
def get_all_strings(
    is_palindrome: Optional[bool] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    word_count: Optional[int] = None,
    contains_character: Optional[str] = Query(None, max_length=1),
):
    try:
        results = []
        for record in db.values():
            p = record["properties"]

            if is_palindrome is not None and p["is_palindrome"] != is_palindrome:
                continue
            if min_length is not None and p["length"] < min_length:
                continue
            if max_length is not None and p["length"] > max_length:
                continue
            if word_count is not None and p["word_count"] != word_count:
                continue
            if contains_character and contains_character not in record["value"]:
                continue

            results.append(record)

        return {
            "data": results,
            "count": len(results),
            "filters_applied": {
                k: v for k, v in {
                    "is_palindrome": is_palindrome,
                    "min_length": min_length,
                    "max_length": max_length,
                    "word_count": word_count,
                    "contains_character": contains_character,
                }.items() if v is not None
            }
        }

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid query parameters")


@app.delete("/strings/{string_value}", status_code=204)
def delete_string(string_value: str):
    sha256_hash = hashlib.sha256(string_value.encode()).hexdigest()
    if sha256_hash not in db:
        raise HTTPException(status_code=404, detail="String not found")
    del db[sha256_hash]
    return None
