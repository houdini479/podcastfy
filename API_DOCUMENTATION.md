# Podcastify API Documentation

## Overview
The Podcastify API provides endpoints for generating and serving podcast content. The API uses FastAPI and is designed to work with the conversation configuration defined in `conversation_config.yaml`.

## Base URL
```
http://your-api-url
```

## Endpoints

### 1. Generate Podcast
Generates a podcast based on provided configuration and content.

**Endpoint:** `POST /generate`

**Request Body:**
```json
{
  "name": "string",
  "tagline": "string",
  "conversation_style": ["string"],
  "roles_person1": "string",
  "roles_person2": "string",
  "dialogue_structure": ["string"],
  "output_language": "string",
  "engagement_techniques": ["string"],
  "creativity": float,
  "user_instructions": "string",
  "tts_model": "string",
  "voices": {
    "question": "string",
    "answer": "string"
  },
  "is_long_form": boolean,
  "urls": ["string"],
  "url_file": "string",
  "transcript_file": "string",
  "transcript_only": boolean,
  "config": object,
  "image_paths": ["string"],
  "is_local": boolean,
  "text": "string",
  "llm_model_name": "string",
  "api_key_label": "string",
  "topic": "string"
}
```

**Required Fields:**
- `name`: Name of the podcast
- `tagline`: Tagline for the podcast
- `conversation_style`: Array of conversation styles
- `roles_person1`: Role of the first person
- `roles_person2`: Role of the second person
- `dialogue_structure`: Array of dialogue sections
- `output_language`: Language for output
- `engagement_techniques`: Array of engagement techniques
- `creativity`: Float between 0.0 and 1.0
- `user_instructions`: Detailed instructions for content generation
- `tts_model`: Text-to-speech model to use
- `voices`: Voice configurations for speakers

**Optional Fields:**
- `is_long_form`: Boolean for long-form content
- `urls`: Array of URLs to process
- `url_file`: Path to file containing URLs
- `transcript_file`: Path to transcript file
- `transcript_only`: Boolean to generate only transcript
- `config`: Additional configuration object
- `image_paths`: Array of image paths
- `is_local`: Boolean for local file processing
- `text`: Direct text input
- `llm_model_name`: Language model to use
- `api_key_label`: API key identifier
- `topic`: Main topic for the podcast

**Response:**
```json
{
  "audioUrl": "string"
}
```

**Example Request:**
```json
{
  "name": "The Goose Report",
  "tagline": "One honk a day keeps the chaos away.",
  "conversation_style": ["engaging", "fast-paced", "enthusiastic"],
  "roles_person1": "host",
  "roles_person2": "co-host",
  "dialogue_structure": ["Introduction", "Settled Vitals", "Deep Dive", "Closing"],
  "output_language": "English",
  "engagement_techniques": ["rhetorical questions", "anecdotes", "analogies", "humor"],
  "creativity": 1.0,
  "user_instructions": "This is an internal daily podcast for Settled Technologies...",
  "tts_model": "elevenlabs",
  "voices": {
    "question": "Chris",
    "answer": "Mark - Natural Conversations"
  },
  "is_long_form": false
}
```

### 2. Serve Audio
Serves the generated audio file.

**Endpoint:** `GET /audio/{filename}`

**Parameters:**
- `filename`: Name of the audio file to serve

**Response:**
- Audio file as FileResponse

### 3. Health Check
Checks the health of the API.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy"
}
```

## Configuration Reference

The API uses configuration from `conversation_config.yaml`. Here are the key configuration options:

### Text-to-Speech Models
```yaml
text_to_speech:
  default_tts_model: "elevenlabs"
  elevenlabs:
    default_voices:
      question: "Chris"
      answer: "Mark - Natural Conversations"
    model: "eleven_multilingual_v2"
  openai:
    default_voices:
      question: "echo"
      answer: "shimmer"
    model: "tts-1-hd"
  edge:
    default_voices:
      question: "en-US-JennyNeural"
      answer: "en-US-EricNeural"
  gemini:
    default_voices:
      question: "en-US-Journey-D"
      answer: "en-US-Journey-O"
```

### Content Structure
```yaml
conversation_style: 
  - "engaging"
  - "fast-paced"
  - "enthusiastic"
