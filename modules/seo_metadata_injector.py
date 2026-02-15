import logging
import yaml
import json
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class SEOMetadataInjector:
    """
    Generates YouTube-optimized metadata including titles, descriptions,
    tags, and chapter markers.
    """
    def __init__(self, config_path: str = "config/seo_templates.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.templates = self.config['templates']

    def generate_title(self, theme: str, duration: int, frequency: int = 432, audience: str = "Deep Sleep") -> str:
        """Generates a YouTube title based on the template."""
        title = self.templates['title'].format(
            duration=duration,
            theme=theme,
            frequency=frequency,
            audience=audience
        )
        return title[:100] # YouTube limit

    def generate_description(self, verses: List[Dict[str, Any]], duration: int, frequency: int = 432) -> str:
        """Generates a YouTube description with chapter markers."""
        verse_list = ""
        current_time = 0
        for verse in verses:
            minutes, seconds = divmod(current_time, 60)
            hours, minutes = divmod(minutes, 60)
            timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            verse_list += f"{timestamp} - {verse['reference']} | {verse['text'][:30]}...\n"
            current_time += 30 # Estimated 30s per verse for the list
            
        description = self.templates['description'].format(
            duration=duration,
            frequency=frequency,
            verse_list=verse_list
        )
        return description[:5000] # YouTube limit

    def generate_tags(self, frequency: int = 432) -> List[str]:
        """Generates a list of SEO tags."""
        tags = [tag.format(frequency=frequency) for tag in self.templates['tags']]
        return tags

    def export_metadata(self, metadata: Dict[str, Any], output_dir: str = "output/metadata"):
        """Exports metadata to JSON and TXT files."""
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        base_name = "youtube_metadata"
        
        # JSON export
        with open(out_path / f"{base_name}.json", 'w') as f:
            json.dump(metadata, f, indent=4)
            
        # TXT export for manual copy-paste
        with open(out_path / f"{base_name}.txt", 'w') as f:
            f.write(f"TITLE:\n{metadata['title']}\n\n")
            f.write(f"DESCRIPTION:\n{metadata['description']}\n\n")
            f.write(f"TAGS:\n{', '.join(metadata['tags'])}\n")
            
        logger.info(f"Metadata exported to {out_path}")

    def generate_all(self, tasks: Dict[str, Any], duration_hours: int) -> Dict[str, Any]:
        """Orchestrates the generation of all metadata."""
        verses = tasks['vocal_tasks']
        theme = verses[0]['reference'].split(' ')[0] if verses else "Scripture"
        
        metadata = {
            "title": self.generate_title(theme, duration_hours),
            "description": self.generate_description(verses, duration_hours),
            "tags": self.generate_tags()
        }
        
        self.export_metadata(metadata)
        return metadata
