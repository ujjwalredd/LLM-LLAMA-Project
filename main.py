import streamlit as st
import yt_dlp
import whisper
import re
import os
from ollama import chat
import tempfile
import shutil

# Page configuration
st.set_page_config(
    page_title="YouTube Content Analyzer",
    page_icon="🎥",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'youtube_content' not in st.session_state:
    st.session_state.youtube_content = None
if 'content_loaded' not in st.session_state:
    st.session_state.content_loaded = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def extract_youtube_content(video_url):
    """Extract content from YouTube video"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("Processing video...")
    progress_bar.progress(10)
    
    # Try subtitles first
    status_text.text("Trying to extract subtitles...")
    progress_bar.progress(30)
    subtitle_text = get_subtitles(video_url)
    
    if subtitle_text:
        status_text.text("Subtitles extracted successfully!")
        progress_bar.progress(100)
        return subtitle_text
    
    # If no subtitles, transcribe audio
    status_text.text("No subtitles found. Transcribing audio...")
    progress_bar.progress(50)
    audio_text = transcribe_audio(video_url, progress_bar, status_text)
    
    if audio_text:
        status_text.text("Audio transcription completed!")
        progress_bar.progress(100)
        return audio_text
    
    status_text.text("Failed to extract content")
    return None

def get_subtitles(video_url):
    """Extract and clean subtitles"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                'writesubtitles': True,
                'writeautomaticsubs': True,
                'subtitleslangs': ['en'],
                'skip_download': True,
                'outtmpl': os.path.join(temp_dir, 'temp_subtitle.%(ext)s'),
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            subtitle_files = [f for f in os.listdir(temp_dir) if f.startswith('temp_subtitle') and f.endswith('.vtt')]
            
            if not subtitle_files:
                return None
            
            with open(os.path.join(temp_dir, subtitle_files[0]), 'r', encoding='utf-8') as f:
                content = f.read()
            
            return clean_subtitle_text(content)
        
    except Exception as e:
        st.error(f"Subtitle extraction failed: {e}")
        return None

def transcribe_audio(video_url, progress_bar, status_text):
    """Download audio and transcribe"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(temp_dir, 'temp_audio.%(ext)s'),
            }
            
            status_text.text("Downloading audio...")
            progress_bar.progress(60)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            audio_files = [f for f in os.listdir(temp_dir) if f.startswith('temp_audio')]
            
            if not audio_files:
                return None
            
            status_text.text("Loading AI model...")
            progress_bar.progress(70)
            model = whisper.load_model("base")
            
            status_text.text("Transcribing audio...")
            progress_bar.progress(80)
            result = model.transcribe(os.path.join(temp_dir, audio_files[0]))
            
            return result["text"].strip()
        
    except Exception as e:
        st.error(f"Audio transcription failed: {e}")
        return None

def clean_subtitle_text(vtt_content):
    """Clean VTT subtitle content"""
    content = re.sub(r'^WEBVTT.*?\n\n', '', vtt_content, flags=re.MULTILINE | re.DOTALL)
    content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*?\n', '', content)
    content = re.sub(r'<[^>]+>', '', content)
    content = re.sub(r'\[.*?\]', '', content)
    content = re.sub(r'♪.*?♪', '', content)
    content = re.sub(r'\n+', ' ', content)
    content = re.sub(r'\s+', ' ', content)
    return content.strip()

def initialize_with_content(youtube_content):
    """Initialize the conversation with the YouTube content"""
    st.session_state.messages = []
    
    system_msg = {
        "role": "system",
        "content": "You are a YouTube video content assistant. Help users analyze video content, suggest topics, titles, thumbnails, and provide YouTube strategy advice."
    }
    st.session_state.messages.append(system_msg)
    
    content_msg = {
        "role": "user", 
        "content": f"Here is the YouTube content I want you to analyze and remember for our conversation: {youtube_content}"
    }
    st.session_state.messages.append(content_msg)
    
    # Get initial acknowledgment
    try:
        stream = chat(
            model='llama2',
            messages=st.session_state.messages,
            stream=False,
        )
        response = stream['message']['content']
        
        ass_msg = {
            "role": "assistant",
            "content": response
        }
        st.session_state.messages.append(ass_msg)
        st.session_state.content_loaded = True
        
    except Exception as e:
        st.error(f"Failed to initialize chat: {e}")
        return False
    
    return True

def get_ai_response_streaming(user_question, response_container):
    """Get streaming response from AI"""
    user_msg = {
        "role": "user",
        "content": user_question
    }
    st.session_state.messages.append(user_msg)
    
    try:
        stream = chat(
            model='llama2',
            messages=st.session_state.messages,
            stream=True,
        )
        
        full_response = ""
        
        # Stream the response
        for chunk in stream:
            content = chunk['message']['content']
            full_response += content
            response_container.write(full_response)
        
        # Add complete response to messages
        ass_msg = {
            "role": "assistant",
            "content": full_response
        }
        st.session_state.messages.append(ass_msg)
        
        return full_response
        
    except Exception as e:
        error_msg = f"Error getting AI response: {e}"
        response_container.error(error_msg)
        return "Sorry, I encountered an error processing your question."

# Main UI
st.title("YouTube Content Analyzer")
st.write("Analyze YouTube videos and get insights about content, titles, and strategy")

# Sidebar for video input
with st.sidebar:
    st.header("Video Input")
    video_url = st.text_input("Enter YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")
    
    if st.button("Analyze Video", type="primary"):
        if video_url:
            with st.spinner("Processing video..."):
                youtube_content = extract_youtube_content(video_url)
                
                if youtube_content:
                    st.session_state.youtube_content = youtube_content
                    success = initialize_with_content(youtube_content)
                    if success:
                        st.success("Video analyzed successfully!")
                        st.session_state.chat_history = []
                    else:
                        st.error("Failed to initialize chat system")
                else:
                    st.error("Failed to extract content from video")
        else:
            st.warning("Please enter a YouTube URL")
    
    if st.session_state.content_loaded:
        st.success("Content loaded and ready!")
        if st.button("Clear Analysis"):
            st.session_state.content_loaded = False
            st.session_state.youtube_content = None
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.rerun()

# Main content area
if st.session_state.content_loaded and st.session_state.youtube_content:
    # Show content preview
    with st.expander("Content Preview"):
        preview = st.session_state.youtube_content[:500] + "..." if len(st.session_state.youtube_content) > 500 else st.session_state.youtube_content
        st.text_area("Extracted Content:", value=preview, height=200, disabled=True)
        st.write(f"Total content length: {len(st.session_state.youtube_content)} characters")
    
    st.subheader("Ask Questions About Your Video")
    
    # Display chat history
    for i, (question, answer) in enumerate(st.session_state.chat_history):
        with st.container():
            st.write(f"**Q{i+1}:** {question}")
            st.write(f"**A{i+1}:** {answer}")
            st.divider()
    
    # Question input
    with st.form("question_form"):
        user_question = st.text_input("Your question:", placeholder="What is this video about?")
        col1, col2 = st.columns([1, 4])
        
        with col1:
            submit_button = st.form_submit_button("Ask", type="primary")
        
        if submit_button and user_question:
            # Add question to chat history immediately
            st.session_state.chat_history.append((user_question, ""))
            
            # Show the question
            with st.container():
                st.write(f"**Q{len(st.session_state.chat_history)}:** {user_question}")
                st.write(f"**A{len(st.session_state.chat_history)}:**")
                
                # Create container for streaming response
                response_container = st.empty()
                
                # Get streaming response
                response = get_ai_response_streaming(user_question, response_container)
                
                # Update chat history with complete response
                st.session_state.chat_history[-1] = (user_question, response)
    
    # Quick question buttons with streaming
    st.subheader("Quick Questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Summarize this video"):
            question = "Provide a comprehensive summary of this video content"
            st.session_state.chat_history.append((question, ""))
            
            with st.container():
                st.write(f"**Q{len(st.session_state.chat_history)}:** {question}")
                st.write(f"**A{len(st.session_state.chat_history)}:**")
                response_container = st.empty()
                response = get_ai_response_streaming(question, response_container)
                st.session_state.chat_history[-1] = (question, response)
    
    with col2:
        if st.button("Suggest better titles"):
            question = "Suggest 5 better, engaging titles for this video content"
            st.session_state.chat_history.append((question, ""))
            
            with st.container():
                st.write(f"**Q{len(st.session_state.chat_history)}:** {question}")
                st.write(f"**A{len(st.session_state.chat_history)}:**")
                response_container = st.empty()
                response = get_ai_response_streaming(question, response_container)
                st.session_state.chat_history[-1] = (question, response)
    
    with col3:
        if st.button("Key topics covered"):
            question = "What are the main topics and key points covered in this video?"
            st.session_state.chat_history.append((question, ""))
            
            with st.container():
                st.write(f"**Q{len(st.session_state.chat_history)}:** {question}")
                st.write(f"**A{len(st.session_state.chat_history)}:**")
                response_container = st.empty()
                response = get_ai_response_streaming(question, response_container)
                st.session_state.chat_history[-1] = (question, response)

else:
    st.info("Enter a YouTube URL in the sidebar to get started")
    
    st.subheader("How to use:")
    st.write("1. Enter a YouTube video URL in the sidebar")
    st.write("2. Click 'Analyze Video' to extract content")
    st.write("3. Ask questions about the video content")
    st.write("4. Get insights about titles, topics, and strategy")
    
    st.subheader("Features:")
    st.write("- Automatic subtitle extraction")
    st.write("- Audio transcription fallback")
    st.write("- Interactive Q&A about video content")
    st.write("- Quick analysis buttons")
    st.write("- Content preview and statistics")

# Footer
st.divider()