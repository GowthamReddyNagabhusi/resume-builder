# Contributing to Resume Builder

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the Resume Builder project.

## Code of Conduct

Please be respectful and constructive in all interactions. We're building a community where everyone feels welcome.

## Getting Started

### 1. Fork the Repository

Click the "Fork" button on the GitHub repository page to create your own copy.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/resume-builder.git
cd resume-builder
```

### 3. Add Upstream Remote

```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/resume-builder.git
git fetch upstream
```

### 4. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` for new features
- `fix/` for bug fixes
- `docs/` for documentation
- `refactor/` for code refactoring
- `test/` for test additions

## Development Workflow

### Setting Up Development Environment

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Making Changes

1. **Write code** following the style guidelines below
2. **Run tests** to ensure nothing breaks
3. **Run linters** to maintain code quality
4. **Write/update documentation** if applicable
5. **Commit** with clear, descriptive messages

### Backend Code Style

**Python** uses Black and isort:

```bash
# Format code
black backend/

# Sort imports
isort backend/

# Check code quality
pylint backend/app

# Run type hints check
mypy backend/app
```

Key style points:
- Use type hints for all function signatures
- Follow PEP 8
- Max line length: 100 characters
- Docstrings for all public functions and classes

Example:

```python
def generate_resume(
    job_description: str,
    career_data: Dict[str, Any],
    template_id: str
) -> GeneratedResume:
    """Generate a resume tailored to a job description.
    
    Args:
        job_description: Full job description text
        career_data: User's career data dictionary
        template_id: Resume template ID
        
    Returns:
        GeneratedResume: The generated resume object
        
    Raises:
        ValueError: If template_id is invalid
    """
```

### Frontend Code Style

**JavaScript** uses Prettier and ESLint:

```bash
# Format code
npm run format

# Check for linting issues
npm run lint

# Fix linting issues
npm run lint -- --fix
```

Key style points:
- Use semicolons
- Use double quotes for strings
- 2 spaces for indentation
- Functional components with hooks (not class components)
- PropTypes for prop validation

Example:

```javascript
import PropTypes from 'prop-types';

export default function ResumeForm({ onSubmit }) {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const handleSubmit = async (data) => {
    setLoading(true);
    setError(null);
    try {
      await onSubmit(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    // JSX here
  );
}

ResumeForm.propTypes = {
  onSubmit: PropTypes.func.isRequired
};
```

## Testing

### Backend Tests

```bash
# Run all tests
pytest backend/

# Run with coverage
pytest --cov=backend backend/

# Run specific test file
pytest backend/tests/test_auth.py

# Run with verbose output
pytest -v backend/
```

All new features should include tests. Aim for 80%+ code coverage.

Example test:

```python
def test_resume_generation():
    """Test resume generation creates a valid resume."""
    job_DESC = "Senior Python developer..."
    career_data = {...}
    
    resume = generate_resume(job_desc, career_data, "modern")
    
    assert resume.id is not None
    assert resume.title is not None
    assert resume.content is not None
    assert len(resume.content.experience) > 0
```

### Frontend Tests

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- test_utils.test.js

# Watch mode
npm run test:watch
```

Example test:

```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import ResumeForm from '../ResumeForm';

describe('ResumeForm', () => {
  it('should submit form with valid data', async () => {
    const mockSubmit = jest.fn();
    render(<ResumeForm onSubmit={mockSubmit} />);
    
    fireEvent.change(screen.getByLabelText(/job description/i), {
      target: { value: 'Senior developer...' }
    });
    
    fireEvent.click(screen.getByText(/generate/i));
    
    expect(mockSubmit).toHaveBeenCalledWith({
      jobDescription: 'Senior developer...'
    });
  });
});
```

## Commit Messages

Write clear, descriptive commit messages:

**Format**:
```
CATEGORY: Short description (50 chars or less)

Optional longer explanation (72 chars per line)
explaining the why and what of the change.

