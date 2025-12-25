import json
import os
import random
import uuid
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(BASE_DIR, "out")
DB_PATH = os.path.join(DATA_DIR, "db.json")
TRIVIA_QUESTIONS_PATH = os.path.join(BASE_DIR, "src", "resources", "trivia", "questions.json")
MUSIC_DIR = os.path.join(BASE_DIR, "src", "resources", "music")

def load_trivia_questions():
    """Loads trivia questions from JSON file."""
    with open(TRIVIA_QUESTIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_random_trivia_questions(category, count=3):
    """Selects random trivia questions from a category."""
    questions_data = load_trivia_questions()
    if category not in questions_data:
        return []
    
    questions = questions_data[category]
    if len(questions) < count:
        return questions 
    
    return random.sample(questions, count)

def get_random_music(genre="lofi"):
    """Picks a random track from the specified genre folder."""
    genre_dir = os.path.join(MUSIC_DIR, genre)
    if not os.path.exists(genre_dir):
        return None
    
    tracks = [f for f in os.listdir(genre_dir) if f.endswith(".mp3")]
    if not tracks:
        return None
        
    return os.path.join("src/resources/music", genre, random.choice(tracks))

def load_db():
    """Loads the video database."""
    if not os.path.exists(DB_PATH):
        return []
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_db(data):
    """Saves the video database."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def add_video_to_db(filename, video_type, title):
    """Adds a new video entry to the database."""
    videos = load_db()
    new_video = {
        "id": str(uuid.uuid4()),
        "filename": filename,
        "type": video_type,
        "date": datetime.now().isoformat(),
        "title": title
    }
    videos.append(new_video)
    save_db(videos)

def delete_video(filename):
    """Deletes a video from disk and the database."""
    # Remove from Disk
    file_path = os.path.join(OUT_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Remove from DB
    videos = load_db()
    videos = [v for v in videos if v["filename"] != filename]
    save_db(videos)

def sync_db():
    """Syncs the database with files in the out directory."""
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
        
    files = [f for f in os.listdir(OUT_DIR) if f.endswith(".mp4")]
    videos = load_db()
    db_filenames = [v["filename"] for v in videos]
    
    changed = False
    
    # Add missing files
    for f in files:
        if f not in db_filenames:
            videos.append({
                "id": str(uuid.uuid4()),
                "filename": f,
                "type": "legacy",
                "date": datetime.now().isoformat(),
                "title": "Legacy Video"
            })
            changed = True
            
    # Remove missing entries
    existing_videos = [v for v in videos if v["filename"] in files]
    if len(existing_videos) != len(videos):
        videos = existing_videos
        changed = True
        
    if changed:
        save_db(videos)
        
    return videos
