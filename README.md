# 🚀 kokoro-kaptions

kokoro-kaptions is a high-performance, production-ready FastAPI wrapper for the [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) text-to-speech model. It provides a drop-in OpenAI-compatible speech endpoint and introduces the **"Level Up" Captions Engine**, enabling real-time word-level synchronization for interactive applications.

## ✨ Key Features

- **🎯 OpenAI Compatibility**: Full support for the `/v1/audio/speech` endpoint. Drop kokoro-kaptions into any OpenAI-compatible app.
- **💎 Level Up Captions**: High-precision word-level timestamps generated alongside audio. Includes a specialized dual-stream JSON format.
- **🎭 Pro Voice Mixing**: Combine multiple voices with custom weights (e.g., `af_bella(1.5)+af_sky(1.0)`).
- **⚡ Ultra-Low Latency**: Optimized PyTorch inference pipeline for sub-second time-to-first-token.
- **🖥️ Universal Hardware Acceleration**: Native support for NVIDIA (CUDA), AMD (ROCm 7.2), Apple Silicon (MPS), and high-performance CPU inference.
- **🧩 Advanced Text Processing**: Multi-language phonemization and direct generation from phoneme strings.

---

## 📋 Table of Contents
1. [🛠️ Tech Stack](#️-tech-stack)
2. [📋 Prerequisites](#-prerequisites)
3. [🚀 Getting Started](#-getting-started)
4. [🏛️ Architecture Overview](#️-architecture-overview)
5. [✨ Captions Extension (Level Up)](#-captions-extension-level-up)
6. [🔧 Environment Variables](#-environment-variables)
7. [📜 Available Scripts](#-available-scripts)
8. [🧪 Testing](#-testing)
9. [🚢 Deployment](#-deployment)
10. [🔍 Troubleshooting](#-troubleshooting)
11. [📄 License](#-license)

---

## 🛠️ Tech Stack

- **Language**: [Python 3.13+](https://www.python.org/)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Inference Engine**: [PyTorch](https://pytorch.org/) (CUDA 12.9 / ROCm 7.2 / MPS)
- **Dependency Management**: [astral-uv](https://docs.astral.sh/uv/)
- **Text Processing**: [misaki](https://github.com/hexgrad/kokoro), [spacy](https://spacy.io/), [espeak-ng](https://github.com/espeak-ng/espeak-ng)
- **Containerization**: [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.13 or higher**
- **[astral-uv](https://docs.astral.sh/uv/)** (Fast dependency manager)
- **espeak-ng** (Required for phonemization: `sudo apt-get install espeak-ng` on Linux)
- **Docker & Docker Compose** (Optional, for containerized execution)

---

## 🚀 Getting Started

### 1. Clone and Setup
```bash
git clone https://github.com/remsky/kokoro-kaptions.git
cd kokoro-kaptions

# Synchronize dependencies based on your hardware
uv sync --extra gpu --extra test  # For NVIDIA
# or
uv sync --extra rocm --extra test # For AMD
# or
uv sync --extra cpu --extra test  # For CPU only
```

### 2. Launch the Server
```bash
# NVIDIA GPU
./start-gpu.sh

# AMD GPU (ROCm)
./start-rocm.sh

# CPU (Intel/AMD/Apple Silicon)
./start-cpu.sh
```

The server will be available at `http://localhost:8880`.

### 3. Access the Web Player
Visit `http://localhost:8880/web/captions.html` to use the interactive player and see **synchronized word highlighting** in action.

---

## 🏛️ Architecture Overview

kokoro-kaptions is designed for high-concurrency TTS tasks with a modular, service-oriented architecture.

### Directory Structure
- `api/src/main.py`: Entry point, FastAPI initialization, and model lifecycle management.
- `api/src/routers/`: API route definitions.
    - `openai_compatible.py`: Implements standard OpenAI `/v1/audio/speech`.
    - `development.py`: Home of the **Level Up** captions and phoneme endpoints.
    - `debug.py`: Real-time system and hardware health monitoring.
- `api/src/inference/`: The heart of kokoro-kaptions.
    - `model_manager.py`: Singleton for model lifecycle, warming, and routing.
    - `voice_manager.py`: Logic for loading `.pt` voice packs and weighted mixing.
    - `kokoro_v1.py`: Primary PyTorch inference implementation.
- `api/src/core/`: Centralized configuration, path resolution, and logging.
- `web/`: A modern, standalone frontend for testing speech and captions.

### Request Lifecycle
1.  **Ingestion**: FastAPI receives a request and validates it against Pydantic models in `api/src/structures/`.
2.  **Normalization**: Text is normalized (handling URLs, numbers, etc.) before being passed to the phonemizer.
3.  **Inference**: The `ModelManager` invokes the PyTorch backend, yielding audio buffers.
4.  **Alignment**: For captioned requests, the engine calculates per-word timestamps by tracking phoneme durations.
5.  **Streaming**: Data is streamed back to the client as either raw audio bytes or a **Dual-Stream JSON** sequence.

---

## ✨ Captions Extension (Level Up)

The Captions Engine is the standout feature of kokoro-kaptions, designed for developers building interactive learning tools, video generators, or accessible media players.

### The Endpoint: `/dev/captioned_speech`
This endpoint returns a sequence of JSON objects containing both the audio chunk (base64) and the associated word timings.

**Specialized JSON Streaming Format:**
Unlike standard JSON arrays, kokoro-kaptions streams individual objects back-to-back:
`{"audio": "...", "timestamps": [...]}{"audio": "...", "timestamps": [...]}`

### Consuming the Stream (SDK)
A full implementation guide is available in [examples/CAPTIONS_SDK.md](examples/CAPTIONS_SDK.md). It covers:
- **JavaScript (Fetch)**: Using `getReader()` to parse concatenated JSON objects.
- **Python (Requests)**: Iterative content consumption for backend-to-backend services.
- **UI Sync**: Patterns for using the `ontimeupdate` event to drive word highlighting.

### Standalone UI
kokoro-kaptions includes a built-in UI at `http://localhost:8880/web/captions.html` that demonstrates pixel-perfect word synchronization. It uses the `JSONStreamingResponse` from the server to highlight words in real-time as the audio plays.

---

## 🔧 Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `API_PORT` | `8880` | Port for the FastAPI server. |
| `USE_GPU` | `true` | Set to `false` to force CPU inference. |
| `DEVICE_TYPE` | `None` | Manually set `cuda`, `mps`, or `cpu`. |
| `DEFAULT_VOICE` | `af_heart` | Default voice for requests missing a voice ID. |
| `MODEL_DIR` | `/app/api/src/models` | Path to Kokoro model files. |
| `HSA_OVERRIDE_GFX_VERSION` | `None` | (ROCm Only) Required for specific AMD hardware overrides. |

---

## 📜 Available Scripts

| Command | Description |
| :--- | :--- |
| `./start-gpu.sh` | Start with NVIDIA acceleration. |
| `./start-rocm.sh` | Start with AMD ROCm 7.2 acceleration (Strix Point support). |
| `./start-cpu.sh` | Start on CPU. |
| `python docker/scripts/download_model.py` | Utility to fetch the latest Kokoro weights. |
| `uv run pytest` | Execute the full test suite. |

---

## 🧪 Testing

We use `pytest` for all unit and integration testing.

```bash
# Run everything
uv run pytest

# Test the core inference engine
uv run pytest api/tests/test_kokoro_v1.py
```

Tests cover path resolution, text normalization, voice mixing logic, and OpenAI API compliance.

---

## 🚢 Deployment

### Docker Compose
kokoro-kaptions is container-first. Each hardware target has a tailored configuration:

```bash
# NVIDIA
cd docker/gpu && docker compose up --build

# AMD (ROCm)
cd docker/rocm && docker compose up --build

# CPU
cd docker/cpu && docker compose up --build
```

### Kubernetes
A Helm chart is available in `charts/kokoro-fastapi` for scaled deployments.

---

## 🔍 Troubleshooting

### ROCm Shared Library Errors
If you see `libcaffe2_nvrtc.so` errors on AMD, use `./start-rocm.sh`. It automatically fixes the library path and sets hardware overrides for new chips like the **Radeon 890M**.

### Python 3.13 Compatibility
If you get an error regarding `audioop`, ensure you've run `uv sync`. kokoro-kaptions uses `audioop-lts` to bridge the removal of `audioop` in Python 3.13.

---

## 📄 License

- **kokoro-kaptions Code**: MIT License.
- **Kokoro-82M Weights**: Apache 2.0.
