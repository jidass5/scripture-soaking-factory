# Scripture Soaking Content Factory

Zero-touch automation pipeline for producing therapeutic-grade Christian meditation videos.

## Quick Start

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configure API keys in `.env`:**
    Create a `.env` file in the root directory based on `.env.example` and populate it with your API keys.
    ```
    ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
    GOOGLE_APPLICATION_CREDENTIALS=path/to/your/google_service_account.json
    ```
3.  **Place spiritual spec JSON in `input/spiritual_specs/`:**
    See `input/spiritual_specs/sample_spec.json` for an example.
4.  **Run the factory:**
    ```bash
    python main.py --input input/spiritual_specs/sample_spec.json --duration 8 --output-dir output/
    ```
5.  **Retrieve output:**
    Rendered videos will be in `output/rendered_videos/` and metadata in `output/metadata/`.

## Module Documentation

Each module (`synapse_parser.py`, `vocal_synthesizer.py`, `dsp_engine.py`, `video_assembler.py`, `seo_metadata_injector.py`) contains detailed docstrings explaining its functionality, classes, and methods.

## Troubleshooting

*   **FFmpeg not found:** Install via `sudo apt install ffmpeg`.
*   **ElevenLabs quota exceeded:** Check your API usage dashboard on ElevenLabs.
*   **Memory errors during render:** Reduce video resolution (if possible, though 4K is specified) or ensure sufficient swap space is available.

## License

MIT License - For ministry use only.
