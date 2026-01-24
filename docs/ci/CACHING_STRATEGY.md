# Caching Strategy Guide

This guide explains Babblr's caching strategy for GitHub Actions to optimize build times and reduce costs.

## Overview

Caching speeds up workflows by reusing previously downloaded or built artifacts:

**Benefits**:
- 30-60% faster builds
- Reduced network usage
- Lower costs (fewer runner minutes)
- Better developer experience

**What we cache**:
- Python dependencies (UV)
- Node.js dependencies (npm)
- Whisper models (~200MB)
- pytest cache
- Build artifacts

## Cache Types

### 1. UV Dependencies Cache

**What**: Python packages managed by UV

**Location**: `~/.cache/uv` and `~/.local/share/uv`

**Key strategy**:
```yaml
key: uv-${{ runner.os }}-py${{ matrix.python-version }}-${{ hashFiles('backend/uv.lock') }}-${{ hashFiles('backend/pyproject.toml') }}
restore-keys: |
  uv-${{ runner.os }}-py${{ matrix.python-version }}-${{ hashFiles('backend/uv.lock') }}-
  uv-${{ runner.os }}-py${{ matrix.python-version }}-
```

**Cache hit conditions**:
- Exact match: Same OS, Python version, and lock files → **Full cache hit**
- Partial match: Same OS and Python, different lock files → **Partial cache hit**
- Miss: Different OS or Python version → **Cache miss**

**Size**: ~50-200 MB depending on dependencies

**Invalidation**: Automatically when `uv.lock` or `pyproject.toml` changes

**Performance**:
- Cold cache: ~2 minutes
- Warm cache: ~30 seconds
- **Speedup: 4x**

### 2. npm Dependencies Cache

**What**: Node.js packages

**Location**: `~/.npm` (automatically managed by `setup-node`)

**Key strategy**:
```yaml
- uses: actions/setup-node@v4
  with:
    cache: 'npm'
    cache-dependency-path: frontend/package-lock.json
```

**Cache hit conditions**:
- Exact match: Same `package-lock.json` → **Cache hit**
- Different: Changed `package-lock.json` → **Cache miss**

**Size**: ~100-500 MB depending on dependencies

**Invalidation**: Automatically when `package-lock.json` changes

**Performance**:
- Cold cache: ~2 minutes
- Warm cache: ~20 seconds
- **Speedup: 6x**

### 3. Whisper Models Cache

**What**: OpenAI Whisper speech recognition models

**Location**: `${{ github.workspace }}/.cache/whisper`

**Key strategy**:
```yaml
key: whisper-${{ runner.os }}-base
restore-keys: |
  whisper-${{ runner.os }}-
```

**Cache hit conditions**:
- Exact match: Same OS → **Cache hit**
- Different OS → **Cache miss**

**Size**: ~200 MB (base model)

