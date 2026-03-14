# AI Pipeline Guide

## Overview

The Resume Builder AI pipeline is a modular, extensible system for automating resume generation. It uses specialized AI tasks that process career data and generate ATS-optimized resume content.

## Architecture

### High-Level Flow

```
Job Description Input
        ↓
┌─────────────────────────────────────┐
│   Job Analysis (JobAnalyzer)        │  Extract requirements, skills, level
└──────────────────┬──────────────────┘
                   ↓
┌─────────────────────────────────────┐
│  Relevance Ranking (RelevanceRanker)│  Score career items against job
└──────────────────┬──────────────────┘
                   ↓
┌─────────────────────────────────────┐
│  Content Generation (ContentGenerate)│  Generate bullets and descriptions
└──────────────────┬──────────────────┘
                   ↓
┌─────────────────────────────────────┐
│  Bullet Enhancement (BulletEnhancer) │  Improve bullet points
└──────────────────┬──────────────────┘
                   ↓
┌─────────────────────────────────────┐
│  ATS Optimization (ATSOptimizer)    │  Optimize for tracking systems
└──────────────────┬──────────────────┘
                   ↓
Resume JSON Output
```

## AI Providers

The system supports multiple AI providers with a fallback mechanism.

### Supported Providers

#### 1. OpenAI

Uses GPT-3.5-turbo or GPT-4.

```python
from app.ai import AIPipeline

# Initialize with OpenAI
pipeline = AIPipeline(provider_name="openai")

# Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4
```

**Advantages**:
- Best quality (GPT-4)
- Fast (3.5-turbo)
- Reliable
- Good pricing

**Disadvantages**:
- Requires API key
- Cost per request
- Rate limited

#### 2. Anthropic Claude

Uses Claude 2 or Claude 3.

```python
pipeline = AIPipeline(provider_name="anthropic")

# Configuration
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

**Advantages**:
- Excellent quality
- Long context window
- Good for detailed analysis

**Disadvantages**:
- Slower than GPT-3.5
- Higher cost
- Requires API key

#### 3. Mock Provider (Testing)

Returns mock data without calling external APIs.

```python
pipeline = AIPipeline(provider_name="mock")
```

**Advantages**:
- No API key needed
- Instant responses
- Great for development/testing

**Disadvantages**:
- Returns dummy data only
- Not suitable for production

#### 4. Local LLM (Ollama)

Run LLMs locally using Ollama.

```python
pipeline = AIPipeline(provider_name="ollama", model="llama2")

# Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

**Advantages**:
- No API keys needed
- Privacy (stays local)
- No costs

**Disadvantages**:
- Requires local setup
- Slower than cloud APIs
- Less accurate for specific tasks

### Provider Configuration

Set the provider via environment variables:

```bash
# Use OpenAI
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo

# Or use Anthropic
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Or use local Ollama
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Or use mock for testing
AI_PROVIDER=mock
```

## AI Tasks

Each task is specialized for a specific purpose.

### 1. Job Analyzer

Analyzes job descriptions to extract structured requirements.

```python
from app.ai.tasks import JobAnalyzer

analyzer = JobAnalyzer()
analysis = analyzer.run(
    job_description="We're looking for a Python developer..."
)

# Returns:
{
    "title": "Senior Python Developer",
    "company": "Example Corp",
    "level": "senior",  # entry, mid, senior, lead
    "required_skills": ["Python", "FastAPI", "PostgreSQL"],
    "nice_to_have": ["Kubernetes", "Docker"],
    "experience_years": 5,
    "key_responsibilities": [
        "Design scalable services",
        "Lead technical interviews",
        ...
    ],
    "compensation": {
        "salary_min": 120000,
        "salary_max": 180000,
        "currency": "USD"
    }
}
```

### 2. Relevance Ranker

Scores user's career items against job requirements.

```python
from app.ai.tasks import RelevanceRanker
from app.database.models import User

ranker = RelevanceRanker()

# Score user's experience
scores = ranker.run(
    job_analysis=job_analysis,
    career_data=user.career_data,
    items=user.experience.all()
)

# Returns:
{
    "overall_match": 0.92,  # 0-1 score
    "skill_match": 0.88,
    "experience_match": 0.95,
    "ranked_items": [
        {
            "item_id": "uuid",
            "type": "experience",
            "title": "Senior Engineer at Google",
            "relevance_score": 0.98,
            "key_points": [
                "Exact skill match: Python, FastAPI",
                "5+ years experience matches requirement",
                "Leadership experience matches",
            ]
        },
        {...}
    ]
}
```

### 3. Content Generator

Generates resume bullets and descriptions.

