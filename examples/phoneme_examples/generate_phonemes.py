import json
from typing import Tuple, Optional, Union, List
from pathlib import Path

import requests

# Get the directory this script is in
SCRIPT_DIR = Path(__file__).parent.absolute()


def get_phonemes(text: str, language: str = "a") -> Tuple[str, list[int]]:
    """Get phonemes and tokens for input text.

    Args:
        text: Input text to convert to phonemes
        language: Language code (defaults to "a" for American English)

    Returns:
        Tuple of (phonemes string, token list)
    """
    # Create the request payload
    payload = {"text": text, "language": language}

    # Make POST request to the phonemize endpoint
    response = requests.post("http://localhost:8880/dev/phonemize", json=payload)

    # Raise exception for error status codes
    response.raise_for_status()

    # Parse the response
    result = response.json()
    return result["phonemes"], result["tokens"]


def generate_audio_from_phonemes(phonemes: str, voice: str = "af_bella") -> Optional[bytes]:
    """Generate audio from phonemes."""
    response = requests.post(
        "http://localhost:8880/dev/generate_from_phonemes",
        json={"phonemes": phonemes, "voice": voice},
        headers={"Accept": "audio/wav"}
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response content type: {response.headers.get('Content-Type')}")
    print(f"Response length: {len(response.content)} bytes")
    
    if response.status_code != 200:
        print(f"Error response: {response.text}")
        return None
        
    if not response.content:
        print("Error: Empty response content")
        return None
        
    return response.content


import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Generate phonemes and audio from text.")
    parser.add_argument("text", nargs="*", help="Text to convert to phonemes. If omitted, you'll be prompted.")
    parser.add_argument("--voice", default="af_bella", help="Voice to use for audio generation (default: af_bella).")
    args = parser.parse_args()

    if args.text:
        examples = [" ".join(args.text)]
    else:
        # Prompt for input if no arguments provided
        user_input = input("Enter the text you want to convert to phonemes: ").strip()
        if not user_input:
            print("No text provided. Exiting.")
            return
        examples = [user_input]

    print(f"Generating phonemes and audio using voice '{args.voice}' for: {examples[0][:50]}...\n")

    # Create output directory in same directory as script
    output_dir = SCRIPT_DIR / "output"
    output_dir.mkdir(exist_ok=True)

    for i, text in enumerate(examples):
        print(f"{len(text)}: Input text: {text}")
        try:
            # Get phonemes
            phonemes, tokens = get_phonemes(text)
            print(f"{len(phonemes)} Phonemes: {phonemes}")
            print(f"{len(tokens)} Tokens: {tokens}")

            # Generate audio from phonemes
            print("Generating audio...")
            audio_bytes = generate_audio_from_phonemes(phonemes, voice=args.voice)
            
            if not audio_bytes:
                print("Error: No audio data generated")
                continue

            # Log response size
            print(f"Generated {len(audio_bytes)} bytes of audio data")

            if audio_bytes:
                # Save audio file
                output_path = output_dir / f"example_{i+1}.wav"
                with output_path.open("wb") as f:
                    f.write(audio_bytes)
                print(f"Audio saved to: {output_path}")

            print()

        except requests.RequestException as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
