"""
FastAPI implementation for Podcastify podcast generation service.

This module provides REST endpoints for podcast generation and audio serving,
with configuration management and temporary file handling.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import yaml
from typing import Dict, Any
from pathlib import Path
from podcastfy.client import generate_podcast
from podcastfy.audio_mixer import AudioMixer
import uvicorn
import logging
from pydub import AudioSegment
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define base paths
BASE_DIR = Path(__file__).parent.parent
TEMP_DIR = BASE_DIR / "api" / "temp_audio"
ASSETS_DIR = BASE_DIR / "assets" / "music"

# Ensure directories exist
TEMP_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

def load_base_config() -> Dict[Any, Any]:
    config_path = BASE_DIR / "conversation_config.yaml"
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Warning: Could not load base config: {e}")
        return {}

def merge_configs(base_config: Dict[Any, Any], user_config: Dict[Any, Any]) -> Dict[Any, Any]:
    """Merge user configuration with base configuration, preferring user values."""
    merged = base_config.copy()
    
    # Handle special cases for nested dictionaries
    if 'text_to_speech' in merged and 'text_to_speech' in user_config:
        merged['text_to_speech'].update(user_config.get('text_to_speech', {}))
    
    # Update top-level keys
    for key, value in user_config.items():
        if key != 'text_to_speech':  # Skip text_to_speech as it's handled above
            if value is not None:  # Only update if value is not None
                merged[key] = value
                
    return merged

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate")
async def generate_podcast_endpoint(data: dict):
    try:
        logger.info(f"Received generate request with data: {data}")
        
        # Load base configuration
        base_config = load_base_config()
        logger.info(f"Loaded base config: {base_config}")
        
        # Get TTS model and its configuration from base config
        tts_model = data.get('tts_model', base_config.get('text_to_speech', {}).get('default_tts_model', 'openai'))
        tts_base_config = base_config.get('text_to_speech', {}).get(tts_model, {})
        logger.info(f"Using TTS model: {tts_model} with config: {tts_base_config}")
        
        # Get voices (use user-provided voices or fall back to defaults)
        voices = data.get('voices', {})
        default_voices = tts_base_config.get('default_voices', {})
        logger.info(f"Using voices: {voices} with defaults: {default_voices}")
        
        # Prepare user configuration
        user_config = {
            'creativity': float(data.get('creativity', base_config.get('creativity', 0.7))),
            'conversation_style': data.get('conversation_style', base_config.get('conversation_style', [])),
            'roles_person1': data.get('roles_person1', base_config.get('roles_person1')),
            'roles_person2': data.get('roles_person2', base_config.get('roles_person2')),
            'dialogue_structure': data.get('dialogue_structure', base_config.get('dialogue_structure', [])),
            'podcast_name': data.get('name', base_config.get('podcast_name')),
            'podcast_tagline': data.get('tagline', base_config.get('podcast_tagline')),
            'output_language': data.get('output_language', base_config.get('output_language', 'English')),
            'user_instructions': data.get('user_instructions', base_config.get('user_instructions', '')),
            'engagement_techniques': data.get('engagement_techniques', base_config.get('engagement_techniques', [])),
            'text_to_speech': {
                'default_tts_model': tts_model,
                'model': tts_base_config.get('model'),
                'default_voices': {
                    'question': voices.get('question', default_voices.get('question')),
                    'answer': voices.get('answer', default_voices.get('answer'))
                }
            }
        }
        logger.info(f"Prepared user config: {user_config}")

        # Merge configurations
        conversation_config = merge_configs(base_config, user_config)
        logger.info(f"Merged conversation config: {conversation_config}")

        # Generate podcast with all possible input types
        logger.info("Starting podcast generation...")
        result = generate_podcast(
            urls=data.get('urls', []),
            url_file=data.get('url_file'),
            transcript_file=data.get('transcript_file'),
            tts_model=tts_model,
            transcript_only=data.get('transcript_only', False),
            config=data.get('config'),
            conversation_config=conversation_config,
            image_paths=data.get('image_paths', []),
            is_local=data.get('is_local', False),
            text=data.get('text'),
            llm_model_name=data.get('llm_model_name'),
            api_key_label=data.get('api_key_label'),
            topic=data.get('topic'),
            longform=bool(data.get('is_long_form', False))
        )
        logger.info(f"Podcast generation result: {result}")
        
        # Handle the result and add music/transitions
        if isinstance(result, str) and os.path.isfile(result):
            # Initialize audio mixer
            audio_mixer = AudioMixer(conversation_config)
            
            # Load the generated audio
            main_audio = AudioSegment.from_file(result)
            
            # Add transitions between sections
            for section in conversation_config.get('dialogue_structure', []):
                if section.lower() in ['settled vitals', 'deep dive', 'closing']:
                    transition_type = f"transition_{section.lower().replace(' ', '_')}"
                    announcement = conversation_config.get('audio_assets', {}).get('transitions', {}).get(transition_type, {}).get('announcement')
                    main_audio = audio_mixer.mix_transition(main_audio, transition_type, announcement)
            
            # Create final podcast with intro and outro
            final_audio = audio_mixer.create_podcast(main_audio)
            
            # Save the final audio
            podcast_title = conversation_config.get('podcast_name', 'podcast').replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{podcast_title}_{timestamp}.mp3"
            output_path = TEMP_DIR / filename
            final_audio.export(str(output_path), format="mp3")
            
            logger.info(f"Generated audio file with music and transitions: {output_path}")
            return {"audioUrl": f"/audio/{filename}"}
        elif hasattr(result, 'audio_path'):
            # Initialize audio mixer
            audio_mixer = AudioMixer(conversation_config)
            
            # Load the generated audio
            main_audio = AudioSegment.from_file(result.audio_path)
            
            # Add transitions between sections
            for section in conversation_config.get('dialogue_structure', []):
                if section.lower() in ['settled vitals', 'deep dive', 'closing']:
                    transition_type = f"transition_{section.lower().replace(' ', '_')}"
                    announcement = conversation_config.get('audio_assets', {}).get('transitions', {}).get(transition_type, {}).get('announcement')
                    main_audio = audio_mixer.mix_transition(main_audio, transition_type, announcement)
            
            # Create final podcast with intro and outro
            final_audio = audio_mixer.create_podcast(main_audio)
            
            # Save the final audio
            podcast_title = conversation_config.get('podcast_name', 'podcast').replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{podcast_title}_{timestamp}.mp3"
            output_path = TEMP_DIR / filename
            final_audio.export(str(output_path), format="mp3")
            
            logger.info(f"Generated audio file with music and transitions: {output_path}")
            return {"audioUrl": f"/audio/{filename}"}
        else:
            logger.error(f"Invalid result format: {result}")
            raise HTTPException(status_code=500, detail="Invalid result format")

    except Exception as e:
        logger.error(f"Error in generate_podcast_endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio/{filename}")
async def serve_audio(filename: str):
    """Serve audio file from the server"""
    file_path = TEMP_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(file_path))

@app.get("/health")
async def healthcheck():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")  # Changed default to 0.0.0.0
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level="info",
        access_log=True,
        use_colors=True
    )
