#!/usr/bin/env python3
"""Test script for Whisper container validation.

Tests GPU availability, health, and transcription accuracy.
"""

import json
import sys
import time
from pathlib import Path

import httpx


def test_health(base_url: str) -> bool:
    """Test Whisper container availability."""
    print("=" * 60)
    print("Test 1: Container Availability Check")
    print("=" * 60)
    # Try root endpoint or docs
    endpoints_to_try = ["/", "/docs", "/openapi.json", "/asr"]
    available = False
    
    for endpoint in endpoints_to_try:
        try:
            response = httpx.get(f"{base_url}{endpoint}", timeout=5.0, follow_redirects=True)
            if response.status_code in [200, 404]:  # 404 means server is up, endpoint doesn't exist
                print(f"[OK] Server responding at {endpoint}: {response.status_code}")
                available = True
                if endpoint == "/docs":
                    print("[INFO] Swagger docs available at /docs")
                break
        except httpx.ConnectError:
            print(f"[FAIL] Cannot connect to {base_url}")
            return False
        except Exception as e:
            continue
    
    if available:
        print("[OK] Container is running and responding")
        return True
    else:
        print("[FAIL] Container not responding")
        return False


def test_gpu_info(base_url: str) -> dict:
    """Test GPU/CUDA availability."""
    print("\n" + "=" * 60)
    print("Test 2: GPU/CUDA Detection")
    print("=" * 60)
    
    gpu_info = {
        "available": False,
        "device": "unknown",
        "source": "unknown",
    }
    
    # Try different endpoints
    endpoints = ["/info", "/status", "/health"]
    for endpoint in endpoints:
        try:
            response = httpx.get(f"{base_url}{endpoint}", timeout=5.0)
            if response.status_code == 200:
                data = response.json() if response.content else {}
                print(f"[INFO] Endpoint {endpoint} response: {json.dumps(data, indent=2)}")
                
                # Try to extract GPU info
                if "device" in data:
                    gpu_info["device"] = data["device"]
                    gpu_info["available"] = data.get("device", "").lower() == "cuda"
                    gpu_info["source"] = endpoint
                elif "cuda" in data:
                    cuda_data = data["cuda"]
                    gpu_info["available"] = cuda_data.get("available", False)
                    gpu_info["device"] = cuda_data.get("device", "unknown")
                    gpu_info["source"] = endpoint
        except Exception as e:
            print(f"[INFO] Endpoint {endpoint} not available or error: {e}")
            continue
    
    # Check container logs for GPU info
    print("\n[INFO] Checking container environment variables...")
    print("Note: Check container logs with: docker logs babblr-whisper | grep -i cuda")
    
    if gpu_info["available"]:
        print(f"[OK] GPU detected: {gpu_info['device']} (from {gpu_info['source']})")
    else:
        print(f"[INFO] GPU not detected or using CPU: {gpu_info['device']}")
    
    return gpu_info


def test_transcription(base_url: str, audio_file: Path) -> dict:
    """Test transcription with German audio file."""
    print("\n" + "=" * 60)
    print("Test 3: Transcription Test")
    print("=" * 60)
    
    if not audio_file.exists():
        print(f"[FAIL] Audio file not found: {audio_file}")
        return {"success": False, "error": "File not found"}
    
    print(f"[INFO] Testing transcription with: {audio_file}")
    print(f"[INFO] Expected: 'Ich möchte gern Deutsch lernen.' or similar")
    print(f"[INFO] Expected language: German (de)")
    
    try:
        with open(audio_file, "rb") as f:
            files = {"audio_file": (audio_file.name, f.read(), "audio/webm")}
        
        print("[INFO] Sending transcription request...")
        start_time = time.time()
        
        response = httpx.post(
            f"{base_url}/asr",
            files=files,
            params={"task": "transcribe", "output": "json"},
            timeout=300.0,  # 5 minutes for large-v3 model
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            text = result.get("text", "").strip()
            language = result.get("language", "unknown")
            
            print(f"[OK] Transcription successful (took {elapsed:.2f}s)")
            print(f"[RESULT] Text: {text}")
            print(f"[RESULT] Language: {language}")
            
            # Check if expected text is present
            expected_phrases = [
                "Ich möchte",
                "Deutsch lernen",
                "gern",
            ]
            found_phrases = [phrase for phrase in expected_phrases if phrase.lower() in text.lower()]
            
            if found_phrases:
                print(f"[OK] Found expected phrases: {', '.join(found_phrases)}")
            else:
                print(f"[WARN] Expected phrases not found in transcription")
            
            if language.lower() == "de":
                print(f"[OK] Language correctly detected as German")
            else:
                print(f"[WARN] Language detected as '{language}', expected 'de'")
            
            return {
                "success": True,
                "text": text,
                "language": language,
                "elapsed": elapsed,
                "found_phrases": found_phrases,
            }
        else:
            print(f"[FAIL] Transcription failed: {response.status_code}")
            print(f"Response: {response.text}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except httpx.TimeoutException:
        print("[FAIL] Transcription timed out (>5 minutes)")
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        print(f"[FAIL] Transcription error: {e}")
        return {"success": False, "error": str(e)}


def main():
    """Run all tests."""
    base_url = "http://localhost:9000"
    audio_file = Path(__file__).parent.parent / "tmp" / "stt_20260106224435.webm"
    
    print("Whisper Container Validation Tests")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print(f"Audio file: {audio_file}")
    print()
    
    results = {
        "health": False,
        "gpu": {},
        "transcription": {},
    }
    
    # Test 1: Health
    results["health"] = test_health(base_url)
    
    if not results["health"]:
        print("\n[FAIL] Health check failed. Container may not be ready.")
        print("Wait a few seconds and try again, or check logs:")
        print("  docker logs babblr-whisper")
        sys.exit(1)
    
    # Test 2: GPU
    results["gpu"] = test_gpu_info(base_url)
    
    # Test 3: Transcription
    results["transcription"] = test_transcription(base_url, audio_file)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Health Check: {'[OK]' if results['health'] else '[FAIL]'}")
    print(f"GPU Available: {'[OK]' if results['gpu'].get('available') else '[INFO] CPU mode'}")
    print(f"Transcription: {'[OK]' if results['transcription'].get('success') else '[FAIL]'}")
    
    if results["transcription"].get("success"):
        print(f"\nTranscription Result:")
        print(f"  Text: {results['transcription'].get('text', 'N/A')}")
        print(f"  Language: {results['transcription'].get('language', 'N/A')}")
        print(f"  Time: {results['transcription'].get('elapsed', 0):.2f}s")
    
    # Overall result
    all_passed = (
        results["health"]
        and results["transcription"].get("success", False)
    )
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] All critical tests passed!")
        print("Whisper container is ready for use as STT backend.")
    else:
        print("[FAIL] Some tests failed. Review output above.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
