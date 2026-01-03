# Contributing to Babblr

Thank you for your interest in contributing to Babblr! We welcome contributions from everyone and are grateful for every contribution, no matter how small.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Contributing Code](#contributing-code)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Code Style Guidelines](#code-style-guidelines)
- [AI-Assisted Development](#ai-assisted-development)
- [License and Copyright](#license-and-copyright)

## Code of Conduct

This project and everyone participating in it is governed by common sense and mutual respect. Please be kind and courteous. We are all here to learn and improve together.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, please include:

- **Clear descriptive title** - Use a clear and descriptive title for the issue
- **Detailed description** - Provide a detailed description of the problem
- **Steps to reproduce** - List the exact steps to reproduce the problem
- **Expected behavior** - Describe what you expected to happen
- **Actual behavior** - Describe what actually happened
- **Environment details** - Include OS, Python version, Node.js version, etc.
- **Screenshots** - If applicable, add screenshots to help explain the problem
- **Additional context** - Any other context about the problem

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Clear descriptive title** - Use a clear and descriptive title for the suggestion
- **Detailed description** - Provide a detailed description of the proposed enhancement
- **Use cases** - Explain why this enhancement would be useful
- **Possible implementation** - If you have ideas on how to implement it, share them
- **Alternatives considered** - Describe any alternative solutions or features you've considered

### Contributing Code

We welcome code contributions! Here's how to get started:

1. **Fork the repository** and create your branch from `main`
2. **Set up your development environment** (see [Development Setup](#development-setup))
3. **Make your changes** following our [Code Style Guidelines](#code-style-guidelines)
4. **Write or update tests** to cover your changes
5. **Ensure all tests pass** and the code builds successfully
6. **Update documentation** if you've changed functionality
7. **Submit a pull request** following the [Pull Request Process](#pull-request-process)

## Development Setup

### Prerequisites

- Python 3.12+
- Node.js 22+ LTS (or 24+)
- uv (Python package manager)

### Backend Setup

```bash
cd backend
uv venv
uv pip install -e ".[dev]"
cp .env.example .env
# Edit .env and add your API keys
```

See [ENVIRONMENT.md](ENVIRONMENT.md) for detailed environment setup.

### Frontend Setup

```bash
cd frontend
npm install
```

### Running the Application

```bash
# Terminal 1: Start backend
./run-backend.sh

# Terminal 2: Start frontend
cd frontend
npm run electron:dev
```

### Running Tests

```bash
# Backend unit tests
cd backend
pytest tests/test_unit.py -v

# Backend integration tests (requires running backend)
cd backend
pytest tests/test_integration.py -v

# All backend tests
cd backend
pytest tests/ -v
```

See [backend/tests/README.md](backend/tests/README.md) for more testing details.

## Pull Request Process

1. **Create a feature branch** - Branch from `main` with a descriptive name (e.g., `feature/add-japanese-support`)
2. **Make your changes** - Keep commits focused and atomic
3. **Write clear commit messages** - Use present tense ("Add feature" not "Added feature")
4. **Update documentation** - Update README.md, DEVELOPMENT.md, or other docs as needed
5. **Test your changes** - Ensure all tests pass and functionality works as expected
6. **Submit your PR** with:
   - Clear title describing the change
   - Description of what changed and why
   - Reference to any related issues (e.g., "Fixes #123")
   - Screenshots/recordings for UI changes
   - Note if AI assistance was used (see [AI-Assisted Development](#ai-assisted-development))

7. **Respond to feedback** - Be open to constructive criticism and suggestions
8. **Maintain your PR** - Keep it up to date with the main branch

### PR Review Process

- Pull requests will be reviewed by project maintainers
- We aim to review PRs within a few days, but please be patient
- Feedback will be constructive and aimed at maintaining code quality
- Once approved, your PR will be merged by a maintainer

## Code Style Guidelines

### Python (Backend)

- **Follow PEP 8** - Python style guidelines
- **Use type hints** - Add type hints for function parameters and return values
- **Write docstrings** - Use clear docstrings for classes and functions
- **Line length**: 100 characters (configured in ruff)
- **Formatting**: Run `ruff format` before committing
- **Linting**: Run `ruff check` and fix any issues

Example:
```python
def calculate_difficulty_level(text: str, current_level: str) -> str:
    """
    Calculate the appropriate CEFR difficulty level based on text complexity.
    
    Args:
        text: The input text to analyze
        current_level: The user's current CEFR level (A1-C2)
    
    Returns:
        The recommended CEFR level as a string
    """
    # Implementation here
    pass
```

### TypeScript (Frontend)

- **Use TypeScript** - Leverage type safety
- **Functional components** - Use React functional components with hooks
- **Clear naming** - Use descriptive variable and function names
- **Component structure** - Keep components focused and single-purpose
- **Props interfaces** - Define interfaces for component props

Example:
```typescript
interface ConversationProps {
  targetLanguage: string;
  cefrLevel: string;
  onMessageSent: (message: string) => void;
}

const Conversation: React.FC<ConversationProps> = ({ 
  targetLanguage, 
  cefrLevel, 
  onMessageSent 
}) => {
  // Component implementation
};
```

### General Guidelines

- **Keep functions focused** - Each function should do one thing well
- **Write self-documenting code** - Use clear names that explain intent
- **Add comments sparingly** - Comment the "why", not the "what"
- **Handle errors gracefully** - Provide meaningful error messages
- **Test edge cases** - Consider and test boundary conditions

## AI-Assisted Development

**AI-assisted coding is welcomed and encouraged!** We recognize that AI tools like GitHub Copilot, ChatGPT, Claude, and others can significantly boost productivity and code quality.

### Guidelines for AI-Assisted Contributions

1. **Disclosure**: When submitting a PR that used AI assistance, please mention it in the PR description
   - Example: "AI-assisted: Used GitHub Copilot for boilerplate code generation"
   - Example: "AI-assisted: Used Claude to help design the error handling logic"

2. **Human Review Required**: All AI-generated code MUST be:
   - **Reviewed** - Carefully reviewed by a human before submission
   - **Understood** - Fully understood by the contributor
   - **Tested** - Thoroughly tested to ensure it works correctly
   - **Adapted** - Modified as needed to fit the project's style and requirements

3. **Quality Standards**: AI-assisted code must meet the same quality standards as any other contribution:
   - Follows our code style guidelines
   - Includes appropriate tests
   - Has clear documentation
   - Handles errors properly
   - Is maintainable and readable

4. **What to Avoid**:
   - Don't blindly copy-paste AI-generated code without understanding it
   - Don't submit large AI-generated blocks without review and testing
   - Don't rely on AI for critical security-related code without extra scrutiny
   - Don't use AI-generated code that may have licensing issues

### Why We Embrace AI Assistance

- **Productivity** - AI can help write boilerplate, tests, and documentation faster
- **Learning** - AI can suggest patterns and approaches you might not have considered
- **Quality** - AI can help catch bugs and suggest improvements
- **Innovation** - We believe in using the best tools available to build better software

We trust our contributors to use AI responsibly and maintain high-quality standards.

## License and Copyright

### Dual License Model

Babblr uses a dual licensing model:

1. **AGPL-3.0** - For open-source use
   - Free to use for personal, educational, and commercial purposes *if you comply with the AGPL*
   - Requires that modifications be shared under AGPL-3.0 when distributed
   - Network use triggers source-availability requirements (AGPL copyleft)

2. **Commercial License** - For proprietary use
   - Required for proprietary / closed-source applications or services when you cannot comply with AGPL source-sharing requirements
   - Contact the project maintainers for commercial licensing terms (see `COMMERCIAL_LICENSE.md`)

### Contributing Your Code

By contributing to Babblr, you agree that:

1. **Your contributions will be licensed** under the same dual license (AGPL-3.0 + Commercial)
2. **You have the right** to submit the code and grant these licenses
3. **You understand** that the project maintainers may use your contribution in both open-source and commercial contexts
4. **You retain copyright** of your contributions, but grant the project necessary rights

### Contributor License Agreement (CLA)

To keep dual licensing possible, Babblr requires a CLA for code contributions.

- Read: `CLA.md`
- How to sign: include the sentence **"I agree to the Babblr CLA"** in your PR description (or first comment).
  This is treated as your electronic signature for the CLA.

### Contributor Rights

- **Recognition** - Contributors will be acknowledged in the project
- **Open Source** - Your code will always remain available under AGPL-3.0
- **Benefit Sharing** - Commercial success may lead to project improvements that benefit all contributors

### Questions About Licensing?

If you have questions about the licensing model or how it affects your contribution, please open an issue or contact the maintainers before submitting your contribution.

## Getting Help

- **Documentation** - Check [README.md](README.md), [DEVELOPMENT.md](DEVELOPMENT.md), and other docs
- **Issues** - Search existing issues or create a new one
- **Discussions** - Use GitHub Discussions for questions and general discussion
- **Be patient** - Maintainers are often volunteers with limited time

## Recognition

Contributors are the heart of open source. We appreciate every contribution, whether it's:
- Code improvements
- Bug reports
- Documentation updates
- Feature suggestions
- Testing and feedback
- Spreading the word about Babblr

Thank you for contributing to Babblr! 🚀
