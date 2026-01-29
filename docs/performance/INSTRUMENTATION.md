# Performance Instrumentation Summary

## What Was Added

### Backend Instrumentation

**1. Performance Utility (`backend/app/utils/performance.py`)**
- High-precision timing with millisecond accuracy
- Context managers: `perf_timer()` and `async_perf_timer()`
- Decorators: `@time_function()` and `@time_async_function()`
- Integrated with Python logging framework

**2. Request Timing Middleware (`backend/app/main.py`)**
- Logs ALL HTTP requests with timing
- Adds `X-Response-Time` header to responses
- Format: `[PERF] REQUEST COMPLETE - METHOD /path - STATUS - XXms`

**3. Instrumented Routes**

**Chat Operations (`backend/app/routes/chat.py`):**
- `initial_message.generate_llm` - First tutor message (LLM call)
- `chat.correct_text` - Text correction (LLM call)
- `chat.generate_response_llm` - AI response generation (LLM call)
- `chat.save_user_message` - Database save

**STT Operations (`backend/app/routes/stt.py`):**
- `stt.transcribe_whisper` - Whisper transcription (GPU/CPU)
- `stt.correction_llm` - Transcription correction (LLM call)

### Frontend Instrumentation

**1. Performance Monitor (`frontend/src/utils/performance.ts`)**
- Chrome DevTools Performance API integration
- Console timing API for detailed logs
- Performance marks visible in Chrome Performance tab
- Runtime enable/disable via localStorage
- Exposed as `window.BabblrPerf` for console access

**2. API Interceptor (`frontend/src/services/api.ts`)**
- Automatic timing of ALL API calls
- Measures network + frontend overhead
- Compares with backend `X-Response-Time` header
- Format: `api.METHOD./endpoint - Backend: Xms, Network+Frontend: Yms`

## How to Use

### View Backend Logs

```bash
# From docker directory
docker logs babblr-backend-dev -f | grep PERF

# Example output when sending chat message:
# [PERF] REQUEST START - POST /chat
# [PERF] chat.correct_text - START
# [PERF] chat.correct_text - DONE in 456.78ms
# [PERF] chat.generate_response_llm - START
# [PERF] chat.generate_response_llm - DONE in 2345.67ms
# [PERF] REQUEST COMPLETE - POST /chat - 200 - 2856.34ms
```

### Use Frontend Debugging

```javascript
// In Chrome DevTools Console:

// Enable (persists across reloads)
BabblrPerf.enable()
location.reload()

// View all measurements
BabblrPerf.getMeasures()

// Log custom events
BabblrPerf.logEvent('user_clicked_send')

// Clear data
BabblrPerf.clear()

// Disable
BabblrPerf.disable()
```

### Chrome DevTools Performance Tab

1. Open DevTools → Performance
2. Click Record (Ctrl+E)
3. Perform action (send message, transcribe, etc.)
4. Stop recording
5. Look for "User Timing" track - shows our performance marks

## What to Look For

### Identifying Bottlenecks

**Slow Initial Message (> 2s):**
```
[PERF] initial_message.generate_llm - DONE in 5678ms  ← LLM is slow
```
- Check Ollama model loading
- Consider smaller/faster models
- First call often slower (model load)

**Slow Chat Response (> 2s):**
```
[PERF] chat.correct_text - DONE in 234ms            ← Text correction
[PERF] chat.generate_response_llm - DONE in 4567ms  ← Main bottleneck
```
- LLM generation is typically slowest
- Larger conversation history = slower
- GPU vs CPU makes big difference for local LLMs

**Slow Transcription (> 1s for 5s audio):**
```
[PERF] stt.transcribe_whisper - DONE in 3456ms  ← Whisper transcription
[PERF] stt.correction_llm - DONE in 456ms       ← Optional correction
```
- Check GPU usage: `curl localhost:8000/stt/cuda`
- GPU should be ~10x faster than CPU
- Model size matters: base < small < medium < large-v3

**Frontend vs Backend:**
```javascript
// Console shows:
[PERF] api.POST./chat - Backend: 2856ms, Network+Frontend: 3012ms
//                       ^^^^^^^^           ^^^^
//                       Backend time       Total time
```
- If difference > 500ms, frontend or network is slow
- Check Chrome Performance tab for render bottlenecks
- Docker networking adds ~10-50ms typically

### Model Loading Detection

**First call is always slower:**
```
First transcription:  stt.transcribe_whisper - DONE in 8234ms  ← Loading model
Second transcription: stt.transcribe_whisper - DONE in 892ms   ← Using cached model
```

This is NORMAL - models are hot-loaded on first use, then cached.

**LLM model loading (Ollama):**
```
First chat: chat.generate_response_llm - DONE in 12456ms  ← Loading model
Next chat:  chat.generate_response_llm - DONE in 2345ms   ← Model cached
```

Check Ollama logs: `docker logs babblr-ollama-dev`

## Performance Targets

### Good (Production Ready)
- Initial message: < 2s
- Chat response: < 2s
- Transcription (GPU, 5s audio): < 1s
- API overhead: < 200ms

### Acceptable (Development)
- Initial message: 2-5s
- Chat response: 2-5s
- Transcription (GPU, 5s audio): 1-3s
- API overhead: 200-500ms

### Needs Investigation
- Initial message: > 5s
- Chat response: > 5s
- Transcription (GPU, 5s audio): > 3s
- API overhead: > 500ms

## Next Steps Based on Findings

**If LLM is slow:**
- Switch to faster models (smaller parameters)
- Use Claude/Gemini API instead of local Ollama
- Implement streaming responses (perceived performance)
- Add Redis caching for common responses

**If Whisper is slow:**
- Ensure GPU is being used (check /stt/cuda)
- Use smaller models (base or small instead of large-v3)
- Consider external Whisper service
- Pre-load models on startup (warmup)

**If Database is slow:**
- Check query patterns in logs
- Add indexes if needed
- Consider connection pooling
- Implement query result caching

**If Frontend is slow:**
- Use Chrome Performance Profiler
- Check for unnecessary re-renders
- Optimize React components
- Lazy load heavy components

## Testing the Instrumentation

Send a chat message and watch logs in real-time:

```bash
# Terminal 1: Backend logs
docker logs babblr-backend-dev -f | grep PERF

# Terminal 2: Send test request
curl -X POST http://localhost:8000/chat/initial-message \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 1,
    "language": "spanish",
    "difficulty_level": "A1",
    "topic_id": "greetings"
  }'

# You should see:
# [PERF] REQUEST START - POST /chat/initial-message
# [PERF] initial_message.generate_llm - START
# [PERF] initial_message.generate_llm - DONE in XXXXms
# [PERF] REQUEST COMPLETE - POST /chat/initial-message - 200 - XXXXms
```

## Files Modified

**Backend:**
- `backend/app/utils/performance.py` (NEW)
- `backend/app/main.py` (added middleware)
- `backend/app/routes/chat.py` (added timing)
- `backend/app/routes/stt.py` (added timing)

**Frontend:**
- `frontend/src/utils/performance.ts` (NEW)
- `frontend/src/services/api.ts` (added interceptor)

**Documentation:**
- `PERFORMANCE_DEBUGGING.md` (NEW - detailed guide)
- `PERF_INSTRUMENTATION_SUMMARY.md` (NEW - this file)

See `PERFORMANCE_DEBUGGING.md` for comprehensive debugging workflows and examples.
