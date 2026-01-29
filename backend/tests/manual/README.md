# Manual Test Scripts

This directory contains manual test scripts that are not part of the automated test suite.

## Scripts

### test_performance.ps1

PowerShell script for testing backend API performance with different configurations.

**Usage:**
```powershell
cd backend/tests/manual
.\test_performance.ps1
```

**What it tests:**
- Initial message generation time (A1 level with corrections)
- Chat message response time (A1 level with corrections)
- Chat message response time (B2 level without corrections)
- Comparison of performance with/without text corrections

**Requirements:**
- PowerShell
- Backend running on http://localhost:8000
- Ollama service running (if using local LLM)

**Expected results:**
- Initial message: 2-4s
- Chat with corrections (A1): 3-5s
- Chat without corrections (B2): 2-3s

**Note:** This script is not run by pytest. It's for manual performance validation.
