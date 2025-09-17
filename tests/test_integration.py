#!/usr/bin/env python3
"""
Integration test for the complete Bonded CLI tool
"""

import sys
import tempfile
import json
from pathlib import Path

# Add the bonded package to path
sys.path.insert(0, '/home/runner/work/bonded/bonded')

from bonded.utils.csv_handler import CSVHandler
from bonded.qc.validator import QualityController
from bonded.utils.rate_limiter import RateLimiter

def test_csv_handler():
    """Test CSV handling functionality"""
    print("Testing CSV Handler...")
    
    csv_handler = CSVHandler()
    
    # Test loading the sample CSV
    sample_path = Path('/home/runner/work/bonded/bonded/examples/sample_input.csv')
    df = csv_handler.load_csv(sample_path)
    
    assert len(df) == 3, f"Expected 3 rows, got {len(df)}"
    assert 'title' in df.columns, "Missing required 'title' column"
    
    # Test validation
    validation = csv_handler.validate_csv_structure(sample_path)
    assert validation['valid'], f"CSV validation failed: {validation}"
    
    print("✓ CSV Handler tests passed")
    return True

def test_rate_limiter():
    """Test rate limiting functionality"""
    print("Testing Rate Limiter...")
    
    limiter = RateLimiter(requests_per_minute=60, max_concurrent=2)
    stats = limiter.get_stats()
    
    assert stats['requests_per_minute_limit'] == 60
    assert stats['max_concurrent'] == 2
    assert stats['available_slots'] == 2
    
    print("✓ Rate Limiter tests passed")
    return True

def test_quality_controller():
    """Test quality control system"""
    print("Testing Quality Controller...")
    
    qc = QualityController()
    
    # Test with minimal content
    minimal_content = "This is a test article with minimal content."
    metadata = {'title': 'Test Article', 'keywords': 'test, article'}
    
    result = qc.validate_content(minimal_content, metadata)
    assert 'overall_score' in result
    assert 'checks' in result
    assert len(result['checks']) == 8  # Should have 8 quality checks
    
    # Test QC report generation
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        report_path = Path(f.name)
    
    qc.generate_report([result], report_path)
    
    # Verify report was created and is valid JSON
    assert report_path.exists()
    with open(report_path) as f:
        report_data = json.load(f)
    
    assert 'summary' in report_data
    assert 'detailed_results' in report_data
    
    # Cleanup
    report_path.unlink()
    
    print("✓ Quality Controller tests passed")
    return True

def test_cli_import():
    """Test that CLI module can be imported"""
    print("Testing CLI Import...")
    
    try:
        from bonded.cli import main
        print("✓ CLI import tests passed")
        return True
    except ImportError as e:
        print(f"✗ CLI import failed: {e}")
        return False

def test_api_client_imports():
    """Test that API client modules can be imported"""
    print("Testing API Client Imports...")
    
    try:
        from bonded.api.openrouter import OpenRouterClient
        from bonded.api.openai_client import OpenAIClient
        
        # Test instantiation (should work even without API keys for basic import test)
        print("✓ API Client import tests passed")
        return True
    except Exception as e:
        print(f"✗ API Client import failed: {e}")
        return False

def run_integration_tests():
    """Run all integration tests"""
    print("Running Bonded CLI Integration Tests")
    print("=" * 50)
    
    tests = [
        test_csv_handler,
        test_rate_limiter,
        test_quality_controller,
        test_cli_import,
        test_api_client_imports
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Integration Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All integration tests passed!")
        return True
    else:
        print("❌ Some integration tests failed")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)