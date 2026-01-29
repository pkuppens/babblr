# Performance Documentation

This directory contains documentation about Babblr's performance characteristics, monitoring, and optimization strategies.

## Documents

### [DEBUGGING.md](./DEBUGGING.md)

Comprehensive guide for identifying and diagnosing performance bottlenecks.

**Topics:**
- Frontend performance monitoring (Chrome DevTools)
- Backend performance logging
- Common bottleneck scenarios (slow LLM, slow STT, slow database)
- Performance targets and acceptable ranges

### [INSTRUMENTATION.md](./INSTRUMENTATION.md)

Technical documentation of the performance instrumentation implementation.

**Topics:**
- Backend timing utilities and middleware
- Frontend performance monitoring API
- Instrumented endpoints and operations
- How to interpret performance data

### [STREAMING.md](./STREAMING.md)

Implementation guide for streaming LLM responses (future enhancement).

**Topics:**
- Architecture for Server-Sent Events (SSE)
- Backend streaming endpoint design
- Frontend streaming response handling
- TTS integration with streaming
- Background processing opportunities

## Related Documentation

- [`../../DEVELOPMENT.md`](../../DEVELOPMENT.md) - Development workflow and testing
- [`../ci/GITHUB_ACTIONS_GUIDE.md`](../ci/GITHUB_ACTIONS_GUIDE.md) - CI/CD pipeline performance

## Performance Configuration

Performance can be tuned via environment variables in `docker/.env`:

```bash
# Text correction settings
CORRECTION_MAX_LEVEL=A2         # Apply corrections up to A2 level
CONVERSATION_MAX_HISTORY=5      # Last N messages in LLM context

# Model selection (affects speed vs quality)
OLLAMA_MODEL=llama3.2:1b        # Fast (1B params)
# OLLAMA_MODEL=llama3.2:latest  # Balanced (3B params)
# OLLAMA_MODEL=llama3.1:8b      # Quality (8B params)

# Whisper model (affects STT speed)
WHISPER_MODEL=base              # Fast, acceptable quality
# WHISPER_MODEL=large-v3        # Slow, best quality
```

## Quick Performance Check

Run the manual test script:
```bash
cd backend/tests/manual
powershell -ExecutionPolicy Bypass -File test_performance.ps1
```

Or use the frontend performance monitor:
```javascript
// In Chrome DevTools Console:
BabblrPerf.enable()
location.reload()
// Interact with app and check console for timing data
```
