"""
Quality Control Validator for enterprise-grade content
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
import validators


class QualityController:
    """Enterprise-quality content validator with comprehensive checks"""
    
    def __init__(self, min_word_count: int = 800):
        self.min_word_count = min_word_count
        self.seo_keywords = [
            'best practices', 'how to', 'guide', 'tips', 'benefits', 
            'advantages', 'comprehensive', 'complete', 'ultimate', 'expert'
        ]
        self.eeat_indicators = [
            'research', 'study', 'expert', 'experience', 'professional',
            'certified', 'proven', 'reliable', 'trusted', 'authority'
        ]
    
    def validate_content(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive content validation
        
        Args:
            content: The content to validate
            metadata: Original row metadata
            
        Returns:
            Validation results with scores and feedback
        """
        results = {
            'title': metadata.get('title', ''),
            'word_count': self._count_words(content),
            'checks': {},
            'overall_score': 0,
            'passed': False,
            'feedback': []
        }
        
        # Run all validation checks
        results['checks']['word_count'] = self._check_word_count(content)
        results['checks']['seo_optimization'] = self._check_seo_optimization(content, metadata)
        results['checks']['eeat_signals'] = self._check_eeat_signals(content)
        results['checks']['structure'] = self._check_content_structure(content)
        results['checks']['readability'] = self._check_readability(content)
        results['checks']['faq_section'] = self._check_faq_section(content)
        results['checks']['keyword_integration'] = self._check_keyword_integration(content, metadata)
        results['checks']['grammar_quality'] = self._check_grammar_quality(content)
        
        # Calculate overall score
        scores = [check['score'] for check in results['checks'].values()]
        results['overall_score'] = sum(scores) / len(scores) if scores else 0
        results['passed'] = results['overall_score'] >= 70  # 70% threshold
        
        # Generate feedback
        results['feedback'] = self._generate_feedback(results['checks'])
        
        return results
    
    def _count_words(self, content: str) -> int:
        """Count words in content"""
        return len(content.split())
    
    def _check_word_count(self, content: str) -> Dict[str, Any]:
        """Check if content meets minimum word count"""
        word_count = self._count_words(content)
        passed = word_count >= self.min_word_count
        
        return {
            'name': 'Word Count',
            'passed': passed,
            'score': 100 if passed else max(0, (word_count / self.min_word_count) * 100),
            'details': f"Content has {word_count} words (minimum: {self.min_word_count})",
            'word_count': word_count
        }
    
    def _check_seo_optimization(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Check SEO optimization elements"""
        content_lower = content.lower()
        score = 0
        details = []
        
        # Check for SEO-friendly keywords
        seo_keyword_count = sum(1 for keyword in self.seo_keywords if keyword in content_lower)
        if seo_keyword_count >= 3:
            score += 30
            details.append(f"Good SEO keyword usage ({seo_keyword_count} found)")
        else:
            details.append(f"Limited SEO keywords ({seo_keyword_count} found, recommend 3+)")
        
        # Check title optimization
        title = metadata.get('title', '').lower()
        if title and title in content_lower:
            score += 25
            details.append("Title appears in content")
        else:
            details.append("Title should appear in content")
        
        # Check for meta description keywords
        keywords = metadata.get('keywords', '').lower()
        if keywords:
            keyword_list = [k.strip() for k in keywords.split(',')]
            found_keywords = sum(1 for kw in keyword_list if kw in content_lower)
            if found_keywords >= len(keyword_list) * 0.7:  # 70% of keywords found
                score += 25
                details.append(f"Good keyword integration ({found_keywords}/{len(keyword_list)})")
            else:
                details.append(f"Improve keyword integration ({found_keywords}/{len(keyword_list)})")
        
        # Check for internal/external linking opportunities
        if 'http' in content or 'www.' in content:
            score += 20
            details.append("Contains links for authority")
        else:
            details.append("Consider adding relevant links")
        
        return {
            'name': 'SEO Optimization',
            'passed': score >= 70,
            'score': score,
            'details': '; '.join(details)
        }
    
    def _check_eeat_signals(self, content: str) -> Dict[str, Any]:
        """Check for E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) signals"""
        content_lower = content.lower()
        score = 0
        details = []
        
        # Check for experience indicators
        experience_indicators = ['experience', 'worked', 'years', 'practiced', 'implemented']
        experience_count = sum(1 for indicator in experience_indicators if indicator in content_lower)
        if experience_count >= 2:
            score += 25
            details.append("Shows personal/professional experience")
        
        # Check for expertise indicators
        expertise_count = sum(1 for indicator in self.eeat_indicators if indicator in content_lower)
        if expertise_count >= 3:
            score += 25
            details.append(f"Demonstrates expertise ({expertise_count} indicators)")
        
        # Check for authoritative language
        auth_phrases = ['according to', 'research shows', 'studies indicate', 'data reveals']
        auth_count = sum(1 for phrase in auth_phrases if phrase in content_lower)
        if auth_count >= 1:
            score += 25
            details.append("Uses authoritative references")
        
        # Check for trustworthiness indicators
        trust_phrases = ['honest', 'transparent', 'accurate', 'reliable', 'verified']
        trust_count = sum(1 for phrase in trust_phrases if phrase in content_lower)
        if trust_count >= 1:
            score += 25
            details.append("Includes trustworthiness signals")
        
        if not details:
            details.append("Limited E-E-A-T signals found")
        
        return {
            'name': 'E-E-A-T Signals',
            'passed': score >= 70,
            'score': score,
            'details': '; '.join(details)
        }
    
    def _check_content_structure(self, content: str) -> Dict[str, Any]:
        """Check content structure and formatting"""
        score = 0
        details = []
        
        # Check for headings
        heading_patterns = [r'^#{1,6}\s+', r'<h[1-6]>']
        has_headings = any(re.search(pattern, content, re.MULTILINE) for pattern in heading_patterns)
        if has_headings:
            score += 30
            details.append("Proper heading structure")
        else:
            details.append("Missing heading structure")
        
        # Check for lists
        list_patterns = [r'^\s*[-*+]\s+', r'^\s*\d+\.\s+', r'<ul>', r'<ol>']
        has_lists = any(re.search(pattern, content, re.MULTILINE) for pattern in list_patterns)
        if has_lists:
            score += 25
            details.append("Uses lists for readability")
        else:
            details.append("Consider adding lists for better structure")
        
        # Check paragraph length
        paragraphs = content.split('\n\n')
        avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        if 50 <= avg_paragraph_length <= 150:  # Optimal paragraph length
            score += 25
            details.append("Good paragraph length")
        else:
            details.append("Consider optimizing paragraph length")
        
        # Check for conclusion
        if any(word in content.lower() for word in ['conclusion', 'summary', 'takeaway', 'final']):
            score += 20
            details.append("Includes conclusion")
        else:
            details.append("Consider adding a clear conclusion")
        
        return {
            'name': 'Content Structure',
            'passed': score >= 70,
            'score': score,
            'details': '; '.join(details)
        }
    
    def _check_readability(self, content: str) -> Dict[str, Any]:
        """Check content readability"""
        score = 0
        details = []
        
        # Simple readability checks
        sentences = re.split(r'[.!?]+', content)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        if 10 <= avg_sentence_length <= 20:  # Optimal sentence length
            score += 40
            details.append("Good sentence length")
        else:
            details.append("Consider varying sentence length")
        
        # Check for transition words
        transitions = ['however', 'therefore', 'furthermore', 'additionally', 'consequently', 'meanwhile']
        transition_count = sum(1 for word in transitions if word in content.lower())
        if transition_count >= 2:
            score += 30
            details.append("Uses transition words")
        else:
            details.append("Consider adding transition words")
        
        # Check for active voice (simple heuristic)
        passive_indicators = ['was', 'were', 'been', 'being']
        passive_count = sum(content.lower().count(word) for word in passive_indicators)
        total_words = len(content.split())
        passive_ratio = passive_count / total_words if total_words > 0 else 0
        
        if passive_ratio < 0.1:  # Less than 10% passive voice
            score += 30
            details.append("Predominantly active voice")
        else:
            details.append("Consider reducing passive voice")
        
        return {
            'name': 'Readability',
            'passed': score >= 70,
            'score': score,
            'details': '; '.join(details)
        }
    
    def _check_faq_section(self, content: str) -> Dict[str, Any]:
        """Check for FAQ section"""
        content_lower = content.lower()
        
        # Look for FAQ indicators
        faq_indicators = ['faq', 'frequently asked', 'common questions', 'q:', 'question:']
        has_faq = any(indicator in content_lower for indicator in faq_indicators)
        
        if has_faq:
            # Count question-answer pairs
            question_count = len(re.findall(r'\b(?:q:|question:|what|how|why|when|where)\b.*\?', content, re.IGNORECASE))
            
            if question_count >= 3:
                score = 100
                details = f"Complete FAQ section with {question_count} questions"
            else:
                score = 70
                details = f"FAQ section present but could be expanded ({question_count} questions)"
        else:
            score = 0
            details = "Missing FAQ section"
        
        return {
            'name': 'FAQ Section',
            'passed': score >= 70,
            'score': score,
            'details': details
        }
    
    def _check_keyword_integration(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Check natural keyword integration"""
        keywords = metadata.get('keywords', '')
        if not keywords:
            return {
                'name': 'Keyword Integration',
                'passed': True,
                'score': 100,
                'details': 'No keywords specified'
            }
        
        content_lower = content.lower()
        keyword_list = [k.strip().lower() for k in keywords.split(',')]
        
        found_keywords = []
        keyword_density = {}
        
        for keyword in keyword_list:
            count = content_lower.count(keyword)
            if count > 0:
                found_keywords.append(keyword)
                keyword_density[keyword] = count
        
        # Calculate score based on keyword coverage and density
        coverage_score = (len(found_keywords) / len(keyword_list)) * 70 if keyword_list else 100
        
        # Check for keyword stuffing (more than 3% density for any keyword)
        total_words = len(content.split())
        stuffing_penalty = 0
        for keyword, count in keyword_density.items():
            density = count / total_words if total_words > 0 else 0
            if density > 0.03:  # More than 3% is likely stuffing
                stuffing_penalty += 20
        
        final_score = max(0, coverage_score + 30 - stuffing_penalty)
        
        return {
            'name': 'Keyword Integration',
            'passed': final_score >= 70,
            'score': final_score,
            'details': f"Found {len(found_keywords)}/{len(keyword_list)} keywords naturally integrated"
        }
    
    def _check_grammar_quality(self, content: str) -> Dict[str, Any]:
        """Basic grammar and style checks"""
        score = 0
        issues = []
        
        # Check for common grammar issues
        if not re.search(r'\s{2,}', content):  # No excessive spacing
            score += 25
        else:
            issues.append("excessive spacing")
        
        # Check for proper capitalization
        sentences = re.split(r'[.!?]+', content)
        properly_capitalized = sum(1 for s in sentences if s.strip() and s.strip()[0].isupper())
        if properly_capitalized / len(sentences) > 0.9:  # 90% of sentences properly capitalized
            score += 25
        else:
            issues.append("capitalization issues")
        
        # Check for consistent punctuation
        if not re.search(r'[.!?]{2,}', content):  # No repeated punctuation
            score += 25
        else:
            issues.append("punctuation inconsistencies")
        
        # Check for proper paragraph breaks
        if '\n\n' in content or len(content.split('\n')) > 1:
            score += 25
        else:
            issues.append("poor paragraph structure")
        
        details = "Good grammar quality" if score >= 75 else f"Issues: {', '.join(issues)}"
        
        return {
            'name': 'Grammar Quality',
            'passed': score >= 70,
            'score': score,
            'details': details
        }
    
    def _generate_feedback(self, checks: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate actionable feedback based on check results"""
        feedback = []
        
        for check_name, check_result in checks.items():
            if not check_result['passed']:
                feedback.append(f"⚠️ {check_name}: {check_result['details']}")
            elif check_result['score'] < 90:
                feedback.append(f"💡 {check_name}: {check_result['details']}")
        
        return feedback
    
    def generate_report(self, qc_results: List[Dict[str, Any]], output_path: Path):
        """Generate comprehensive QC report"""
        summary = {
            'total_articles': len(qc_results),
            'passed_qc': sum(1 for result in qc_results if result['passed']),
            'average_score': sum(result['overall_score'] for result in qc_results) / len(qc_results) if qc_results else 0,
            'average_word_count': sum(result['word_count'] for result in qc_results) / len(qc_results) if qc_results else 0,
            'common_issues': self._analyze_common_issues(qc_results)
        }
        
        report = {
            'summary': summary,
            'detailed_results': qc_results,
            'recommendations': self._generate_recommendations(summary)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
    
    def _analyze_common_issues(self, qc_results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze common quality issues across all content"""
        issues = {}
        
        for result in qc_results:
            for check_name, check_result in result['checks'].items():
                if not check_result['passed']:
                    issues[check_name] = issues.get(check_name, 0) + 1
        
        return dict(sorted(issues.items(), key=lambda x: x[1], reverse=True))
    
    def _generate_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on overall results"""
        recommendations = []
        
        if summary['average_score'] < 80:
            recommendations.append("Overall quality could be improved. Focus on failing check categories.")
        
        if summary['average_word_count'] < self.min_word_count:
            recommendations.append(f"Content length is below target. Aim for {self.min_word_count}+ words per article.")
        
        for issue, count in summary['common_issues'].items():
            if count > len(qc_results) * 0.3:  # More than 30% of articles have this issue
                recommendations.append(f"Address common {issue} issues across {count} articles.")
        
        return recommendations