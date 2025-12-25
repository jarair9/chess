import streamlit as st
import os
import json
import uuid
import sys
import importlib.util

# Add src to path to allow imports
sys.path.append(os.path.abspath("src"))

from lib.python import helpers
from lib.python import trivia as trivia_module
from lib.python.chess import puzzle as puzzle_module
from lib.python.logger import MoviePyStreamlitLogger

st.set_page_config(page_title="JA Studio", layout="wide", page_icon="🎬")

# Custom CSS for styling
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
    }
    .stVideo {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.title("JA Studio 🎬")

# Tabs
tab_generate, tab_feed, tab_library = st.tabs(["✨ Generate", "📺 Feed", "📚 PGN Library"])

# --- Generate Tab ---
with tab_generate:
    st.header("Produce Short")
    
    short_type = st.selectbox("Short Type", ["Trivia", "Chess Puzzle"])
    
    if short_type == "Trivia":
        questions_data = helpers.load_trivia_questions()
        categories = list(questions_data.keys())
        category = st.selectbox("Category", categories)
        
        if st.button("✨ PRODUCE TRIVIA SHORT"):
            with st.spinner("Generating Trivia Short..."):
                try:
                    # 1. Get Resources
                    questions = helpers.get_random_trivia_questions(category)
                    music_path = helpers.get_random_music("lofi")
                    
                    if not questions:
                        st.error("No questions found for this category.")
                    elif not music_path:
                        st.error("No music found.")
                    else:
                        # 2. Setup Paths
                        output_filename = f"{uuid.uuid4()}.mp4"
                        output_path = os.path.join("out", output_filename)
                        if not os.path.exists("out"):
                            os.makedirs("out")

                        # 3. Call Generation Logic
                        # Trivia module expects dicts for questions, which we have from json
                        prog_bar = st.progress(0, text="Rendering video...")
                        logger = MoviePyStreamlitLogger(progress_bar=prog_bar, label_widget=st.empty())

                        trivia_module.produce_short(
                            questions=questions,
                            background="src/resources/parkour.mp4",
                            music=music_path,
                            font="src/resources/default.ttf",
                            output=output_path,
                            logger=logger
                        )
                        
                        prog_bar.empty()

                        # 4. Update DB
                        helpers.add_video_to_db(output_filename, "trivia", "Trivia Short")
                        st.success(f"Generated: {output_filename}")
                        st.session_state.last_video = output_path
                        
                except Exception as e:
                    st.error(f"Error producing video: {e}")
                    import traceback
                    st.text(traceback.format_exc())

    elif short_type == "Chess Puzzle":
        # Load Phonk tracks for drops
        phonk_tracks_path = os.path.join("src", "resources", "music", "phonk", "tracks.json")
        try:
            with open(phonk_tracks_path, "r") as f:
                phonk_tracks = json.load(f)
        except:
            phonk_tracks = []
            
        pgn_input = st.text_area("PGN (leave empty for random)", height=150)
        
        # Player selection for random game
        # We need to bridge the PGN library logic here.
        # The TS version used 'src/lib/pgn/library.ts' which reads from 'games' folder.
        # We can implement a simple python version or rely on user pasting PGN.
        # For now, let's allow pasting.
        
        if st.button("✨ PRODUCE PUZZLE SHORT"):
             with st.spinner("Generating Chess Puzzle..."):
                try:
                    import chess.pgn
                    import io
                    import random
                    
                    final_pgn = pgn_input.strip()
                    
                    # If empty, try to pick a random game from 'games' dir if possible
                    if not final_pgn:
                        games_dir = os.path.join("games")
                        if os.path.exists(games_dir):
                            pgn_files = [f for f in os.listdir(games_dir) if f.endswith(".pgn")]
                            if pgn_files:
                                selected_file = random.choice(pgn_files)
                                with open(os.path.join(games_dir, selected_file), "r") as f:
                                    # Read one game? or all? Assuming one per file or we pick random
                                    # Simulating the library logic: just read the whole file text
                                    final_pgn = f.read()
                    
                    if not final_pgn:
                        st.error("Please provide a PGN or ensure 'games/' directory has PGN files.")
                    else:
                         # 2. Get Music
                        track = random.choice(phonk_tracks) if phonk_tracks else None
                        if not track:
                             st.error("No phonk tracks found.")
                        else:
                            music_filename = track["filename"]
                            music_drop = track["dropTime"]
                            music_path = f"src/resources/music/phonk/{music_filename}"
                            
                            # 3. Setup Paths
                            output_filename = f"{uuid.uuid4()}.mp4"
                            output_path = os.path.join("out", output_filename)
                            if not os.path.exists("out"):
                                os.makedirs("out")
                                
                            # 4. Call Generation Logic
                            prog_bar = st.progress(0, text="Rendering video...")
                            logger = MoviePyStreamlitLogger(progress_bar=prog_bar, label_widget=st.empty())

                            puzzle_module.produce_short(
                                output=output_path,
                                game_pgn=final_pgn,
                                background="src/resources/gridbackground.png",
                                font="src/resources/default.ttf",
                                music=music_path,
                                music_drop_time=music_drop,
                                logger=logger
                            )
                            
                            prog_bar.empty()
                            
                            # 5. Update DB
                            helpers.add_video_to_db(output_filename, "chess/puzzle", "Chess Puzzle Short")
                            st.success(f"Generated: {output_filename}")
                            st.session_state.last_video = output_path

                except Exception as e:
                    st.error(f"Error producing video: {e}")
                    import traceback
                    st.text(traceback.format_exc())

    if "last_video" in st.session_state and os.path.exists(st.session_state.last_video):
        st.subheader("Preview")
        col_prev, _ = st.columns([0.4, 0.6])
        with col_prev:
            st.video(st.session_state.last_video)


# --- Feed Tab ---
with tab_feed:
    st.header("Video Feed")
    
    if st.button("🔄 Refresh Feed"):
        helpers.sync_db()
        st.rerun()

    # Load videos
    helpers.sync_db() # Sync on load
    videos = helpers.load_db()
    # Sort by date desc
    videos.sort(key=lambda x: x.get("date", ""), reverse=True)
    
    if not videos:
        st.info("No videos found. Generate some!")
    
    for video in videos:
        col_info, col_del = st.columns([0.85, 0.15])
        with col_info:
             st.subheader(video.get("title", "Untitled"))
             st.caption(f"Filename: {video['filename']} | Date: {video.get('date', 'Unknown')}")
        with col_del:
             if st.button("🗑️ Delete", key=f"del_{video['id']}"):
                helpers.delete_video(video['filename'])
                st.rerun()

        file_path = os.path.join("out", video['filename'])
        if os.path.exists(file_path):
            col_vid, _ = st.columns([0.4, 0.6])
            with col_vid:
                st.video(file_path)
        else:
            st.error("File not found on disk.")
        
        st.divider()

# --- Library Tab ---
with tab_library:
    st.header("PGN Library")
    
    # 1. Upload
    uploaded_file = st.file_uploader("Upload PGN", type=["pgn"])
    if uploaded_file is not None:
        save_path = os.path.join("games", uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded {uploaded_file.name}")
        st.rerun()
        
    st.divider()
    
    # 2. List Files
    if not os.path.exists("games"):
        os.makedirs("games")
        
    pgn_files = [f for f in os.listdir("games") if f.endswith(".pgn")]
    if not pgn_files:
        st.info("No PGN files found in 'games/' directory.")
    else:
        for pgn_file in pgn_files:
            col_name, col_action = st.columns([0.8, 0.2])
            
            with col_name:
                file_path = os.path.join("games", pgn_file)
                size_kb = os.path.getsize(file_path) / 1024
                st.write(f"📄 **{pgn_file}** ({size_kb:.1f} KB)")
                
                with st.expander("Preview"):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read(1000)
                            st.code(content + ("..." if len(content) == 1000 else ""), language="text")
                    except Exception as e:
                        st.error(f"Error reading file: {e}")

            with col_action:
                if st.button("🗑️", key=f"del_pgn_{pgn_file}"):
                    os.remove(os.path.join("games", pgn_file))
                    st.rerun()
            
            st.divider()
