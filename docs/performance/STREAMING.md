# Streaming Implementation Guide

## Overview

Streaming responses provides significantly better perceived performance by showing the AI response as it's generated, rather than waiting for the complete response.

**Current**: 6-8s wait → complete response appears
**With Streaming**: Response starts appearing in ~500ms, continues building

## Architecture

### Backend (FastAPI + SSE)

**Current Flow:**
```
User message → LLM generate (6-8s) → Complete response → Frontend
```

**Streaming Flow:**
```
User message → LLM stream → Token 1 → Frontend (500ms)
                         → Token 2 → Frontend (600ms)
                         → ...
                         → Token N → Frontend (6-8s)
```

### Implementation Steps

#### 1. Update LLM Providers to Support Streaming

**Ollama** (already supports streaming):
```python
# In app/services/llm/providers/ollama.py

async def generate_stream(self, prompt: str, **kwargs):
    """Generate response with streaming."""
    response = await self.client.chat(
        model=self.model,
        messages=[{"role": "user", "content": prompt}],
        stream=True  # Enable streaming
    )

    async for chunk in response:
        if chunk['message']['content']:
            yield chunk['message']['content']
```

**Claude/Gemini** (also support streaming):
- Claude: Use `anthropic.messages.stream()`
- Gemini: Use `model.generate_content(..., stream=True)`

#### 2. Create Streaming Endpoint

```python
# In app/routes/chat.py

from fastapi.responses import StreamingResponse

@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """Stream chat response using Server-Sent Events."""

    async def event_generator():
        # Get conversation context (same as before)
        conversation = await get_conversation(request.conversation_id, db)
        history = await get_history(request.conversation_id, db)

        # Get LLM provider
        llm = ProviderFactory.get_provider(settings.llm_provider)

        # Build prompt
        prompt = build_prompt(request.user_message, history, ...)

        # Stream response
        full_response = ""
        async for token in llm.generate_stream(prompt):
            full_response += token
            # Send SSE event
            yield f"data: {json.dumps({'token': token})}\n\n"

        # Send completion event
        yield f"data: {json.dumps({'done': True, 'full_text': full_response})}\n\n"

        # Save to database after streaming completes
        await save_message(db, request.conversation_id, full_response)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )
```

#### 3. Update Frontend to Handle Streaming

```typescript
// In frontend/src/services/api.ts

export const chatService = {
  async sendMessageStream(
    conversation_id: number,
    user_message: string,
    language: string,
    difficulty_level: string,
    onToken: (token: string) => void,
    onComplete: (fullText: string, corrections?: any) => void
  ): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        conversation_id,
        user_message,
        language,
        difficulty_level,
      }),
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let fullText = '';

    while (true) {
      const { done, value } = await reader!.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));

          if (data.token) {
            fullText += data.token;
            onToken(data.token);
          }

          if (data.done) {
            onComplete(data.full_text, data.corrections);
          }
        }
      }
    }
  },
};
```

#### 4. Update React Component

```typescript
// In ConversationInterface.tsx

const [streamingMessage, setStreamingMessage] = useState('');
const [isStreaming, setIsStreaming] = useState(false);

const handleSendMessage = async (message: string) => {
  setIsStreaming(true);
  setStreamingMessage('');

  await chatService.sendMessageStream(
    conversationId,
    message,
    language,
    difficultyLevel,
    // On each token
    (token) => {
      setStreamingMessage((prev) => prev + token);
    },
    // On complete
    (fullText, corrections) => {
      setIsStreaming(false);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: fullText, corrections },
      ]);
      setStreamingMessage('');

      // Start TTS after complete response
      if (ttsEnabled) {
        playTTS(fullText);
      }
    }
  );
};

// In render:
{isStreaming && (
  <MessageBubble role="assistant" isStreaming>
    {streamingMessage}
    <StreamingCursor />
  </MessageBubble>
)}
```

## TTS Integration

**Important**: TTS happens AFTER streaming completes (not during).

**Rationale:**
- TTS engines need complete sentences for natural intonation
- Streaming partial text would sound robotic
- User can read while waiting for TTS

**Flow:**
1. Stream text to UI (user can read immediately)
2. When streaming completes → trigger TTS
3. Play audio while showing complete text

## Performance Impact

**Before Streaming:**
- Wait: 6-8s
- User experience: Feels slow, blocking

**After Streaming:**
- First token: ~500ms
- Complete: 6-8s
- User experience: Feels 3-5x faster, can read while generating

## Testing

```bash
# Test streaming endpoint
curl -N http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 1,
    "user_message": "Hola",
    "language": "spanish",
    "difficulty_level": "A1"
  }'

# Should see:
# data: {"token": "¡"}
# data: {"token": "Hola"}
# data: {"token": "!"}
# ...
# data: {"done": true, "full_text": "¡Hola! ¿Cómo estás?"}
```

## Background Processing (Future Enhancement)

While user is recording/typing, use idle time for:

1. **Conversation Summarization** (after 10+ messages):
   ```python
   # Background task
   async def summarize_old_messages(conversation_id: int):
       messages = await get_messages(conversation_id)
       if len(messages) > 10:
           old_messages = messages[:-5]  # Keep last 5
           summary = await llm.summarize(old_messages)
           await save_summary(conversation_id, summary)
   ```

2. **Pre-warming Models**:
   - Load next likely model based on pattern
   - Pre-cache common responses

3. **Vocabulary Extraction**:
   - Extract key words from conversation
   - Prepare vocabulary cards in background

## Implementation Priority

**Phase 1 (Current Optimizations)** ✅
- Optional corrections (500-1000ms saved)
- Smaller model (3-4s saved)
- Limited history (500ms saved)
- **Total**: 7.5s → ~2-3s

**Phase 2 (Streaming)** ⏭️
- Backend streaming support
- Frontend SSE handling
- UI with streaming indicator
- **Result**: Same 2-3s, but feels instant

**Phase 3 (Background Processing)** 🔮
- Conversation summarization
- Model pre-warming
- Vocabulary extraction

## Notes

- Keep text correction synchronous (don't stream corrections separately)
- Database save happens after streaming completes
- Error handling: If stream fails mid-way, show error and retry
- Consider rate limiting for streaming to prevent abuse
