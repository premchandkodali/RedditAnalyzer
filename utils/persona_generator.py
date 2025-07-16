import os
import requests
import praw
from dotenv import load_dotenv
from tqdm import tqdm

# Load API keys
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Reddit API config
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

def extract_username(profile_url):
    return profile_url.rstrip('/').split('/')[-1]

def fetch_user_activity(username, limit=100):
    user = reddit.redditor(username)
    posts, comments = [], []
    print(f"\n📥 Collecting data for u/{username}...\n")
    for submission in tqdm(user.submissions.new(limit=limit), desc="Fetching posts"):
        print("submission",submission)
        if submission.selftext:
            posts.append(f"[POST in r/{submission.subreddit}] {submission.title}\n{submission.selftext}\n")
    for comment in tqdm(user.comments.new(limit=limit), desc="Fetching comments"):
        comments.append(f"[COMMENT in r/{comment.subreddit}]\n{comment.body}\n")
    return posts, comments

def call_gemini(prompt):
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    data = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    response = requests.post(GEMINI_ENDPOINT, headers=headers, json=data)
    if response.status_code == 200:
        content = response.json()
        return content['candidates'][0]['content']['parts'][0]['text']
    else:
        raise Exception(f"Gemini API Error {response.status_code}: {response.text}")

def generate_persona_api(profile_url):
    username = extract_username(profile_url)
    posts, comments = fetch_user_activity(username)
    print(posts,comments)
    if not posts and not comments:
        raise Exception("No content found for this user.")
    combined_text = "\n---\n".join(posts + comments)
    prompt = f"""
You are an AI researcher analyzing a Reddit user's activity.

Based on the following Reddit posts and comments, write a detailed user persona for u/{username} including:
- Age (guess if not explicit)
- Occupation (guess if not explicit)
- Status (relationship/family)
- Location (guess if not explicit)
- Tier (e.g. Early Adopter, Mainstream, etc.)
- Archetype (e.g. The Creator, The Analyst, etc.)
- Motivations (list)
- Personality (list)
- Behaviour & Habits (list)
- Goals & Needs (list)
- Frustrations (list)
- A short quote that summarizes the persona's attitude

Return the result as a JSON object with keys: name, age, occupation, status, location, tier, archetype, motivations, personality, behaviour, goals, frustrations, quote.

Reddit activity:
------------------
{combined_text}
"""
    result = call_gemini(prompt)
    import json
    persona = None
    # Try to parse JSON from Gemini, fallback to text parsing if needed
    try:
        persona = json.loads(result)
    except Exception:
        # Try to extract JSON from within markdown code block
        import re
        match = re.search(r'```json([\s\S]*?)```', result)
        if match:
            try:
                persona = json.loads(match.group(1))
            except Exception:
                persona = None
    if not persona:
        persona = {"name": username, "raw": result}
    # Save to personas folder
    os.makedirs("personas", exist_ok=True)
    with open(f"personas/{username}_persona.txt", "w", encoding="utf-8") as f:
        f.write(result)
    return persona
