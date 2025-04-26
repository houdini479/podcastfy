"""
Audio mixing module for Podcastify.
Handles mixing of voice, music, and transition effects.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
from pydub import AudioSegment
import logging

logger = logging.getLogger(__name__)

class AudioMixer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.audio_assets = config.get('audio_assets', {})
        
        # Define base paths
        self.base_dir = Path(__file__).parent
        self.assets_dir = self.base_dir / "assets" / "music"
        self.temp_dir = self.base_dir / "api" / "temp_audio"
        
        # Ensure directories exist
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Load audio assets
        self._load_audio_assets()
    
    def _load_audio_assets(self):
        """Load all audio assets into memory."""
        self.assets = {}
        
        # Load intro music
        if 'intro_music' in self.audio_assets:
            path = self.assets_dir / "intro.mp3"
            if path.exists():
                self.assets['intro'] = AudioSegment.from_file(str(path))
                logger.info(f"Loaded intro music from {path}")
            else:
                logger.warning(f"Intro music not found at {path}")
        
        # Load outro music
        if 'outro_music' in self.audio_assets:
            path = self.assets_dir / "outro.mp3"
            if path.exists():
                self.assets['outro'] = AudioSegment.from_file(str(path))
                logger.info(f"Loaded outro music from {path}")
            else:
                logger.warning(f"Outro music not found at {path}")
        
        # Load transition music
        if 'transitions' in self.audio_assets:
            for section, transition in self.audio_assets['transitions'].items():
                if 'music' in transition:
                    # Convert section name to filename format
                    section_name = section.lower().replace(' ', '_')
                    path = self.assets_dir / f"{section_name}_transition.mp3"
                    if path.exists():
                        self.assets[f'transition_{section_name}'] = AudioSegment.from_file(str(path))
                        logger.info(f"Loaded transition music for {section} from {path}")
                    else:
                        logger.warning(f"Transition music not found at {path}")
    
    def _apply_fade(self, audio: AudioSegment, fade_in: float, fade_out: float) -> AudioSegment:
        """Apply fade in and fade out effects to an audio segment."""
        if fade_in > 0:
            audio = audio.fade_in(int(fade_in * 1000))  # Convert to milliseconds
        if fade_out > 0:
            audio = audio.fade_out(int(fade_out * 1000))
        return audio
    
    def _adjust_volume(self, audio: AudioSegment, volume: float) -> AudioSegment:
        """Adjust the volume of an audio segment."""
        return audio - (20 * (1 - volume))  # Convert volume (0-1) to dB reduction
    
    def mix_transition(self, 
                      main_audio: AudioSegment, 
                      transition_type: str, 
                      announcement: Optional[str] = None) -> AudioSegment:
        """Mix a transition with the main audio."""
        # Convert transition type to match the loaded assets
        transition_key = f"transition_{transition_type.lower().replace(' ', '_')}"
        logger.info(f"Looking for transition: {transition_key}")
        
        if transition_key not in self.assets:
            logger.warning(f"Transition {transition_key} not found in assets. Available transitions: {list(self.assets.keys())}")
            return main_audio
        
        transition = self.assets[transition_key]
        transition_config = self.audio_assets.get('transitions', {}).get(transition_type, {})
        
        # Apply fade and volume adjustments
        transition = self._apply_fade(
            transition,
            transition_config.get('fade_in', 1.0),
            transition_config.get('fade_out', 1.0)
        )
        transition = self._adjust_volume(
            transition,
            transition_config.get('volume', 0.7)
        )
        
        # If there's an announcement, mix it with the transition
        if announcement:
            # Generate announcement audio using TTS
            # This would need to be implemented based on your TTS system
            pass
        
        # Mix the transition with the main audio
        # You might want to adjust the overlap timing here
        logger.info(f"Mixing transition {transition_key} with main audio")
        return main_audio.overlay(transition, position=len(main_audio) - 1000)
    
    def create_podcast(self, 
                      main_audio: AudioSegment, 
                      include_intro: bool = True, 
                      include_outro: bool = True) -> AudioSegment:
        """Create the final podcast with all audio elements."""
        final_audio = main_audio
        
        # Add intro music with overlap
        if include_intro and 'intro' in self.assets:
            intro_config = self.audio_assets['intro_music']
            
            # Get the intro music
            intro = self.assets['intro']
            
            # Apply fade in to intro
            intro = self._apply_fade(
                intro,
                intro_config.get('fade_in', 2.0),
                0  # No fade out yet
            )
            
            # Adjust intro volume
            intro = self._adjust_volume(intro, intro_config.get('volume', 0.8))
            
            # Calculate overlap timing
            overlap_duration = 2000  # 2 seconds of overlap
            fade_out_start = len(intro) - overlap_duration
            
            # Apply fade out to intro during overlap
            intro = intro.fade_out(overlap_duration)
            
            # Create a silent segment for the overlap
            overlap = AudioSegment.silent(duration=overlap_duration)
            
            # Mix the intro with the main audio
            logger.info("Adding intro music with overlap")
            final_audio = intro + overlap + final_audio
        
        # Add outro music
        if include_outro and 'outro' in self.assets:
            outro_config = self.audio_assets['outro_music']
            outro = self._apply_fade(
                self.assets['outro'],
                outro_config.get('fade_in', 2.0),
                outro_config.get('fade_out', 3.0)
            )
            outro = self._adjust_volume(outro, outro_config.get('volume', 0.8))
            logger.info("Adding outro music")
            final_audio = final_audio + outro
        
        return final_audio
    
    def save_audio(self, audio: AudioSegment, filename: str) -> str:
        """Save the mixed audio to a file."""
        output_path = self.temp_dir / filename
        audio.export(str(output_path), format="mp3")
        return str(output_path) 