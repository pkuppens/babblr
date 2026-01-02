# Whisper Speech Recognition Optimization Guide

## Current Configuration

You are currently using Whisper **`base`** model, which is a good balance but may not be optimal for noisy audio or when you need faster transcription.

## Model Options

Whisper models come in different sizes with trade-offs between speed and accuracy:

| Model | Size | Speed (CPU) | Speed (GPU) | Accuracy | Best For |
|-------|------|-------------|-------------|----------|----------|
| `tiny` | ~39M | ⚡⚡⚡ Fastest | ⚡⚡⚡⚡⚡ Very Fast | ⭐⭐ Lower | Quick testing, low-resource devices |
| `base` | ~74M | ⚡⚡ Fast | ⚡⚡⚡⚡ Fast | ⭐⭐⭐ Good | **Current default** - balanced |
| `small` | ~244M | ⚡ Moderate | ⚡⚡⚡ Fast | ⭐⭐⭐⭐ Better | **Recommended for noisy audio** |
| `medium` | ~769M | 🐌 Slower | ⚡⚡ Moderate | ⭐⭐⭐⭐⭐ High | High accuracy needs |
| `large` | ~1550M | 🐌🐌 Very Slow | ⚡ Fast | ⭐⭐⭐⭐⭐ Best | Best accuracy, needs ~10GB VRAM |

**Note:** All models benefit from GPU acceleration (5-10x speedup). GPU is **not required** for any model, but highly recommended for `medium` and `large` models.

## Recommended Changes

### Option 1: Upgrade to `small` Model (Recommended)

The `small` model provides significantly better accuracy, especially in noisy conditions, with only a moderate speed penalty.

**To change:**
1. Edit `backend/.env`:
   ```bash
   WHISPER_MODEL=small
   ```
2. Restart the backend
3. The model will download automatically on first use (~244MB)

**Benefits:**
- ✅ Better accuracy, especially with background noise
- ✅ Still reasonably fast
- ✅ Better handling of accented speech

### Option 2: Use `medium` for Maximum Accuracy

If accuracy is more important than speed:

```bash
WHISPER_MODEL=medium
```

**Note:** This model is ~769MB and will be slower, but provides the best accuracy for noisy audio.

## Speed Optimization

### Current Optimizations Applied

The code now includes:
- ✅ `fp16=True` - Uses half-precision for faster processing
- ✅ `beam_size=5` - Optimized beam search
- ✅ Language specification - Faster when language is known

### Additional Speed Improvements

#### Option A: Use GPU Acceleration (Recommended)

**All Whisper models automatically use GPU if available!**

For setup instructions, see [SETUP.md](SETUP.md#4-install-pytorch-with-cuda-gpu-acceleration).

**Benefits:**
- ⚡ **5-10x faster** transcription on GPU
- ✅ Works with all model sizes
- ✅ Automatic detection - no configuration needed

**Performance Comparison (5-second audio):**
- CPU (`base`): ~2-5 seconds → GPU: ~0.5-1 second ⚡
- CPU (`small`): ~3-7 seconds → GPU: ~0.7-1.5 seconds ⚡
- CPU (`large`): ~10-20 seconds → GPU: ~2-4 seconds ⚡

#### Option B: Use `faster-whisper` Library

`faster-whisper` is a reimplementation of Whisper using CTranslate2, providing **4x faster** transcription.

**Installation:**
```bash
cd backend
uv pip install faster-whisper
```

**Note:** Requires code changes to use `faster-whisper` instead of `openai-whisper`.

**Benefits:**
- ⚡ 4x faster transcription
- ✅ Same accuracy as original Whisper
- ✅ Lower memory usage
- ✅ Better GPU support

## Noise Reduction

### Current Limitations

The current implementation doesn't include audio preprocessing for noise reduction. For noisy audio, consider:

1. **Upgrade to `small` or `medium` model** - These handle noise better
2. **Use `faster-whisper`** - Has better noise handling
3. **Add audio preprocessing** - Can be implemented to normalize and filter audio

### Audio Preprocessing (Future Enhancement)

We can add audio preprocessing to reduce noise:
- Normalize audio levels
- Apply noise reduction filters
- Enhance speech frequencies

This would require additional dependencies like `noisereduce` or `librosa`.

## Quick Comparison

### Current Setup (`base` model on CPU):
- Speed: ~2-5 seconds for 5-second audio
- Accuracy: Good for clean audio, moderate for noisy
- Memory: ~1GB RAM

### Current Setup (`base` model on GPU):
- Speed: ~0.5-1 second for 5-second audio ⚡
- Accuracy: Good for clean audio, moderate for noisy
- Memory: ~1GB RAM + ~500MB VRAM

### Recommended (`small` model on CPU):
- Speed: ~3-7 seconds for 5-second audio
- Accuracy: Better for noisy audio
- Memory: ~2GB RAM

### Recommended (`small` model on GPU):
- Speed: ~0.7-1.5 seconds for 5-second audio ⚡
- Accuracy: Better for noisy audio
- Memory: ~2GB RAM + ~1GB VRAM

### With `faster-whisper` + `small` + GPU:
- Speed: ~0.3-0.7 seconds for 5-second audio ⚡⚡
- Accuracy: Better for noisy audio
- Memory: ~1.5GB RAM + ~800MB VRAM

## How to Change Model

1. **Edit `backend/.env`:**
   ```bash
   # For better accuracy (recommended)
   WHISPER_MODEL=small
   
   # Or for maximum accuracy (slower)
   # WHISPER_MODEL=medium
   ```

2. **Restart backend:**
   ```bash
   # Stop current backend (Ctrl+C)
   # Then restart
   ./run-backend.sh
   ```

3. **First run will download the model** (one-time download, ~244MB for small, ~769MB for medium)

## Testing

After changing the model:

1. Record a test audio with some background noise
2. Compare transcription accuracy
3. Check transcription speed in console logs
4. Adjust model size based on your needs

## Troubleshooting

### GPU Not Detected

See [SETUP.md](SETUP.md#troubleshooting) for CUDA setup and troubleshooting.

### "Model not found" error
- The model will download automatically on first use
- Ensure you have internet connection
- Check disk space (models are 100MB-3GB)

### Still too slow
- Consider `faster-whisper` library (requires code change)
- Use GPU if available (see [SETUP.md](SETUP.md#4-install-pytorch-with-cuda-gpu-acceleration))
- Try `tiny` model for fastest speed (lower accuracy)

### Still inaccurate with noise
- Upgrade to `small` or `medium` model
- Ensure language is correctly specified
- Consider audio preprocessing (future enhancement)

## Summary

**For your current issues (noise + speed):**

1. **Immediate fix:** Change to `small` model in `.env`
   ```bash
   WHISPER_MODEL=small
   ```

2. **Best solution:** Use `faster-whisper` library (requires code update)
   - 4x faster + better noise handling

3. **Maximum accuracy:** Use `medium` model (slower but best for noise)

The code has been updated with optimized transcription settings that should help with both speed and accuracy.