```python
from app.ai.tasks import ContentGenerator

generator = ContentGenerator()

# Generate bullets for an experience
bullets = generator.run(
    context={
        "item": experience_object,
        "job_analysis": job_analysis,
        "relevance_context": "Top match for this role"
    }
)

# Returns:
{
    "title": "Senior Software Engineer | Google",
    "date_range": "2022 - Present",
    "summary": "Led development of core infrastructure...",
    "bullets": [
        "Architected microservices reducing latency 40%",
        "Led team of 5 engineers on platform projects",
        "Mentored 10+ junior developers",
        "Improved deployment frequency from weekly to daily"
    ],
    "technologies": ["Python", "FastAPI", "PostgreSQL", "Kubernetes"],
    "impact_metrics": [
        "40% latency reduction",
        "1B+ daily requests served",
        "99.99% uptime maintained"
    ]
}
```

### 4. Bullet Enhancer

Improves bullet points for impact and clarity.

```python
from app.ai.tasks import BulletEnhancer

enhancer = BulletEnhancer()

# Enhance bullets
enhanced = enhancer.run(
    bullets=[
        "Worked on backend",
        "Fixed bugs",
        "Helped team members"
    ],
    context={
        "job_analysis": job_analysis,
        "role": "Staff Engineer",
        "company": "Tech Company"
    }
)

# Returns:
[
    "Designed and shipped critical backend services handling 10B+ requests/month",
    "Resolved high-priority production issues reducing MTTR by 60%",
    "Mentored 8 junior engineers, with 3 promoted within 2 years"
]
```

### 5. ATS Optimizer

Optimizes content for Applicant Tracking Systems.

```python
from app.ai.tasks import ATSOptimizer

optimizer = ATSOptimizer()

# Optimize resume
optimized = optimizer.run(
    resume_content=generated_resume,
    job_description=job_description,
    template_format="modern"  # Some templates require different formatting
)

# Returns:
{
    "original_keywords": ["Python", "FastAPI"],
    "added_keywords": ["REST API", "Database Design"],
    "content": {
        "summary": "Optimized summary with keywords...",
        "experience": [...],
        "skills": ["Python", "FastAPI", "REST API", "Database Design", ...]
    },
    "ats_score": 0.94,
    "missing_keywords": ["Cloud Architecture"],
    "recommendations": [
        "Add 'Cloud Architecture' if you have relevant experience",
        "Include specific tools: 'AWS', 'GCP' if used"
    ]
}
```

## Usage Examples

### Example 1: Basic Resume Generation

```python
from app.ai import AIPipeline
from app.database.models import User

# Setup
pipeline = AIPipeline(provider_name="openai")
user = User.get_by_id("user-123")
job_description = "Senior Python developer role..."

# Run pipeline
result = pipeline.generate_resume(
    user_career_data=user.get_career_data(),
    job_description=job_description,
    template_id="modern"
)

# Access result
resume = result.resume
print(f"Generated resume: {resume.title}")
print(f"Match score: {result.relevance_score}")
```

### Example 2: Custom Task Chain

```python
from app.ai.tasks import JobAnalyzer, RelevanceRanker, ContentGenerator

# Analyze job
analyzer = JobAnalyzer()
job_analysis = analyzer.run(job_description)

# Rank relevant experience
ranker = RelevanceRanker()
ranked = ranker.run(
    job_analysis=job_analysis,
    career_data=user.career_data,
    items=user.experience.all()
)

# Generate content for top experience
generator = ContentGenerator()
best_experience = ranked["ranked_items"][0]
content = generator.run(
    context={
        "item": best_experience,
        "job_analysis": job_analysis
    }
)
```

### Example 3: Testing with Mock Provider

```python
# For testing without API keys
pipeline = AIPipeline(provider_name="mock")

result = pipeline.generate_resume(
    user_career_data=test_data,
    job_description="test job",
    template_id="modern"
)

# Works instantly, returns mock data
assert result.resume is not None
```

### Example 4: Provider Fallback

```python
# Will try providers in order
pipeline = AIPipeline()

# Attempts:
# 1. Try configured provider (OPENAI_API_KEY exists)
# 2. Fall back to Anthropic if OpenAI fails and ANTHROPIC_API_KEY exists
# 3. Fall back to local Ollama if available
# 4. Use mock provider as last resort
```

## Performance & Rate Limiting

### Rate Limits

By default:
- 10 resume generations per minute (per user)
- 100 task executions per minute (per user)
- Can be configured via environment:

```python
AI_RATE_LIMIT_RESUMES=10
AI_RATE_LIMIT_TASKS=100
```

### Performance Metrics

