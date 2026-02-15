import os
import logging
import hashlib
import requests
from pathlib import Path
from typing import Optional
from pydub import AudioSegment
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class VocalSynthesizer:
    """
    Synthesizes spiritual verses into therapeutic-grade vocals using ElevenLabs.
    """
    VOICE_MAPPING = {
        "segurança_transferida": "21m00Tcm4TlvDq8ikWAM",  # Rachel (soft, maternal)
        "declaração_de_shalom": "AZnzlk1XhkDPsW8n3W8X",   # Domi (peaceful, steady)
        "passividade_sagrada": "EXAVITQu4vr4xnNLMQbo",    # Bella (gentle, whispered)
    }

    def __init__(self, api_key: Optional[str] = None, cache_dir: str = "assets/cache/vocals"):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.api_key:
            logger.warning("ELEVENLABS_API_KEY not found. Synthesis will fail unless using cache.")

    def select_voice_profile(self, emotion: str) -> str:
        """Maps emotional intention to ElevenLabs voice ID."""
        return self.VOICE_MAPPING.get(emotion, "21m00Tcm4TlvDq8ikWAM") # Default to Rachel

    def apply_prosody_tags(self, text: str) -> str:
        """Applies SSML-like prosody tags for spiritual delivery."""
        # Note: ElevenLabs doesn't support full SSML, but we can simulate pauses
        # and use their stability/similarity settings for tone.
        processed_text = text.replace("...", " <break time=\"800ms\"/> ")
        return processed_text

    def get_cache_path(self, text: str, voice_id: str) -> Path:
        """Generates a unique cache path based on text and voice."""
        hash_key = hashlib.md5(f"{text}{voice_id}".encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.wav"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_elevenlabs(self, text: str, voice_id: str) -> bytes:
        """Internal method to call ElevenLabs API with retry logic."""
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.85
            }
        }
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.content

    def synthesize_verse(self, text: str, emotion: str) -> str:
        """
        Synthesizes a single verse. Returns path to the WAV file.
        """
        voice_id = self.select_voice_profile(emotion)
        cache_path = self.get_cache_path(text, voice_id)
        
        if cache_path.exists():
            logger.info(f"Using cached vocal for: {text[:30]}...")
            return str(cache_path)

        logger.info(f"Synthesizing vocal for: {text[:30]}...")
        if not self.api_key:
            raise ValueError("API Key required for synthesis.")

        audio_data = self._call_elevenlabs(text, voice_id)
        
        # Save as WAV 48kHz, 24-bit (via pydub)
        temp_mp3 = cache_path.with_suffix('.mp3')
        with open(temp_mp3, 'wb') as f:
            f.write(audio_data)
            
        audio = AudioSegment.from_mp3(temp_mp3)
        audio = audio.set_frame_rate(48000).set_sample_width(3).set_channels(1)
        
        # Normalize to -18 LUFS (approximate with dBFS)
        change_in_dbfs = -18.0 - audio.dBFS
        audio = audio.apply_gain(change_in_dbfs)
        
        audio.export(cache_path, format="wav")
        temp_mp3.unlink() # Remove temp file
        
        return str(cache_path)
