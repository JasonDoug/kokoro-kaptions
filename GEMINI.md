# kokoro-kaptions Project Context

## Project Overview
kokoro-kaptions is a high-performance, containerized FastAPI wrapper for the [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) text-to-speech model. It provides an OpenAI-compatible speech endpoint and extends it with features like multi-language support, voice mixing (weighted combinations), per-word timestamped caption generation, and phoneme-based audio generation.

### Key Technologies
- **Framework:** FastAPI
- **Inference Engine:** PyTorch (supporting CUDA, ROCm, and CPU)
- **Dependency Management:** [astral-uv](https://docs.astral.sh/uv/)
- **Configuration:** Pydantic Settings with `.env` support
- **Logging:** Loguru
- **Containerization:** Docker & Docker Compose

### Architecture
- `api/src/main.py`: Entry point and FastAPI app initialization.
- `api/src/routers/`: API route definitions.
    - `openai_compatible.py`: Implements `/v1/audio/speech` and related OpenAI endpoints.
    - `development.py`: Specialized endpoints for phonemes, captions, and direct generation.
    - `debug.py`: System health and resource monitoring.
- `api/src/inference/`: Core TTS logic.
    - `model_manager.py`: Handles model lifecycle, initialization, and warming up.
    - `voice_manager.py`: Manages voice packs and weighted mixing.
    - `kokoro_v1.py`: Implementation of the Kokoro v1.0 inference pipeline.
- `api/src/core/`: Core configuration and utility logic.
- `web/`: Static files for the web player UI.
- `docker/`: Dockerfiles and compose configurations for CPU, GPU (NVIDIA), and ROCm (AMD).
- `examples/`: Comprehensive set of usage examples, benchmarks, and specialized tests (e.g., `openai_streaming_audio.py`, `benchmark_unified_streaming.py`).
    - `CAPTIONS_SDK.md`: Documentation for the "Level Up" captions extension, detailing dual-stream consumption of audio and word timings.
- `scripts/`: Maintenance scripts for versioning, badges, and fixing dependencies.

## Key Features & Extensions

### Captions Extension ("Level Up")
- **Endpoint:** `/dev/captioned_speech`
- **Functionality:** Provides high-precision word-level timestamps alongside audio data.
- **Dual-Stream Support:** Supports streaming continuous JSON objects containing base64 audio chunks and associated word timings.
- **UI:** A specialized standalone interface is available at `web/captions.html` (or `http://localhost:8880/web/captions.html` when served) to demonstrate synchronized highlighting.
- **SDK:** `examples/CAPTIONS_SDK.md` provides implementation patterns for both JavaScript and Python clients to consume the dual stream.

## Building and Running

### Prerequisites
- [astral-uv](https://docs.astral.sh/uv/) installed locally.
- [espeak-ng](https://github.com/espeak-ng/espeak-ng) for phonemization.

### Local Development (via uv)
Start the service with hot-reload:
- **CPU:** `./start-cpu.sh`
- **GPU (NVIDIA):** `./start-gpu.sh`
- **ROCm (AMD):** `./start-rocm.sh`

### Docker
Run with Docker Compose from the respective directory:
- **CPU:** `cd docker/cpu && docker compose up --build`
- **GPU (NVIDIA):** `cd docker/gpu && docker compose up --build`
- **ROCm (AMD):** `cd docker/rocm && docker compose up --build`

### Testing
Run the test suite using `pytest`:
```bash
pytest
```
Configuration is managed in `pyproject.toml` and `pytest.ini`.

## Development Conventions

### Coding Style & Standards
- **Configuration:** All settings should be added to `api/src/core/config.py` using `Settings(BaseSettings)`.
- **Logging:** Use `loguru.logger` for all logging. Avoid `print()`.
- **Type Safety:** Use Python type hints throughout the codebase.
- **API Design:** New endpoints should be added to the appropriate router in `api/src/routers/`.

### Dependency Management
- Use `uv add <package>` to add new dependencies.
- Use optional dependencies (`gpu`, `cpu`, `rocm`, `test`) where appropriate in `pyproject.toml`.

### Testing Practices
- Place tests in `api/tests/`.
- Use `pytest` fixtures for common setup (e.g., `kokoro_backend` in `test_kokoro_v1.py`).
- Use `unittest.mock` for mocking external dependencies and hardware-specific features (like CUDA availability).

### Adding New Voices
Voice packs (`.pt` files) are typically stored in `api/src/voices/v1_0`. The `voice_manager.py` handles loading and combining these packs.
