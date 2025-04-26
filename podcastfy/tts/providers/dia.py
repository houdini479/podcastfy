"""Dia TTS provider implementation."""

import os
import replicate
import requests
from typing import List, Tuple
from ..base import TTSProvider

class DiaTTS(TTSProvider):
    """Dia TTS provider implementation."""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize Dia TTS provider.
        
        Args:
            api_key: Not used for Dia (uses REPLICATE_API_TOKEN env var)
            model: Optional model ID/name to use
        """
        # Verify API token is set
        if not os.getenv("REPLICATE_API_TOKEN"):
            raise ValueError("REPLICATE_API_TOKEN environment variable must be set")
            
        self.model = model or "zsxkib/dia:46ad4a48b01c6d8b7366cbef1ae6d518f6a56c246b6ae831665e92ad923dd21b"
        self.model_params = {
            "cfg_scale": 4,
            "temperature": 1.3,
            "speed_factor": 0.94,
            "top_p": 0.95,
            "max_new_tokens": 3072,
            "cfg_filter_top_k": 35
        }

    def generate_audio(self, text: str, voice: str = "S1", model: str = None, voice2: str = "S2") -> bytes:
        """
        Generate audio from text using Dia's API.
        
        Args:
            text: Text to convert to speech
            voice: Voice ID for first speaker (S1)
            model: Not used for Dia (uses self.model)
            voice2: Voice ID for second speaker (S2)
            
        Returns:
            Audio data as bytes
            
        Raises:
            ValueError: If invalid parameters are provided
            RuntimeError: If audio generation fails
        """
        # Convert Person1/Person2 tags to S1/S2 format
        dia_text = self._convert_to_dia_format(text)
        
        # Prepare input for Dia
        input_data = {
            "text": dia_text,
            **self.model_params
        }
        
        try:
            # Run the model using the full model ID from initialization
            output_url = replicate.run(
                self.model,  # Use the full model ID from initialization
                input=input_data
            )
            
            # Download the audio from the URL
            response = requests.get(output_url)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Return the audio data
            return response.content
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate audio with Dia: {str(e)}")

    def _convert_to_dia_format(self, text: str) -> str:
        """
        Convert Person1/Person2 tags to Dia's S1/S2 format.
        
        Args:
            text: Input text with Person1/Person2 tags
            
        Returns:
            Text formatted for Dia
        """
        # Replace Person1/Person2 tags with S1/S2
        text = text.replace("<Person1>", "[S1]")
        text = text.replace("</Person1>", "")
        text = text.replace("<Person2>", "[S2]")
        text = text.replace("</Person2>", "")
        
        # Convert emotion tags to Dia format
        text = self._convert_emotion_tags(text)
        
        return text

    def _convert_emotion_tags(self, text: str) -> str:
        """
        Convert emotion tags to Dia's format.
        
        Args:
            text: Input text with emotion tags
            
        Returns:
            Text with emotions in Dia format
        """
        # Convert <emotion type="X"> to (X)
        text = text.replace('<emotion type="', '(')
        text = text.replace('">', ')')
        text = text.replace('</emotion>', '')
        
        # Convert <prosody> tags to Dia format
        text = text.replace('<prosody rate="slow" pitch="low">', '(slow, low)')
        text = text.replace('<prosody rate="fast" pitch="high">', '(fast, high)')
        text = text.replace('<prosody volume="soft">', '(soft)')
        text = text.replace('<prosody volume="loud">', '(loud)')
        text = text.replace('</prosody>', '')
        
        return text

    def get_supported_tags(self) -> List[str]:
        """
        Get set of SSML tags supported by Dia.
        
        Returns:
            Set of supported SSML tag names
        """
        return self.COMMON_SSML_TAGS.copy() 