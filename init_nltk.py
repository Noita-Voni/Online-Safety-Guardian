#!/usr/bin/env python3
"""
Initialize NLTK data for deployment
"""
import nltk
import os

def download_nltk_data():
    """Download required NLTK data"""
    try:
        # Create NLTK data directory if it doesn't exist
        nltk_data_dir = os.path.expanduser('~/nltk_data')
        if not os.path.exists(nltk_data_dir):
            os.makedirs(nltk_data_dir)
        
        # Download required NLTK data
        nltk.download('vader_lexicon', quiet=True)
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        
        print("NLTK data downloaded successfully")
        return True
    except Exception as e:
        print(f"Warning: Could not download NLTK data: {e}")
        return False

if __name__ == "__main__":
    download_nltk_data()
