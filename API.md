# 🚀 kokoro-kaptions API Documentation

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![OpenAI Compatible](https://img.shields.io/badge/OpenAI-Compatible-412991?style=for-the-badge&logo=openai)](https://platform.openai.com/docs/api-reference/audio/createSpeech)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

kokoro-kaptions is a high-performance FastAPI wrapper for the **Kokoro-82M** TTS model, providing sub-second latency, multi-language support, and advanced captioning capabilities.

---

## 📋 Table of Contents
1. [Authentication](#-authentication)
2. [OpenAI-Compatible Speech](#-openai-compatible-speech)
3. [Captioned Speech (Level Up)](#-captioned-speech-level-up)
4. [Text Processing & Phonemes](#-text-processing--phonemes)
5. [Voice Mixing & Customization](#-voice-mixing--customization)
6. [System & Debug](#-system--debug)
7. [Health Check](#-health-check)

---

## 🔐 Authentication
Currently, the API does not require authentication by default. If deployed behind a proxy, use standard `Authorization: Bearer <TOKEN>` headers as per your configuration.

---

## 🎙️ OpenAI-Compatible Speech
**Endpoint:** `POST /v1/audio/speech`

This endpoint follows the OpenAI API format, allowing you to drop kokoro-kaptions into existing applications with minimal changes.

### Request Body
| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `model` | string | `kokoro` | Supported: `tts-1`, `tts-1-hd`, `kokoro`. |
| `input` | string | **Required** | The text to generate audio for. |
| `voice` | string | `af_heart` | Voice ID or [Voice Mixture](#-voice-mixing--customization). |
| `response_format` | string | `mp3` | `mp3`, `opus`, `flac`, `wav`, `pcm`. |
| `speed` | float | `1.0` | Range: `0.25` to `4.0`. |
| `stream` | boolean | `true` | Stream audio chunks as they are generated. |

### Extensions (Custom Headers & Fields)
*   **Header `X-Return-Timestamps: true`**: When set, the response switches to a captioned JSON format (similar to `/dev/captioned_speech`).
*   **Field `lang_code`**: Override language detection (e.g., `a` for American English, `b` for British, `j` for Japanese).
*   **Field `normalization_options`**: Fine-tune text normalization (phone numbers, URLs, etc.).

---

## ✨ Captioned Speech ("Level Up")
**Endpoint:** `POST /dev/captioned_speech`

The "Level Up" endpoint is designed for interactive UIs that require word-level synchronization.

### The JSON Streaming Format
When `stream: true`, the server returns a sequence of JSON objects. **Note:** This is not a standard JSON array, but a stream of individual objects: `{"audio": "...", "timestamps": [...]}{"audio": "...", "timestamps": [...]}`.

### JavaScript Fetch Example
```javascript
const response = await fetch('/dev/captioned_speech', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        input: "The quick brown fox jumps over the lazy dog.",
        voice: "af_bella",
        stream: true
    })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();
let buffer = '';

while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    
    buffer += decoder.decode(value, { stream: true });
    
    // Split concatenated JSON objects
    let boundary;
    while ((boundary = buffer.indexOf('}{')) !== -1) {
        const part = buffer.slice(0, boundary + 1);
        const data = JSON.parse(part);
        handleChunk(data); // data.audio (base64) and data.timestamps
        buffer = buffer.slice(boundary + 1);
    }
}
```

---

## 🧩 Text Processing & Phonemes

### Phonemize
**Endpoint:** `POST /dev/phonemize`
Converts raw text into the phonemes used by the Kokoro model.
*   **Input:** `{"text": "Hello", "language": "a"}`
*   **Output:** `{"phonemes": "həˈloʊ", "tokens": [1, 34, 23, ... ]}`

### Generate from Phonemes
**Endpoint:** `POST /dev/generate_from_phonemes`
Generate audio directly by providing a phoneme string.
*   **Input:** `{"phonemes": "həˈloʊ", "voice": "af_bella"}`

---

## 🎛️ Voice Mixing & Customization
kokoro-kaptions supports linear combination of voices to create unique personas.

**Format:** `voice_id(weight)+voice_id(weight)`

**Examples:**
*   `af_bella(1)+af_sky(1)`: 50/50 mix of Bella and Sky.
*   `af_sarah(2)+am_adam(1)`: Weighted mix favoring Sarah.

You can also use the **Voice Combination Utility**:
`POST /v1/audio/voices/combine`
Accepts a list of voices and returns a temporary ID for the combined voice.

---

## 🛠️ System & Debug
Monitoring and diagnostic endpoints for performance tuning:

*   `GET /debug/threads`: Inspect current active threads.
*   `GET /debug/storage`: Check temporary file storage usage.
*   `GET /debug/system`: Get hardware utilization (CPU/GPU/MPS).
*   `GET /debug/session_pools`: Monitor active inference sessions.

---

## 🏥 Health Check
**Endpoint:** `GET /health`
Returns `{"status": "healthy"}` if the service and model are ready.

---

> **Tip:** For high-performance streaming, use the `pcm` or `wav` formats to avoid encoding overhead on the server.
