# Performance Debugging Guide

This guide explains how to identify and diagnose performance bottlenecks in Babblr using the built-in instrumentation.

## Quick Start

### Backend Performance Logs

The backend now logs detailed timing information for all operations. View logs with:

```bash
# From docker directory
docker logs babblr-backend-dev -f | grep PERF

# Example output:
# [PERF] REQUEST START - POST /chat/initial-message
# [PERF] initial_message.generate_llm - START
# [PERF] initial_message.generate_llm - DONE in 1234.56ms
# [PERF] REQUEST COMPLETE - POST /chat/initial-message - 200 - 1456.78ms
```

### Frontend Performance Monitoring

Open Chrome DevTools Console and use:

```javascript
// Enable performance debugging (persists across reloads)
BabblrPerf.enable()

// Reload page to activate
location.reload()

// View performance data
BabblrPerf.getMeasures()

// Clear performance data
BabblrPerf.clear()

// Disable when done
BabblrPerf.disable()
```

## What Gets Measured

### Backend (millisecond precision)

**Request Level:**
- Total request time (all endpoints)
- Backend response time in `X-Response-Time` header

**Chat Operations:**
- `initial_message.generate_llm` - First tutor message generation
- `chat.correct_text` - User message correction (LLM call)
- `chat.generate_response_llm` - AI tutor response generation (LLM call)
- `chat.save_user_message` - Database operation

**STT Operations:**
- `stt.transcribe_whisper` - Whisper model transcription (GPU/CPU)
- `stt.correction_llm` - Transcription correction (LLM call)

### Frontend (millisecond precision)

**API Calls:**
- All API requests automatically timed
- Shows backend time vs network+frontend overhead
- Example: `api.POST./chat` - tracks end-to-end latency

**Chrome DevTools Integration:**
- Performance marks visible in Performance tab
- Use Performance Profiler to record and analyze
- Console timers for detailed debugging

## Identifying Bottlenecks

### 1. Slow Initial Message

Check logs for:
```
[PERF] initial_message.generate_llm - DONE in XXXXms
```

**If > 2000ms:**
- LLM provider is slow (Ollama, Claude, Gemini)
- Check if Ollama models are loaded (first call loads model)
- Consider using smaller models or switching providers

### 2. Slow Chat Responses

Check logs for:
```
[PERF] chat.correct_text - DONE in XXXms
[PERF] chat.generate_response_llm - DONE in XXXms
```

**If correction > 500ms:**
- Text correction LLM call is slow
- May skip for good speakers to improve UX

**If generate_response > 2000ms:**
- LLM provider is slow
- Check Ollama model size and GPU usage
- Long conversation history increases latency

### 3. Slow Transcription

Check logs for:
```
[PERF] stt.transcribe_whisper - DONE in XXXms
[PERF] stt.correction_llm - DONE in XXXms
```

**If transcribe > 3000ms for short audio:**
- Check if GPU is being used: `curl localhost:8000/stt/cuda`
- GPU should be 10x faster than CPU
- First transcription loads model (slower)
- Subsequent transcriptions use cached model (faster)

**If correction > 1000ms:**
- STT correction LLM call adds overhead
- Only runs when conversation_id provided

### 4. Frontend Overhead

Compare backend time vs total time:
```
[PERF] api.POST./chat - Backend: 1234ms, Network+Frontend: 1456ms
```

**If (Total - Backend) > 200ms:**
- Network latency (containerization overhead)
- Frontend React render time
- Check Chrome DevTools Performance tab

## Common Scenarios

### First Tutor Message is Slow

**Diagnosis:**
```bash
docker logs babblr-backend-dev | grep "initial_message"
```

**Typical causes:**
1. Ollama loading model for first time (~5-10s)
2. LLM provider warm-up
3. Database query on first request

**Solutions:**
- Model warmup on startup (already implemented for STT)
- Use lighter LLM models for faster responses
- Redis caching for common prompts (planned)

### Every Chat Message is Slow

**Diagnosis:**
```bash
docker logs babblr-backend-dev | grep "chat\."
```

**Typical causes:**
1. Ollama/LLM provider latency
2. GPU not being used (CPU inference is slow)
3. Large conversation history

**Solutions:**
- Check Ollama GPU usage: `docker logs babblr-ollama-dev`
- Reduce max conversation history length
- Use faster LLM models (smaller parameters)

### Transcription is Slow

**Diagnosis:**
```bash
# Check if GPU is used
curl localhost:8000/stt/cuda

# Check logs
docker logs babblr-backend-dev | grep "stt\."
```

**Typical causes:**
1. CPU transcription (10x slower than GPU)
2. Large Whisper model (large-v3 is slow)
3. First transcription loading model

**Solutions:**
- Ensure GPU support enabled (already done)
- Use smaller model (base, small instead of large-v3)
- Model pre-loading/warmup

## Advanced Debugging

### Chrome DevTools Performance Profiler

1. Open DevTools → Performance tab
2. Click Record (Ctrl+E)
3. Perform slow action (send message, etc.)
4. Stop recording
5. Analyze timeline:
   - Look for long tasks (yellow/red bars)
   - Check "User Timing" track for our performance marks
   - Identify JavaScript functions taking longest

### Backend Detailed Logging

Enable DEBUG level logging:

```bash
# Edit docker-compose.dev.yml, add to backend environment:
- LOG_LEVEL=DEBUG

# Restart backend
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml restart backend

# View detailed logs
docker logs babblr-backend-dev -f
```

### Network Inspection

Chrome DevTools → Network tab:
- Check request timing (Waiting vs Content Download)
- Look for queueing (connection limits)
- Verify X-Response-Time header matches backend logs

## Performance Targets

**Good Performance:**
- Initial message: < 2s
- Chat response: < 2s
- Transcription (GPU): < 1s for 5s audio
- API overhead: < 200ms

**Acceptable Performance:**
- Initial message: 2-5s
- Chat response: 2-5s
- Transcription (GPU): 1-3s for 5s audio
- API overhead: 200-500ms

**Needs Investigation:**
- Initial message: > 5s
- Chat response: > 5s
- Transcription (GPU): > 3s for 5s audio
- API overhead: > 500ms

## Next Steps

Based on performance data, consider:

1. **Redis Caching:** Cache LLM responses for common patterns
2. **Model Optimization:** Use smaller, faster models
3. **Streaming Responses:** Stream LLM output for perceived speed
4. **Background Processing:** Pre-generate or cache responses
5. **Connection Pooling:** Reduce database/API connection overhead

## Example Session

```bash
# 1. Enable frontend debugging
# In browser console:
BabblrPerf.enable()
location.reload()

# 2. Enable backend DEBUG logging
docker logs babblr-backend-dev -f | grep PERF

# 3. Perform action (send chat message)

# 4. Analyze results:
# Backend log shows: chat.generate_response_llm - DONE in 3456ms
# Console shows: api.POST./chat - Backend: 3456ms, Network+Frontend: 3678ms
# Conclusion: LLM is the bottleneck (3.4s), network overhead is minimal (222ms)

# 5. Check LLM provider
docker logs babblr-ollama-dev
# If using Ollama, check model size and GPU usage
```