Typical latencies:
- **Job Analysis**: 2-5 seconds
- **Relevance Ranking**: 3-7 seconds
- **Content Generation**: 5-10 seconds per item
- **ATS Optimization**: 2-4 seconds
- **Total Pipeline**: 15-30 seconds

For 10 experience items:
- Total time: ~120 seconds
- Should run asynchronously

### Optimization Strategies

**Parallel Processing**:
```python
import asyncio

# Run tasks in parallel
results = await asyncio.gather(
    generate_experience_content(),
    generate_education_content(),
    generate_skills_content(),
    return_exceptions=True
)
```

**Caching**:
```python
# Cache job analysis for 1 hour
cache_key = f"job_analysis:{hash(job_description)}"
cached = redis.get(cache_key)

if not cached:
    analysis = analyzer.run(job_description)
    redis.setex(cache_key, 3600, json.dumps(analysis))
else:
    analysis = json.loads(cached)
```

**Batching**:
```python
# Process multiple resumes in one call
results = pipeline.batch_generate(
    [
        (user1, job1),
        (user2, job2),
        (user3, job3),
    ]
)
```

## Customization

### Creating Custom Tasks

```python
from app.ai.base import AITask, AIResponse

class CustomTask(AITask):
    """Custom task for specific use case."""
    
    name = "custom_task"
    description = "Does custom processing"
    
    def run(self, **context) -> AIResponse:
        """Execute the task."""
        prompt = self._build_prompt(context)
        
        response = self.provider.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=500
        )
        
        return AIResponse(
            task_name=self.name,
            status="success",
            output={
                "result": response
            },
            metadata={
                "provider": self.provider.name,
                "model": self.provider.model
            }
        )
    
    def _build_prompt(self, context):
        """Build prompt for the custom task."""
        return f"Do something with {context}"
```

### Creating Custom Providers

```python
from app.ai.base import AIProvider

class CustomProvider(AIProvider):
    """Custom AI provider."""
    
    name = "custom"
    model = "custom-model"
    
    def generate(self, prompt, **kwargs):
        """Generate response."""
        # Call your API
        response = call_custom_api(prompt)
        return response
    
    def validate_config(self):
        """Validate required config."""
        assert os.getenv("CUSTOM_API_KEY")
```

Register it:
```python
from app.ai.providers.provider_factory import ProviderFactory

ProviderFactory.register("custom", CustomProvider)
```

## Monitoring & Debugging

### Enable Detailed Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("app.ai")
logger.setLevel(logging.DEBUG)
```

### View Pipeline Execution

```python
pipeline = AIPipeline(provider_name="openai", debug=True)

result = pipeline.generate_resume(...)

# Access execution details
for task_result in result.pipeline_execution:
    print(f"Task: {task_result.task_name}")
    print(f"Duration: {task_result.duration}s")
    print(f"Tokens used: {task_result.tokens}")
    print(f"Output: {task_result.output}")
```

### Cost Tracking

```python
# Pipeline tracks token usage
result = pipeline.generate_resume(...)

total_cost = result.tokens_used * (price_per_1k_tokens / 1000)

print(f"Tokens: {result.tokens_used}")
print(f"Estimated cost: ${total_cost:.2f}")
```

## Troubleshooting

### Issue: API Key Not Found

```
Error: OPENAI_API_KEY not found in environment
```

**Solution**:
```bash
export OPENAI_API_KEY=sk-...
# or in .env file
OPENAI_API_KEY=sk-...
```

### Issue: Rate Limit Exceeded

```
Error: Rate limited - try again in 60 seconds
```

**Solution**:
- Wait before retrying
- Implement exponential backoff
- Use batch processing for multiple items

### Issue: Poor Quality Output

**Solutions**:
- Adjust temperature (0.7 = balanced, 0.5 = deterministic, 0.9 = creative)
- Improve prompt engineering
- Try different AI provider
- Provide more context

### Issue: High Cost

**Solutions**:
- Use GPT-3.5 instead of GPT-4
- Cache results
- Use local LLM (Ollama)
- Batch process multiple items

## Best Practices

1. **Always use async**: AI tasks are I/O-bound, use async/await
2. **Cache results**: Job analysis rarely changes, cache for 1+ hours
3. **Handle failures gracefully**: Have fallbacks for AI failures
4. **Monitor costs**: Track token usage and costs
5. **Test with mock**: Use mock provider during development
6. **Provide context**: Better context = better output
7. **Iterate on prompts**: A/B test different prompts
8. **Use appropriate models**: GPT-3.5 for speed, GPT-4 for quality

## References

- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic API](https://docs.anthropic.com)
- [Ollama](https://ollama.ai)

---

**For questions or issues, open a GitHub issue or contact support.**
