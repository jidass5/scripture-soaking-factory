import argparse
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

from modules.synapse_parser import SynapseParser
from modules.vocal_synthesizer import VocalSynthesizer
from modules.dsp_engine import DSPEngine
from modules.video_assembler import VideoAssembler
from modules.seo_metadata_injector import SEOMetadataInjector

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/production.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ScriptureSoakingFactory")

def run_pipeline(input_spec: str, duration: int, output_dir: str):
    """
    Orchestrates the full content production pipeline.
    """
    logger.info("🚀 Starting Scripture Soaking Factory Pipeline")
    
    try:
        # Stage 1: Parse Spiritual Spec
        logger.info("--- Stage 1: Parsing Spiritual Spec ---")
        parser = SynapseParser(input_spec)
        tasks = parser.create_task_manifest()
        
        # Stage 2: Vocal Synthesis
        logger.info("--- Stage 2: Vocal Synthesis ---")
        synthesizer = VocalSynthesizer()
        vocal_paths = []
        for task in tasks['vocal_tasks']:
            path = synthesizer.synthesize_verse(task['text'], task['emotion'])
            vocal_paths.append(path)
            
        # Stage 3: DSP Processing
        logger.info("--- Stage 3: DSP Processing ---")
        dsp = DSPEngine()
        processed_audio = dsp.process_chain(vocal_paths)
        audio_output_path = "output/temp_processed_audio.wav"
        processed_audio.export(audio_output_path, format="wav")
        
        # Stage 4: Video Assembly
        logger.info("--- Stage 4: Video Assembly ---")
        assembler = VideoAssembler(output_dir=os.path.join(output_dir, "rendered_videos"))
        # Note: In a real run, we need a background video file. 
        # For this script, we assume it exists or use a placeholder.
        bg_video = "assets/visual_loops/default_bg.mp4"
        if not Path(bg_video).exists():
            logger.warning(f"Background video {bg_video} not found. Rendering will fail.")
            # In a real scenario, we might download a default or use a static image
            
        video_path = assembler.render_final_video(
            audio_path=audio_output_path,
            background_path=bg_video,
            duration_hours=duration
        )
        
        # Stage 5: SEO Metadata Generation
        logger.info("--- Stage 5: SEO Metadata Generation ---")
        seo = SEOMetadataInjector()
        metadata = seo.generate_all(tasks, duration)
        
        logger.info(f"✅ Pipeline Complete! Video: {video_path}")
        return video_path, metadata

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scripture Soaking Content Factory Pipeline")
    parser.add_argument("--input", required=True, help="Path to spiritual spec JSON")
    parser.add_argument("--duration", type=int, default=8, help="Target video duration in hours")
    parser.add_argument("--output-dir", default="output/", help="Directory for output files")
    
    args = parser.parse_args()
    
    run_pipeline(args.input, args.duration, args.output_dir)
