---
description: Test-Driven Development workflow - plan, write tests first, then implement
argument-hint: <feature-description>
---

# Test-Driven Development (TDD) Workflow

You are guiding a strict Test-Driven Development process. Follow these phases in order.

## Task Description

$ARGUMENTS

**If no task description was provided above, ask the user to describe what they want to implement before proceeding.**

---

## Phase 1: PLAN (Use Plan Mode)

Before writing any code, enter plan mode and thoroughly analyze the task:

### 1.1 Understand the Requirements
- What is the core functionality being requested?
- What are the inputs and outputs?
- What existing code/patterns in the codebase should be followed?

### 1.2 Architecture & Design
- Identify which files need to be created or modified
- Show the proposed file structure
- Explain how this fits into the existing codebase architecture
- Identify dependencies and interfaces

### 1.3 Implementation Steps
Create a numbered list of implementation steps, including:
- Test files to create or modify
- Implementation files to create/modify
- Any configuration changes needed

### 1.4 Clarification Questions
Ask the user about any ambiguities:
- Edge cases that need clarification
- Error handling preferences
- Naming conventions
- Integration points with existing code

**Wait for user approval of the plan before proceeding to Phase 2.**

---

## Phase 2: RED (Write Failing Tests)

Write comprehensive tests BEFORE any implementation code.

### 2.1 Create and Modify Test File(s)
- Follow the project's existing test patterns and conventions
- Use descriptive test names that explain the expected behavior

### 2.2 Test Categories to Include

**Happy Path Tests:**
- Normal expected usage
- Valid inputs producing expected outputs

**Edge Case Tests:**
- Empty inputs (null, undefined, empty strings, empty arrays)
- Boundary values (0, -1, max values, min values)
- Single element collections
- Very large inputs

**Error Case Tests:**
- Invalid input types
- Missing required fields
- Out-of-range values
- Network/IO failures (if applicable)
- Permission/authorization failures (if applicable)

**Integration Tests (if applicable):**
- Interaction with other components
- Database operations
- API calls

### 2.3 Run Tests (Should Fail)
Run the test suite to confirm tests fail as expected:
```bash
# Python
uv run pytest <test_file> -v

# JavaScript/TypeScript
npm test -- <test_file>
```

The tests SHOULD fail at this point - this confirms:
1. The tests are actually being run
2. The tests are testing real behavior (not passing by accident)

**Show the user the failing test output before proceeding.**

---

## Phase 3: GREEN (Implement Minimal Code)

Now write the minimum code necessary to make all tests pass.

### 3.1 Implementation Guidelines
- Write the simplest code that makes tests pass
- Don't add features not covered by tests
- Don't optimize prematurely
- Follow existing code patterns in the codebase

### 3.2 Run Tests (Should Pass)
```bash
# Python
uv run pytest <test_file> -v

# JavaScript/TypeScript
npm test -- <test_file>
```

**If tests fail:**
- Fix the implementation (not the tests, unless they have bugs)
- Re-run until all tests pass

**Show the user the passing test output.**

---

## Phase 4: REFACTOR (Improve Code Quality)

With passing tests as a safety net, improve the code:

### 4.1 Refactoring Checklist
- Remove code duplication (DRY)
- Improve variable/function names for clarity
- Extract reusable functions/methods
- Simplify complex logic
- Add appropriate comments for non-obvious code
- Ensure consistent code style (run linter)

### 4.2 Verify Tests Still Pass
After EACH refactoring change, run tests:
```bash
# Python
uv run pytest <test_file> -v

# JavaScript/TypeScript
npm test -- <test_file>
```

**Never break tests during refactoring. If a test fails, undo the refactor.**

---

## Phase 5: REVIEW

### 5.1 Final Verification
- Run the full test suite to check for regressions
- Run linting/formatting checks
- Review the changes with the user

### 5.2 Summary
Provide a summary of:
- Files created/modified
- Test coverage (number of test cases)
- Any remaining TODOs or known limitations

---

## TDD Principles to Follow

1. **Never write implementation code without a failing test**
2. **Write only enough test to fail** (one test at a time if needed)
3. **Write only enough code to pass** the failing test
4. **Refactor continuously** while keeping tests green
5. **Tests are documentation** - they describe expected behavior
6. **Fast feedback** - run tests frequently

## Project-Specific Notes

For this Python project (babblr):
- Tests are in `backend/tests/`
- Use pytest with `uv run pytest`
- Follow existing patterns in `test_unit.py` and `test_integration.py`
- Use pytest markers for different test types (`@pytest.mark.integration`)
