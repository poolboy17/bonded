"""
CSV Handler for reading and writing content data
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any


class CSVHandler:
    """Handle CSV file operations for content processing"""
    
    def __init__(self):
        self.required_columns = ['title']
        self.optional_columns = [
            'description', 'keywords', 'target_audience', 'content'
        ]
    
    def load_csv(self, file_path: Path) -> pd.DataFrame:
        """
        Load and validate CSV file
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Validated DataFrame
        """
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            # Try with different encoding
            df = pd.read_csv(file_path, encoding='latin-1')
        
        # Validate required columns
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Add missing optional columns with empty values
        for col in self.optional_columns:
            if col not in df.columns:
                df[col] = ''
        
        # Clean data
        df = self._clean_dataframe(df)
        
        return df
    
    def save_csv(self, df: pd.DataFrame, file_path: Path):
        """
        Save DataFrame to CSV file
        
        Args:
            df: DataFrame to save
            file_path: Output file path
        """
        # Ensure output directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save with UTF-8 encoding
        df.to_csv(file_path, index=False, encoding='utf-8')
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize DataFrame data"""
        # Fill NaN values with empty strings
        df = df.fillna('')
        
        # Strip whitespace from string columns
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
        
        # Remove completely empty rows
        df = df[df['title'].str.len() > 0]
        
        return df
    
    def validate_csv_structure(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate CSV structure without loading full data
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Validation results
        """
        try:
            # Read just the header
            sample_df = pd.read_csv(file_path, nrows=0)
            
            validation = {
                'valid': True,
                'columns': list(sample_df.columns),
                'missing_required': [],
                'extra_columns': [],
                'warnings': []
            }
            
            # Check required columns
            missing_required = [col for col in self.required_columns if col not in sample_df.columns]
            validation['missing_required'] = missing_required
            
            if missing_required:
                validation['valid'] = False
            
            # Check for unexpected columns
            expected_columns = self.required_columns + self.optional_columns
            extra_columns = [col for col in sample_df.columns if col not in expected_columns]
            validation['extra_columns'] = extra_columns
            
            if extra_columns:
                validation['warnings'].append(f"Unexpected columns found: {extra_columns}")
            
            return validation
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'columns': [],
                'missing_required': [],
                'extra_columns': [],
                'warnings': []
            }