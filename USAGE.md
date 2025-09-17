# Bonded CLI Tool Usage Examples

This document provides practical examples of using the Bonded CLI tool for content generation and quality control.

## Basic Usage

### Simple Content Processing
```bash
bonded -i input.csv -o output.csv
```

### With Custom QC Report Location
```bash
bonded -i articles.csv -o rewritten_articles.csv -q custom_qc_report.json
```

### Dry Run (Preview Mode)
```bash
bonded -i input.csv -o output.csv --dry-run
```

## Advanced Usage

### High-Volume Processing
```bash
bonded \
  --input large_dataset.csv \
  --output processed_content.csv \
  --qc-report detailed_qc.json \
  --max-workers 10 \
  --rate-limit 150
```

### Conservative Rate Limiting
```bash
bonded \
  --input sensitive_content.csv \
  --output careful_output.csv \
  --max-workers 2 \
  --rate-limit 30
```

## Input CSV Examples

### Minimal Input (Title Only)
```csv
title
"How to Start a Garden"
"Python Programming Basics"
"Digital Marketing Strategies"
```

### Complete Input with All Fields
```csv
title,description,keywords,target_audience,content
"SEO Best Practices","Complete guide to search engine optimization","SEO, search optimization, ranking","digital marketers","SEO is crucial for online visibility..."
"Remote Work Tips","Essential tips for working from home","remote work, productivity, work from home","remote workers","Working from home requires discipline..."
```

### Input with Mixed Completeness
```csv
title,description,keywords,target_audience,content
"AI in Healthcare","","artificial intelligence, healthcare, medical AI","healthcare professionals",""
"Sustainable Cooking","Eco-friendly cooking methods","sustainable cooking, green kitchen, eco recipes","","Start with choosing local ingredients..."
"Crypto Basics","Introduction to cryptocurrency","cryptocurrency, bitcoin, blockchain","beginners",""
```

## Expected Output Structure

The output CSV will include all original columns plus these generated fields:

```csv
title,description,keywords,target_audience,content,generated_outline,rewritten_content,word_count,qc_score
"SEO Best Practices","Complete guide to search engine optimization","SEO, search optimization, ranking","digital marketers","SEO is crucial...","# SEO Best Practices Outline...","# The Ultimate Guide to SEO Best Practices...","1247","87.5"
```

## Quality Control Report Structure

The QC report provides detailed analysis:

```json
{
  "summary": {
    "total_articles": 10,
    "passed_qc": 8,
    "average_score": 82.3,
    "average_word_count": 945,
    "common_issues": {
      "word_count": 2,
      "faq_section": 1
    }
  },
  "detailed_results": [
    {
      "title": "Article Title",
      "word_count": 1247,
      "overall_score": 87.5,
      "passed": true,
      "checks": {
        "word_count": {
          "passed": true,
          "score": 100,
          "details": "Content has 1247 words (minimum: 800)"
        }
      },
      "feedback": []
    }
  ],
  "recommendations": [
    "Address common word_count issues across 2 articles.",
    "Consider improving FAQ sections for better user engagement."
  ]
}
```

## Batch Processing Scripts

### Bash Script for Multiple Files
```bash
#!/bin/bash

# Process multiple CSV files in a directory
for file in data/*.csv; do
    output_name=$(basename "$file" .csv)_rewritten.csv
    qc_name=$(basename "$file" .csv)_qc.json
    
    echo "Processing $file..."
    bonded -i "$file" -o "output/$output_name" -q "reports/$qc_name"
done
```

### Python Script for Automated Processing
```python
import os
import subprocess
from pathlib import Path

def process_content_batch(input_dir, output_dir, reports_dir):
    """Process all CSV files in a directory"""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    reports_path = Path(reports_dir)
    
    # Create output directories
    output_path.mkdir(exist_ok=True)
    reports_path.mkdir(exist_ok=True)
    
    for csv_file in input_path.glob("*.csv"):
        output_file = output_path / f"{csv_file.stem}_rewritten.csv"
        qc_file = reports_path / f"{csv_file.stem}_qc.json"
        
        print(f"Processing {csv_file.name}...")
        
        subprocess.run([
            "bonded",
            "-i", str(csv_file),
            "-o", str(output_file),
            "-q", str(qc_file)
        ])

# Usage
process_content_batch("input_data", "processed_content", "qc_reports")
```

## Performance Optimization Tips

### 1. Optimal Worker Configuration
- For most use cases: `--max-workers 5`
- For high-rate-limit accounts: `--max-workers 10`
- For free tier API keys: `--max-workers 2`

### 2. Rate Limiting Guidelines
- OpenAI Plus: `--rate-limit 100`
- OpenAI Free Tier: `--rate-limit 20`
- OpenRouter Free: `--rate-limit 60`

### 3. Memory Considerations
For large CSV files (>1000 rows), consider processing in chunks:

```bash
# Split large file first
split -l 100 large_input.csv chunk_

# Process chunks
for chunk in chunk_*; do
    bonded -i "$chunk" -o "output_$chunk" --max-workers 3
done

# Combine results
cat output_chunk_* > final_output.csv
```

## Troubleshooting

### Common Issues and Solutions

1. **API Rate Limits Exceeded**
   ```bash
   # Reduce workers and rate limit
   bonded -i input.csv -o output.csv --max-workers 2 --rate-limit 30
   ```

2. **Out of Memory Errors**
   ```bash
   # Process smaller batches
   bonded -i input.csv -o output.csv --max-workers 1
   ```

3. **API Authentication Errors**
   ```bash
   # Check environment variables
   echo $OPENROUTER_API_KEY
   echo $OPENAI_API_KEY
   ```

### Environment Variables Setup

Create a `.env` file in your project directory:
```env
OPENROUTER_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
MAX_CONCURRENT_REQUESTS=5
REQUESTS_PER_MINUTE=100
MIN_WORD_COUNT=800
```

## Integration Examples

### Web Application Integration
```python
import asyncio
from bonded.api.openrouter import OpenRouterClient
from bonded.api.openai_client import OpenAIClient
from bonded.qc.validator import QualityController

async def process_single_article(title, description, keywords):
    """Process a single article in a web application"""
    
    # Create clients
    openrouter = OpenRouterClient()
    openai = OpenAIClient()
    qc = QualityController()
    
    # Generate content
    row = {
        'title': title,
        'description': description,
        'keywords': keywords,
        'target_audience': '',
        'content': ''
    }
    
    outline = await openrouter.generate_outline(row)
    content = await openai.rewrite_content(row, outline)
    qc_result = qc.validate_content(content, row)
    
    return {
        'outline': outline,
        'content': content,
        'qc_score': qc_result['overall_score'],
        'passed_qc': qc_result['passed']
    }
```

### API Service Integration
```python
from flask import Flask, request, jsonify
import asyncio

app = Flask(__name__)

@app.route('/generate-content', methods=['POST'])
def generate_content():
    data = request.get_json()
    
    result = asyncio.run(process_single_article(
        data['title'],
        data.get('description', ''),
        data.get('keywords', '')
    ))
    
    return jsonify(result)
```