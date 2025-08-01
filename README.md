# YouTube Content Analyzer

A powerful web application that extracts content from YouTube videos and provides AI-powered analysis, insights, and suggestions for content creators.

## Features

- **Content Extraction**: Automatically extracts subtitles or transcribes audio from YouTube videos
- **AI Analysis**: Get insights about video content, topics, and themes
- **Content Strategy**: Receive suggestions for better titles, thumbnails, and content strategy
- **Real-time Responses**: Stream AI responses in real-time for better user experience
- **Clean Interface**: Simple, user-friendly web interface built with Streamlit

## Demo

![YouTube Content Analyzer Demo](demo.gif)

## Installation

### Prerequisites

- Python 3.8 or higher
- Ollama installed and running locally
- FFmpeg (for audio processing)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/youtube-content-analyzer.git
   cd youtube-content-analyzer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Ollama**
   - Download and install Ollama from [https://ollama.ai](https://ollama.ai)
   - Pull the required model:
     ```bash
     ollama pull llama2
     ```

4. **Install FFmpeg**
   - **Windows**: Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

## Usage

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser**
   - Navigate to `http://localhost:8501`

3. **Analyze a video**
   - Enter a YouTube URL in the sidebar
   - Click "Analyze Video"
   - Wait for content extraction and processing

4. **Ask questions**
   - Use the text input to ask specific questions
   - Try the quick action buttons for common tasks
   - Watch responses stream in real-time

## How It Works

### Content Extraction Process

1. **Subtitle Extraction**: Attempts to download existing subtitles (fastest method)
2. **Audio Transcription**: If no subtitles available, downloads audio and uses Whisper AI for transcription
3. **Content Cleaning**: Removes timestamps, HTML tags, and formatting artifacts
4. **AI Analysis**: Feeds cleaned content to local Ollama model for analysis

### AI Integration

- Uses Ollama with Llama2 model for local AI processing
- Maintains conversation context for follow-up questions
- Streams responses in real-time for better user experience

## File Structure

```
youtube-content-analyzer/
│
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── demo.gif              # Demo animation (optional)
└── .gitignore            # Git ignore file
```

## Configuration

### Model Selection

You can change the AI model by modifying the model parameter in the `chat()` function:

```python
stream = chat(
    model='llama2',  # Change to other Ollama models
    messages=st.session_state.messages,
    stream=True,
)
```

Available models (requires pulling with Ollama):
- `llama2` (default)
- `codellama`
- `mistral`
- `phi`

### Whisper Model

You can adjust the Whisper model for different accuracy/speed trade-offs:

```python
model = whisper.load_model("base")  # Options: tiny, base, small, medium, large
```

## API Limits and Considerations

- **YouTube**: No API key required, but respect rate limits
- **Processing Time**: Large videos may take several minutes to process
- **Storage**: Temporary files are automatically cleaned up
- **Privacy**: All processing happens locally on your machine

## Troubleshooting

### Common Issues

1. **Ollama not found**
   ```
   Error: Ollama not responding
   ```
   - Ensure Ollama is installed and running
   - Check if the model is pulled: `ollama list`

2. **FFmpeg not found**
   ```
   Error: ffmpeg not found
   ```
   - Install FFmpeg and ensure it's in your PATH
   - Restart your terminal after installation

3. **Video extraction fails**
   ```
   Error: Failed to extract content
   ```
   - Check if the YouTube URL is valid and accessible
   - Some videos may have restricted access
   - Try a different video

4. **Memory issues with large videos**
   - Use smaller Whisper models (`tiny` or `base`)
   - Process shorter video segments
   - Increase system RAM if possible

### Debug Mode

Enable debug output by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Roadmap

- [ ] Support for multiple languages
- [ ] Batch processing of multiple videos
- [ ] Export analysis results to PDF/JSON
- [ ] Integration with other AI models (OpenAI, Claude)
- [ ] Video thumbnail analysis
- [ ] Sentiment analysis of comments
- [ ] SEO optimization suggestions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Streamlit](https://streamlit.io/) for the web framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube content extraction
- [OpenAI Whisper](https://github.com/openai/whisper) for audio transcription
- [Ollama](https://ollama.ai/) for local AI model hosting

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/youtube-content-analyzer/issues) page
2. Create a new issue with detailed description
3. Include error messages and system information

## Disclaimer

This tool is for educational and content analysis purposes. Please respect YouTube's Terms of Service and copyright laws when using this application.
