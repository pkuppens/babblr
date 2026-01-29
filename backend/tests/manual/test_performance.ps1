# Performance test script for Babblr backend

Write-Host "=== Babblr Performance Test ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Create conversation
Write-Host "1. Creating test conversation (A1 level)..." -ForegroundColor Yellow
$conv = Invoke-RestMethod -Uri 'http://localhost:8000/conversations' -Method Post -ContentType 'application/json' -Body '{"language": "spanish", "difficulty_level": "A1", "topic_id": "travel"}'
Write-Host "   Created conversation ID: $($conv.id)" -ForegroundColor Green
Write-Host ""

# Test 2: Initial message with corrections (A1)
Write-Host "2. Testing Initial Message (A1 - WITH corrections)..." -ForegroundColor Yellow
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$response = Invoke-WebRequest -Uri 'http://localhost:8000/chat/initial-message' -Method Post -ContentType 'application/json' -Body "{`"conversation_id`": $($conv.id), `"language`": `"spanish`", `"difficulty_level`": `"A1`", `"topic_id`": `"travel`"}"
$stopwatch.Stop()
$json = $response.Content | ConvertFrom-Json
$backendTime = $response.Headers['x-response-time']
Write-Host "   Backend time: $backendTime" -ForegroundColor Green
Write-Host "   Total time: $($stopwatch.ElapsedMilliseconds)ms" -ForegroundColor Green
Write-Host "   Response: $($json.assistant_message.Substring(0, [Math]::Min(80, $json.assistant_message.Length)))..." -ForegroundColor Gray
Write-Host ""

# Test 3: Regular chat message (A1 with corrections)
Write-Host "3. Testing Chat Message (A1 - WITH corrections)..." -ForegroundColor Yellow
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$response = Invoke-WebRequest -Uri 'http://localhost:8000/chat' -Method Post -ContentType 'application/json' -Body "{`"conversation_id`": $($conv.id), `"user_message`": `"Hola, ¿cómo estás?`", `"language`": `"spanish`", `"difficulty_level`": `"A1`"}"
$stopwatch.Stop()
$json = $response.Content | ConvertFrom-Json
$backendTime = $response.Headers['x-response-time']
Write-Host "   Backend time: $backendTime" -ForegroundColor Green
Write-Host "   Total time: $($stopwatch.ElapsedMilliseconds)ms" -ForegroundColor Green
Write-Host "   Response: $($json.assistant_message.Substring(0, [Math]::Min(80, $json.assistant_message.Length)))..." -ForegroundColor Gray
Write-Host ""

# Test 4: Create B2 conversation (no corrections)
Write-Host "4. Creating test conversation (B2 level - no corrections)..." -ForegroundColor Yellow
$convB2 = Invoke-RestMethod -Uri 'http://localhost:8000/conversations' -Method Post -ContentType 'application/json' -Body '{"language": "spanish", "difficulty_level": "B2", "topic_id": "travel"}'
Write-Host "   Created conversation ID: $($convB2.id)" -ForegroundColor Green
Write-Host ""

# Test 5: Chat message without corrections (B2)
Write-Host "5. Testing Chat Message (B2 - NO corrections, should be faster)..." -ForegroundColor Yellow
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$response = Invoke-WebRequest -Uri 'http://localhost:8000/chat' -Method Post -ContentType 'application/json' -Body "{`"conversation_id`": $($convB2.id), `"user_message`": `"Hola, me gustaría hablar sobre viajar por España.`", `"language`": `"spanish`", `"difficulty_level`": `"B2`"}"
$stopwatch.Stop()
$json = $response.Content | ConvertFrom-Json
$backendTime = $response.Headers['x-response-time']
Write-Host "   Backend time: $backendTime" -ForegroundColor Green
Write-Host "   Total time: $($stopwatch.ElapsedMilliseconds)ms" -ForegroundColor Green
Write-Host "   Response: $($json.assistant_message.Substring(0, [Math]::Min(80, $json.assistant_message.Length)))..." -ForegroundColor Gray
Write-Host ""

Write-Host "=== Performance Test Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  - A1 (with corrections): More processing time for correction LLM call"
Write-Host "  - B2 (no corrections): Faster due to skipped correction step"
Write-Host "  - Using llama3.2:1b model (faster than llama3.2:latest)"
Write-Host "  - History limited to last 5 messages"
