"""
seed_db.py — One-time script to load biology questions into Supabase.

Usage:
    1. Make sure you have a .env file with SUPABASE_URL and SUPABASE_SERVICE_KEY
    2. pip install supabase python-dotenv
    3. python scripts/seed_db.py

Run this ONCE. It's safe to re-run — it checks for existing data first.
"""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Load .env from the api/ folder (one level up from scripts/)
env_path = Path(__file__).parent.parent / "api" / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")  # Use SERVICE key, not anon!

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("ERROR: Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# ── Load JSON files ───────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent / "data"

with open(DATA_DIR / "questions_biology.json", encoding="utf-8") as f:
    questions_raw = json.load(f)

with open(DATA_DIR / "answers_biology.json", encoding="utf-8") as f:
    answers_raw = json.load(f)

# Build a lookup: question_number → correct_options
answers_lookup = {a["question"]: a["correct_options"] for a in answers_raw}

# ── Category ranges (from the textbook table of contents) ─────────────────────
# These map question number ranges to category names
CATEGORIES = [
    {"name": "Biológia bunky, rastlín a živočíchov", "range": (1, 450),    "sort_order": 1},
    {"name": "Biológia človeka",                      "range": (451, 900),  "sort_order": 2},
    {"name": "Genetika",                              "range": (901, 1250), "sort_order": 3},
    {"name": "Systém rastlín a živočíchov",           "range": (1251, 1365),"sort_order": 4},
    {"name": "Ekológia a evolúcia",                   "range": (1366, 1500),"sort_order": 5},
]

def get_category_name(question_number: int) -> str:
    for cat in CATEGORIES:
        lo, hi = cat["range"]
        if lo <= question_number <= hi:
            return cat["name"]
    return "Nezaradené"  # "Uncategorised" in Slovak

# ── Step 1: Create Subject ────────────────────────────────────────────────────
print("Checking for existing Biology subject...")

existing = supabase.table("subjects").select("id").eq("name", "Biológia").execute()

if existing.data:
    subject_id = existing.data[0]["id"]
    print(f"  Subject already exists: {subject_id}")
else:
    result = supabase.table("subjects").insert({
        "name": "Biológia",
        "description": "Biológia — príprava na prijímacie skúšky LF UPJŠ Košice (1500 otázok)",
        "user_id": None  # system/public content
    }).execute()
    subject_id = result.data[0]["id"]
    print(f"  Created subject: {subject_id}")

# ── Step 2: Create Categories ─────────────────────────────────────────────────
print("Creating categories...")

category_id_map = {}  # name → UUID

for cat_def in CATEGORIES:
    existing_cat = supabase.table("categories") \
        .select("id") \
        .eq("subject_id", subject_id) \
        .eq("name", cat_def["name"]) \
        .execute()

    if existing_cat.data:
        category_id_map[cat_def["name"]] = existing_cat.data[0]["id"]
        print(f"  Already exists: {cat_def['name']}")
    else:
        result = supabase.table("categories").insert({
            "subject_id": subject_id,
            "name": cat_def["name"],
            "sort_order": cat_def["sort_order"]
        }).execute()
        category_id_map[cat_def["name"]] = result.data[0]["id"]
        print(f"  Created: {cat_def['name']}")

# ── Step 3: Seed Questions in batches ─────────────────────────────────────────
print(f"\nSeeding {len(questions_raw)} questions...")

# Check how many already exist for this subject
existing_count = supabase.table("questions") \
    .select("id", count="exact") \
    .eq("subject_id", subject_id) \
    .execute()

if existing_count.count and existing_count.count > 0:
    print(f"  {existing_count.count} questions already seeded. Skipping.")
    print("  If you want to re-seed, delete all questions for this subject first.")
else:
    BATCH_SIZE = 100
    total_inserted = 0
    skipped = 0

    for i in range(0, len(questions_raw), BATCH_SIZE):
        batch_raw = questions_raw[i:i + BATCH_SIZE]
        batch_to_insert = []

        for q in batch_raw:
            qnum = q["question_number"]
            correct = answers_lookup.get(qnum)

            if correct is None:
                # Questions 1493-1500 exist in answers but not in questions JSON
                # (PDF extraction missed them) — skip gracefully
                skipped += 1
                continue

            cat_name = get_category_name(qnum)
            cat_id = category_id_map.get(cat_name)

            batch_to_insert.append({
                "subject_id": subject_id,
                "category_id": cat_id,
                "question_number": qnum,
                "question_text": q["question_text"],
                "type": q["type"],
                "options": q["options"],        # JSONB: {"a": "...", "b": "..."}
                "correct_options": correct,     # TEXT[]: ["a", "c"]
                "page": q.get("page"),
                "user_id": None                 # system content
            })

        if batch_to_insert:
            supabase.table("questions").insert(batch_to_insert).execute()
            total_inserted += len(batch_to_insert)

        print(f"  Progress: {min(i + BATCH_SIZE, len(questions_raw))}/{len(questions_raw)}", end="\r")

    print(f"\n  Inserted: {total_inserted} questions")
    if skipped:
        print(f"  Skipped (no answer found): {skipped} questions")

print("\n✅ Seeding complete!")
print(f"   Subject ID: {subject_id}")
print(f"   Categories: {len(category_id_map)}")
