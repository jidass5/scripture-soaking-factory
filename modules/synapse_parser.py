import json
import logging
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Verse(BaseModel):
    frequencia_hz: int = Field(..., alias="frequência_hz")
    verso_ingles: str = Field(..., alias="verso_inglês")
    referencia: str = Field(..., alias="referência")
    intencao_emocional: str = Field(..., alias="intenção_emocional")
    analise_fonetica: Dict[str, Any] = Field(default_factory=dict, alias="análise_fonética")
    analise_semantica: Dict[str, Any] = Field(default_factory=dict, alias="análise_semântica")

    class Config:
        populate_by_name = True

class HookStructure(BaseModel):
    duration_seconds: int
    verses: List[Verse]
    sequencia_de_hook: Dict[str, Any] = Field(default_factory=dict, alias="sequência_de_hook")

class SpiritualSpec(BaseModel):
    hook_structure: HookStructure

class SynapseParser:
    """
    Ingests and validates spiritual engineering specs for the content pipeline.
    """
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.data: Optional[SpiritualSpec] = None

    def load_spiritual_spec(self) -> Dict[str, Any]:
        """Loads and validates the JSON spiritual spec."""
        logger.info(f"Loading spiritual spec from {self.file_path}")
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            self.data = SpiritualSpec(**raw_data)
            logger.info("Spiritual spec validated successfully.")
            return self.data.model_dump()
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Failed to load or validate spiritual spec: {e}")
            raise

    def extract_vocal_instructions(self) -> List[Dict[str, Any]]:
        """Extracts instructions for the vocal synthesizer."""
        if not self.data:
            self.load_spiritual_spec()
        
        instructions = []
        for verse in self.data.hook_structure.verses:
            instructions.append({
                "text": verse.verso_ingles,
                "emotion": verse.intencao_emocional,
                "reference": verse.referencia,
                "frequency": verse.frequencia_hz
            })
        return instructions

    def extract_dsp_parameters(self) -> Dict[str, Any]:
        """Extracts parameters for the DSP engine."""
        if not self.data:
            self.load_spiritual_spec()
        
        # Defaulting to 432Hz conversion as per spec
        return {
            "target_frequency": 432,
            "original_frequency": 440,
            "verses_count": len(self.data.hook_structure.verses)
        }

    def create_task_manifest(self) -> Dict[str, Any]:
        """Creates a manifest of tasks for the pipeline."""
        if not self.data:
            self.load_spiritual_spec()
            
        manifest = {
            "vocal_tasks": self.extract_vocal_instructions(),
            "dsp_tasks": self.extract_dsp_parameters(),
            "assembly_tasks": {
                "duration_seconds": self.data.hook_structure.duration_seconds,
                "background_video": "default_loop.mp4" # Placeholder
            }
        }
        
        # Export as pickle for resumption
        pickle_path = self.file_path.with_suffix('.pickle')
        with open(pickle_path, 'wb') as f:
            pickle.dump(manifest, f)
        logger.info(f"Task manifest exported to {pickle_path}")
        
        return manifest