**Invalidation**: Manual only (model doesn't change)

**Performance**:
- Cold cache: ~1 minute download + model loading
- Warm cache: Instant
- **Speedup: Eliminates download time**

**Note**: Only cached when `CACHE_WHISPER_MODELS: true`

### 4. pytest Cache

**What**: pytest's internal cache (.pytest_cache)

**Location**: `backend/.pytest_cache`

**Key strategy**:
```yaml
key: pytest-${{ runner.os }}-py${{ matrix.python-version }}-${{ hashFiles('backend/tests/**/*.py') }}
restore-keys: |
  pytest-${{ runner.os }}-py${{ matrix.python-version }}-
```

**Cache hit conditions**:
- Exact match: Same OS, Python, and test files → **Cache hit**
- Partial match: Same OS and Python, different test files → **Partial cache hit**

**Size**: ~1-10 MB

**Invalidation**: When test files change

**Performance**:
- Marginal speedup (~5-10 seconds)
- Enables pytest's --lf (last failed) and --ff (failed first) modes

## Cache Configuration

### Global Cache Control

Set in workflow environment:

```yaml
env:
  CACHE_WHISPER_MODELS: true
  CACHE_RETENTION_DAYS: 7
```

### Per-Job Cache Control

Control caching per job:

```yaml
jobs:
  test:
    steps:
      - name: Cache dependencies
        if: env.CACHE_ENABLED == 'true'
        uses: actions/cache@v4
        with:
          path: ~/.cache/uv
          key: uv-cache-${{ github.run_id }}
```

## Cache Key Design

### Hierarchical Keys

Use hierarchical restore keys for flexibility:

```yaml
key: uv-v1-${{ runner.os }}-py${{ matrix.python-version }}-${{ hashFiles('backend/uv.lock') }}
restore-keys: |
  uv-v1-${{ runner.os }}-py${{ matrix.python-version }}-
  uv-v1-${{ runner.os }}-
```

**Matching order**:
1. Try exact match (full key)
2. Try partial match (first restore-key)
3. Try broader match (second restore-key)
4. Cache miss

### Versioned Keys

Include version prefix to force cache refresh:

```yaml
key: uv-v2-${{ runner.os }}-${{ hashFiles('backend/uv.lock') }}
```

**When to bump version**:
- Major dependency changes
- Build system updates
- Cache corruption

### Dynamic Keys

Use dynamic inputs for unique caching:

```yaml
key: build-${{ github.run_id }}-${{ github.run_attempt }}
```

**Use cases**:
- Build artifacts (unique per run)
- Temporary data
- Test databases

## Cache Limits

### Size Limits

GitHub Actions cache limits:

- **Per cache**: 10 GB (soft limit)
- **Total repository**: 10 GB (old caches evicted)
- **Cache lifetime**: 7 days (unused)

### Eviction Policy

Caches evicted when:
1. Total size > 10 GB (oldest evicted first)
2. Cache unused for 7 days
3. Cache manually deleted

### Optimization Tips

**Keep caches small**:
- Cache only necessary files
- Use specific paths, not wildcards
- Compress large files before caching

**Bad** (caches too much):
```yaml
path: |
  ~/.cache
  ~/.local
```

**Good** (caches specific paths):
```yaml
path: |
  ~/.cache/uv
  ~/.local/share/uv
```

## Cache Management

### Viewing Caches

1. Go to **Actions** tab
2. Click **Caches** in left sidebar
3. View all caches, sizes, and last used

### Deleting Caches

**Via UI**:
1. Go to **Actions** → **Caches**
2. Click three dots next to cache
3. Click **Delete**

**Via GitHub CLI**:
```bash
# List caches
gh cache list

# Delete specific cache
gh cache delete <cache-id>

# Delete all caches
gh cache delete --all
```

**Workflow deletion** (automated):
```yaml
- name: Clear old caches
  run: |
    gh cache delete --all
  env:
    GH_TOKEN: ${{ github.token }}
```

### Cache Debugging

**Check cache status**:

```yaml
- name: Check cache hit
  run: |
    if [ "${{ steps.cache.outputs.cache-hit }}" == "true" ]; then
      echo "Cache hit! Using cached dependencies."
    else
      echo "Cache miss. Installing dependencies."
    fi
```

**Log cache metrics**:

```yaml
- name: Cache metrics
  run: |
    echo "Cache key: ${{ steps.cache.outputs.cache-primary-key }}"
    echo "Cache hit: ${{ steps.cache.outputs.cache-hit }}"
    echo "Cache matched key: ${{ steps.cache.outputs.cache-matched-key }}"
```

## Advanced Patterns

### Conditional Caching

Cache only on main branch:

```yaml
- uses: actions/cache@v4
  if: github.ref == 'refs/heads/main'
  with:
    path: ~/.cache/uv
    key: uv-${{ hashFiles('backend/uv.lock') }}
```

### Multi-Path Caching

Cache multiple paths with one cache:

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/uv
      ~/.local/share/uv
      backend/.pytest_cache
    key: backend-deps-${{ hashFiles('backend/uv.lock') }}
```

### Save Cache Only on Success

```yaml
- name: Install dependencies
  run: uv sync --dev

- uses: actions/cache/save@v4
  if: success()
  with:
    path: ~/.cache/uv
    key: uv-${{ hashFiles('backend/uv.lock') }}
```

### Cross-Job Caching

Share cache between jobs:

```yaml
jobs:
  build:
    steps:
      - uses: actions/cache@v4
        with:
          path: dist/
          key: build-${{ github.run_id }}

  test:
    needs: build
    steps:
      - uses: actions/cache@v4
        with:
          path: dist/
          key: build-${{ github.run_id }}
```

## Monitoring and Metrics

### Cache Hit Rate

Monitor cache effectiveness:

**Target**: > 90% cache hit rate

**Measure**:
1. Count total workflow runs
2. Count cache hits (check logs)
3. Calculate hit rate: `(hits / total) * 100`

### Build Time Comparison

Compare cold vs warm cache builds:

| Step | Cold Cache | Warm Cache | Speedup |
|------|-----------|-----------|---------|
| Install UV deps | 120s | 30s | 4x |
| Install npm deps | 90s | 15s | 6x |
| Download Whisper | 60s | 0s | ∞ |
| **Total** | **270s** | **45s** | **6x** |

### Cost Savings

Estimate cost savings:

**Before caching**:
- 60 runs/month × 10 min = 600 minutes

**After caching**:
- 60 runs/month × 6 min = 360 minutes

**Savings**: 240 minutes/month (40% reduction)

## Best Practices

### 1. Cache Aggressively

Cache everything that's:
- Slow to download
- Expensive to compute
- Unlikely to change

### 2. Use Granular Keys

Include all relevant factors in cache key:
- OS
- Language version
- Lock file hashes
- Configuration files

### 3. Provide Restore Keys

Always provide fallback restore keys:

```yaml
restore-keys: |
  prefix-${{ runner.os }}-
  prefix-
```

### 4. Version Your Caches

Include version in key for easy invalidation:

```yaml
key: v2-deps-${{ hashFiles('lock-file') }}
```

### 5. Monitor Cache Usage

- Check cache hit rates weekly
- Identify cache misses
- Optimize cache keys

### 6. Clean Up Stale Caches

Delete unused caches:
- After major refactors
- When changing build systems
- If hitting size limits

## Troubleshooting

### Low Cache Hit Rate

**Symptoms**:
- Frequent cache misses
- Slow builds
- High runner minute usage

**Solutions**:
1. Check if cache key is too specific
2. Review restore-keys
3. Verify lock files committed to git
4. Check if caches being evicted

### Cache Corruption

**Symptoms**:
- Build fails with cached deps
- Succeeds after cache clear
- Inconsistent behavior

**Solutions**:
1. Delete corrupted cache
2. Bump cache version: `v1` → `v2`
3. Tighten cache key specificity

### Cache Size Too Large

**Symptoms**:
- Caches > 1 GB
- Slow cache save/restore
- Frequent evictions

**Solutions**:
1. Reduce cached paths
2. Exclude unnecessary files
3. Split into multiple caches
4. Use compression

### Cache Not Found

**Symptoms**:
- Always cache miss
- Cache key exists but not found

**Solutions**:
1. Check if cache was evicted (7 day limit)
2. Verify cache key matches
3. Check if repository hit 10 GB limit
4. Ensure workflow has cache access

## Resources

- [GitHub Actions Cache Documentation](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [Cache Action Repository](https://github.com/actions/cache)
- [Cache Eviction Policy](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows#usage-limits-and-eviction-policy)
- [CI Pipeline Architecture](CI_PIPELINE.md)