roles_person1: "host"
roles_person2: "co-host"
dialogue_structure: 
  - "Introduction"
  - "Settled Vitals"
  - "Deep Dive"
  - "Closing"
```

## Usage Examples

### 1. Basic Podcast Generation
```python
import requests

url = "http://your-api-url/generate"
data = {
    "name": "The Goose Report",
    "tagline": "One honk a day keeps the chaos away.",
    "conversation_style": ["engaging", "fast-paced", "enthusiastic"],
    "roles_person1": "host",
    "roles_person2": "co-host",
    "dialogue_structure": ["Introduction", "Settled Vitals", "Deep Dive", "Closing"],
    "output_language": "English",
    "engagement_techniques": ["rhetorical questions", "anecdotes", "analogies", "humor"],
    "creativity": 1.0,
    "user_instructions": "This is an internal daily podcast for Settled Technologies...",
    "tts_model": "elevenlabs",
    "voices": {
        "question": "Chris",
        "answer": "Mark - Natural Conversations"
    }
}

response = requests.post(url, json=data)
audio_url = response.json()["audioUrl"]
```

### 2. Long-form Podcast with Custom Content
```python
import requests

url = "http://your-api-url/generate"
data = {
    "name": "The Goose Report",
    "tagline": "One honk a day keeps the chaos away.",
    "conversation_style": ["engaging", "fast-paced", "enthusiastic"],
    "roles_person1": "host",
    "roles_person2": "co-host",
    "dialogue_structure": ["Introduction", "Settled Vitals", "Deep Dive", "Closing"],
    "output_language": "English",
    "engagement_techniques": ["rhetorical questions", "anecdotes", "analogies", "humor"],
    "creativity": 1.0,
    "is_long_form": True,
    "user_instructions": """
    This is an internal daily podcast for Settled Technologies...
    
    Introduction:
    - Welcome to today's episode
    - Special announcement about new partnership
    
    Settled Vitals:
    - Active users: 10,000
    - Resolution rate: 85%
    - Customer satisfaction: 4.8/5
    
    Deep Dive:
    Topic: New Partnership with Airline X
    Key Points:
    - Strategic benefits
    - Implementation timeline
    - Expected impact on user base
    
    Closing:
    - Motivational message about innovation
    - Next steps and deadlines
    """,
    "tts_model": "elevenlabs",
    "voices": {
        "question": "Chris",
        "answer": "Mark - Natural Conversations"
    }
}

response = requests.post(url, json=data)
audio_url = response.json()["audioUrl"]
```

### 3. Transcript-only Generation
```python
import requests

url = "http://your-api-url/generate"
data = {
    "name": "The Goose Report",
    "tagline": "One honk a day keeps the chaos away.",
    "conversation_style": ["engaging", "fast-paced", "enthusiastic"],
    "roles_person1": "host",
    "roles_person2": "co-host",
    "dialogue_structure": ["Introduction", "Settled Vitals", "Deep Dive", "Closing"],
    "output_language": "English",
    "engagement_techniques": ["rhetorical questions", "anecdotes", "analogies", "humor"],
    "creativity": 1.0,
    "transcript_only": True,
    "user_instructions": "This is an internal daily podcast for Settled Technologies...",
    "tts_model": "elevenlabs",
    "voices": {
        "question": "Chris",
        "answer": "Mark - Natural Conversations"
    }
}

response = requests.post(url, json=data)
transcript = response.json()["transcript"]
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

Error response format:
```json
{
  "detail": "Error message"
}
```

## Best Practices

1. **Content Structure**
   - Follow the dialogue structure defined in the configuration
   - Provide clear, well-organized content in the `user_instructions`
   - Use appropriate creativity levels based on content type

2. **Voice Selection**
   - Choose appropriate TTS model based on language and voice requirements
   - Test different voice combinations for optimal results
   - Consider using different voices for different roles

3. **Error Handling**
   - Implement proper error handling for API calls
   - Check response status codes
   - Handle timeouts and network issues

4. **Performance**
   - Use appropriate `is_long_form` setting based on content length
   - Consider using `transcript_only` for testing
   - Cache generated audio files when possible 