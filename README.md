# Bonded - Content Generation & Quality Control CLI

A powerful CLI tool that reads CSV files with titles and metadata, generates section outlines via OpenRouter free models, expands and fully rewrites content using GPT-5, and enforces enterprise-quality quality control.

## Features

- 📝 **CSV Processing**: Read titles and metadata from CSV files
- 🤖 **AI-Powered Outlines**: Generate comprehensive content outlines using OpenRouter free models
- ✨ **Content Rewriting**: Expand and fully rewrite content using GPT-5 (GPT-4)
- 🔍 **Enterprise QC**: Comprehensive quality control with 800+ word requirement, SEO checks, E-E-A-T validation, and FAQ requirements
- ⚡ **Parallel Processing**: Process multiple articles concurrently with intelligent rate limiting
- 📊 **Detailed Reporting**: Generate comprehensive QC reports with actionable feedback

## Quality Control Checks

- **Word Count**: Ensures minimum 800 words per article
- **SEO Optimization**: Keyword integration, title optimization, linking opportunities
- **E-E-A-T Signals**: Experience, Expertise, Authoritativeness, Trustworthiness indicators
- **Content Structure**: Proper headings, lists, paragraphs, conclusions
- **Readability**: Sentence length, transition words, active voice
- **FAQ Section**: Requires 3-5 relevant questions and answers
- **Keyword Integration**: Natural keyword placement without stuffing
- **Grammar Quality**: Basic grammar and style validation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/poolboy17/bonded.git
cd bonded
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the package:
```bash
pip install -e .
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

Create a `.env` file with the following variables:

```env
# OpenRouter API Configuration (for free outline generation)
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# OpenAI API Configuration (for GPT-5/GPT-4 content rewriting)
OPENAI_API_KEY=your_openai_api_key_here

# Rate limiting settings
MAX_CONCURRENT_REQUESTS=5
REQUESTS_PER_MINUTE=100

# Quality Control Settings
MIN_WORD_COUNT=800
```

## Usage

### Basic Usage

```bash
bonded -i input.csv -o output.csv
```

### Advanced Usage

```bash
bonded \
  --input examples/sample_input.csv \
  --output rewritten_content.csv \
  --qc-report qc_report.json \
  --max-workers 3 \
  --rate-limit 60
```

### Dry Run

Preview what would be processed without making API calls:

```bash
bonded -i input.csv -o output.csv --dry-run
```

## CSV Format

### Input CSV Structure

The input CSV should have the following columns:

- `title` (required): Article title
- `description` (optional): Brief description
- `keywords` (optional): Comma-separated keywords
- `target_audience` (optional): Target audience description
- `content` (optional): Original content to be rewritten

### Output CSV Structure

The output CSV includes all original columns plus:

- `generated_outline`: AI-generated content outline
- `rewritten_content`: Fully rewritten content
- `word_count`: Final word count
- `qc_score`: Overall quality control score

## Example

See `examples/sample_input.csv` for a sample input file:

```csv
title,description,keywords,target_audience,content
"How to Build a Successful Blog","A comprehensive guide to creating and growing a profitable blog","blogging, content marketing, SEO","aspiring bloggers","..."
```

## Quality Control Report

The QC report provides detailed analysis including:

- Overall statistics (pass rate, average scores, word counts)
- Individual article results with specific feedback
- Common issues across all content
- Actionable recommendations for improvement

## API Integration

### OpenRouter Integration
- Uses free models for cost-effective outline generation
- Configurable model selection
- Automatic retry logic with exponential backoff

### OpenAI Integration
- GPT-4 for high-quality content rewriting
- Intelligent content expansion to meet word count requirements
- Context-aware content enhancement

## Development

### Project Structure

```
bonded/
├── bonded/
│   ├── __init__.py
│   ├── cli.py              # Main CLI interface
│   ├── api/
│   │   ├── openrouter.py   # OpenRouter API client
│   │   └── openai_client.py # OpenAI API client
│   ├── qc/
│   │   └── validator.py    # Quality control system
│   └── utils/
│       ├── csv_handler.py  # CSV processing utilities
│       └── rate_limiter.py # Rate limiting implementation
├── examples/
│   └── sample_input.csv    # Example input file
├── requirements.txt
├── setup.py
└── README.md
```

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests (when available)
python -m pytest
```

## Rate Limiting

The tool includes intelligent rate limiting to respect API quotas:

- Configurable requests per minute
- Maximum concurrent request limiting
- Automatic backoff and retry logic
- Real-time rate limit monitoring

## Error Handling

- Comprehensive error logging
- Graceful handling of API failures
- Partial result preservation
- Detailed error reporting in QC reports

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the examples directory for usage samples
- Review the QC report for content improvement suggestions