- Bullet point 1
- Bullet point 2
```

**Categories**:
- `FEAT`: New feature
- `FIX`: Bug fix
- `DOCS`: Documentation
- `STYLE`: Code style changes
- `REFACTOR`: Code refactoring
- `TEST`: Test additions/changes
- `CHORE`: Build, dependencies, etc.

**Examples**:

```
FEAT: Add resume PDF export functionality

Implements PDF generation using reportlab library.
Converts generated resume JSON to styled PDF with proper
formatting and page layout.

- Add PDFGenerator class
- Add export DOCX format support
- Update resume model with export methods

Fixes #123
```

```
FIX: Fix JWT token refresh endpoint

The refresh endpoint was not properly invalidating
the old token. Added token blacklist tracking.

Fixes #456
```

## Pull Request Process

### Before Submitting

1. **Update your fork**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Verify all tests pass**:
   ```bash
   pytest backend/
   npm test
   ```

### Creating a Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill in the PR template

**PR Template**:

```markdown
## Description
Brief description of the changes

## Related Issues
Closes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Breaking change

## Testing
Describe how you tested the changes

## Screenshots (if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No new warnings generated
```

### Review Process

- At least one maintainer will review your code
- Changes may be requested before approval
- Once approved, your PR will be merged

## Documentation

### Backend Documentation

Document all public APIs with docstrings:

```python
def analyze_job(job_description: str) -> JobAnalysis:
    """Analyze a job description using AI.
    
    Parses the job description to extract required skills,
    experience level, and key responsibilities.
    
    Args:
        job_description: Full job description text
        
    Returns:
        JobAnalysis: Structured job analysis with:
            - required_skills: List of required skills
            - seniority_level: Entry/mid/senior level
            - key_responsibilities: List of main duties
            
    Raises:
        ValueError: If job_description is empty
        AIProviderError: If AI service fails
        
    Example:
        >>> analysis = analyze_job("Need Python dev...")
        >>> print(analysis.required_skills)
        ['Python', 'FastAPI', 'PostgreSQL']
    """
```

### Frontend Documentation

Document React components:

```javascript
/**
 * ResumePreview component displays a formatted resume.
 * 
 * @component
 * 
 * @param {Object} props - Component props
 * @param {Object} props.resume - Resume object with content
 * @param {string} props.template - Template name (modern|classic)
 * @param {Function} props.onDownload - Download callback
 * 
 * @example
 * const resume = { id: '123', content: {...} };
 * return (
 *   <ResumePreview 
 *     resume={resume}
 *     template="modern"
 *     onDownload={handleDownload}
 *   />
 * )
 */
export function ResumePreview({ resume, template, onDownload }) {
  // Component code
}
```

## Reporting Bugs

### Bug Report Template

```markdown
## Description
Brief description of the bug

## Reproduction Steps
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: Windows/Mac/Linux
- Python/Node version
- Browser (if frontend)

## Screenshots
If applicable

## Logs
Error messages and stack traces
```

## Feature Requests

### Feature Request Template

```markdown
## Description
What new feature would you like?

## Problem It Solves
What problem does this solve?

## Proposed Solution
How should this work?

## Alternatives
Other approaches you've considered

## Additional Context
Any other relevant information
```

## Code Review Guidelines

When reviewing code:

1. **Functionality**: Does it work as intended?
2. **Tests**: Are tests included? Good coverage?
3. **Style**: Does it follow guidelines?
4. **Documentation**: Is it well documented?
5. **Performance**: Any efficiency concerns?
6. **Security**: Any security implications?

Be constructive and respectful in reviews. Ask questions rather than asserting.

## Development Tools

### Useful Commands

**Backend**:
```bash
# Run in watch mode
uvicorn backend.app.main:app --reload

# Check database
psql postgresql://user:pass@localhost/resume_builder

# Generate migration
alembic revision --autogenerate -m "Add field"

# Type checking
mypy backend/
```

**Frontend**:
```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Analyze bundle size
npm run analyze
```

## Getting Help

- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Use GitHub Issues for bugs and features
- **Chat**: Join our community Discord server
- **Email**: Contact maintainers at `maintainers@resumebuilder.local`

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project README

Thank you for making Resume Builder better! 🚀

---

**Happy contributing!**
