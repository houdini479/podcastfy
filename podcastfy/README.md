# Podcastify

A podcast generation service that creates engaging audio content with music transitions and professional voice synthesis.

## Features

- Text-to-speech conversion using multiple providers (ElevenLabs, OpenAI, Edge, Gemini)
- Audio mixing with intro/outro music and transitions
- Configurable dialogue structure and style
- Web interface for podcast generation

## Deployment

### Prerequisites

- Python 3.8 or higher
- FFmpeg (required for audio processing)
- Railway account

### Environment Variables

The following environment variables need to be set in Railway:

```
# TTS Provider API Keys
ELEVENLABS_API_KEY=your_elevenlabs_key
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key

# Optional: Custom configuration
PORT=8080
HOST=0.0.0.0
```

### Railway Deployment

1. Connect your GitHub repository to Railway
2. Set up the environment variables in Railway's dashboard
3. Deploy the application

### Local Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables in a `.env` file
5. Run the development server:
   ```bash
   uvicorn api.fast_app:app --reload
   ```

## Project Structure

```
podcastfy/
├── api/
│   └── fast_app.py
├── assets/
│   └── music/
├── data/
│   ├── audio/
│   └── transcripts/
├── frontend/
│   └── index.html
├── requirements.txt
├── conversation_config.yaml
└── README.md
```

## Configuration

The `conversation_config.yaml` file contains all the configuration settings for:
- Podcast style and structure
- Audio assets and transitions
- TTS provider settings
- Dialogue parameters

## License

MIT License 