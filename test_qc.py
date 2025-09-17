#!/usr/bin/env python3
"""
Test script to verify the Quality Control system
"""

import sys
import os

# Add the bonded package to path
sys.path.insert(0, '/home/runner/work/bonded/bonded')

from bonded.qc.validator import QualityController

def test_quality_control():
    """Test the quality control system with sample content"""
    
    qc = QualityController()
    
    # Sample content for testing
    sample_content = """
# How to Build a Successful Blog: The Complete Guide

Building a successful blog requires careful planning, consistent effort, and strategic implementation. According to research from industry experts, the most successful bloggers combine technical expertise with authentic storytelling and audience engagement. Our experience working with hundreds of bloggers over the years has shown that certain proven strategies consistently lead to profitable, sustainable blog growth.

## Understanding Your Niche and Audience

The foundation of any successful blog lies in choosing the right niche and understanding your target audience. Professional bloggers recommend starting with a topic you're genuinely passionate about, as this authentic enthusiasm will shine through in your content. Research shows that blogs focused on specific, well-defined niches tend to perform better than those attempting to cover broad, general topics.

Your target audience should be clearly defined with specific demographics, interests, and pain points. Create detailed reader personas based on data and research rather than assumptions. This strategic approach ensures your content consistently provides value to the right people.

## Content Strategy and Planning

Developing a comprehensive content strategy is essential for long-term success. Expert bloggers typically plan content several months in advance, ensuring consistent publishing schedules and strategic topic coverage. Best practices include:

- Conducting thorough keyword research using reliable tools
- Creating editorial calendars with seasonal considerations
- Balancing evergreen content with trending topics
- Implementing proper SEO optimization techniques

## Technical Implementation and SEO

The technical foundation of your blog significantly impacts its success potential. Professional web developers recommend choosing reliable hosting, implementing responsive design, and optimizing for speed. SEO experts consistently emphasize the importance of proper on-page optimization, including title tags, meta descriptions, and header structure.

## Monetization Strategies

Successful bloggers employ multiple revenue streams to maximize their earning potential. Proven monetization methods include affiliate marketing, sponsored content, digital product sales, and service offerings. However, building trust with your audience must always come before monetization efforts.

## Frequently Asked Questions

**Q: How long does it take to build a successful blog?**
A: Building a profitable blog typically takes 6-12 months of consistent effort, though this varies based on niche, content quality, and marketing strategy.

**Q: What's the most important factor for blog success?**
A: Consistent, high-quality content that genuinely helps your target audience is the most critical success factor.

**Q: How often should I publish new content?**
A: Quality is more important than quantity, but most successful blogs publish at least once per week to maintain audience engagement.

**Q: Do I need technical skills to start a blog?**
A: While technical skills are helpful, modern blogging platforms make it possible to start without coding knowledge. However, learning basic SEO and analytics is beneficial for growth.

**Q: How do I know if my blog is successful?**
A: Success metrics include growing organic traffic, engaged readership, email subscribers, and eventually revenue generation from your content efforts.
"""
    
    # Sample metadata
    metadata = {
        'title': 'How to Build a Successful Blog',
        'description': 'A comprehensive guide to creating and growing a profitable blog',
        'keywords': 'blogging, content marketing, SEO, monetization',
        'target_audience': 'aspiring bloggers and content creators'
    }
    
    # Run quality control
    print("Running Quality Control Test...")
    print("=" * 50)
    
    result = qc.validate_content(sample_content, metadata)
    
    # Display results
    print(f"Title: {result['title']}")
    print(f"Word Count: {result['word_count']}")
    print(f"Overall Score: {result['overall_score']:.1f}%")
    print(f"Passed QC: {'✓' if result['passed'] else '✗'}")
    print()
    
    print("Individual Check Results:")
    print("-" * 30)
    for check_name, check_result in result['checks'].items():
        status = "✓" if check_result['passed'] else "✗"
        print(f"{status} {check_name}: {check_result['score']:.1f}% - {check_result['details']}")
    
    if result['feedback']:
        print("\nFeedback:")
        print("-" * 10)
        for feedback in result['feedback']:
            print(f"  {feedback}")
    
    return result['passed']

if __name__ == "__main__":
    success = test_quality_control()
    print(f"\nQuality Control Test: {'PASSED' if success else 'FAILED'}")