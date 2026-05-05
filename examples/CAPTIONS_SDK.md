# Kokoro-FastAPI Captioned Speech SDK

The Captioned Speech endpoint is a "Level Up" over standard TTS because it provides high-precision word-level timestamps alongside the audio data.

## 1. Standard Request (Non-Streaming)
Use this for shorter snippets of text where you can wait for the full generation before playback.

**Endpoint:** `POST /dev/captioned_speech`
**Payload:**
```json
{
  "input": "The quick brown fox.",
  "voice": "af_bella",
  "stream": false
}
```

**Response:** A single JSON object.
```json
{
  "audio": "BASE64_ENCODED_WAV_DATA",
  "audio_format": "audio/wav",
  "timestamps": [
    {"word": "The", "start_time": 0.0, "end_time": 0.2},
    {"word": "quick", "start_time": 0.2, "end_time": 0.5}
  ]
}
```

**Python Example (Standard):**
```python
import requests
import base64

response = requests.post(
    "http://localhost:8880/dev/captioned_speech",
    json={
        "input": "The quick brown fox.",
        "stream": False
    }
)

data = response.json()
audio_bytes = base64.b64decode(data["audio"])
timestamps = data["timestamps"]
```

---

## 2. Streaming Request (Advanced)
Use this for long-form text. It returns a **continuous stream of JSON objects**, allowing you to start playback and highlighting before the entire generation is finished.

**Payload:**
```json
{
  "input": "Long text...",
  "stream": true
}
```

**JavaScript Example (Streaming):**
Because the server sends multiple JSON objects back-to-back, you cannot use `.json()`. You must use a stream reader.

```javascript
const response = await fetch('/dev/captioned_speech', {
    method: 'POST',
    body: JSON.stringify({ input: "...", stream: true })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();
let buffer = '';

while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    
    buffer += decoder.decode(value, { stream: true });
    
    // The server returns responses concatenated: {"audio": "..."}{"audio": "..."}
    // We split them at the boundary between objects
    let boundary;
    while ((boundary = buffer.indexOf('}{')) !== -1) {
        const part = buffer.slice(0, boundary + 1);
        processChunk(JSON.parse(part));
        buffer = buffer.slice(boundary + 1);
    }
}
```

**Python Example (Streaming):**
```python
import requests
import json
import base64

response = requests.post(
    "http://localhost:8880/dev/captioned_speech",
    json={"input": "Long text...", "stream": True},
    stream=True
)

buffer = ""
for chunk in response.iter_content(decode_unicode=True):
    if chunk:
        buffer += chunk
        # Split concatenated JSON objects at the boundary
        while "}{" in buffer:
            boundary = buffer.find("}{")
            part = buffer[:boundary+1]
            data = json.loads(part)
            # Process your chunk (audio and timestamps)
            print(f"Received chunk with {len(data['timestamps'])} timestamps")
            buffer = buffer[boundary+1:]
```

---

## 3. Synchronizing the UI
To sync captions with audio, use the `ontimeupdate` event of your audio player.

**Logic:**
1.  **Storage:** Keep your timestamps in an array `[{word, start_time, end_time}, ...]`.
2.  **Tracking:** On every time update (approx 4-6 times per second), find the word that matches the current playhead.

```javascript
audioPlayer.ontimeupdate = () => {
    const now = audioPlayer.currentTime;
    
    // Find the word currently being spoken
    const activeWord = timestamps.find(ts => 
        now >= ts.start_time && now <= ts.end_time
    );
    
    if (activeWord) {
        highlightWordInUI(activeWord);
    }
};
```

---

## 4. OpenAI-Compatible Header
If you use the **OpenAI-compatible endpoint** (`/v1/audio/speech`), you can still get captions by adding this header:
*   `X-Return-Timestamps: true`

This will force the OpenAI endpoint to switch from returning raw bytes to the Captioned Response JSON format.
