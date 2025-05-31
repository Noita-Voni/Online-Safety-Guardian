# Online Safety Guardian

## Overview
Online Safety Guardian is a tool for detecting potentially suspicious messages in text conversations, designed to help identify patterns associated with grooming and other concerning behaviors. It uses regex pattern matching and sentiment analysis to flag suspicious messages and categorize them by severity.

## Features
- Analysis of chat messages via CSV files
- Detection of suspicious patterns using regular expressions
- Sentiment analysis integration with NLTK VADER
- Severity classification (Safe, Suspicious, High Risk)
- Web interface with interactive data visualizations:
  - Risk level distribution chart
  - Top detected suspicious patterns
  - Sentiment score distribution
  - Match count analysis
- Console application for command-line analysis
- CSV export of flagged messages

## How Message Classification Works

Messages are analyzed and classified into three risk categories:

### High Risk
- Messages containing 2 or more suspicious patterns
- Example: "Let's meet alone, don't tell your parents"
  (Has "meet alone" and "don't tell" patterns)

### Suspicious
- Messages that either:
  - Contain exactly 1 suspicious pattern
  - OR have a very negative tone (sentiment score ≤ -0.5)
- Example: "You should keep this a secret" or "You will regret it if you don't listen"

### Safe
- Messages with no suspicious patterns and without a very negative tone
- These messages are not flagged in the results

The system flags both "High Risk" and "Suspicious" messages for review, while "Safe" messages are not flagged.

## Technical Details

### Components
1. **Guardian Module** (guardian.py)
   - Core analysis engine
   - Performs regex pattern matching and sentiment analysis 
   - Outputs results to console and saves to CSV

2. **Web Application** (app.py)
   - Flask-based web interface
   - File upload capability
   - Displays analysis results in HTML tables

3. **Frontend Template** (templates/index.html)
   - Responsive Bootstrap-based UI
   - File upload form
   - Results presentation

### Technology Stack
- **Python 3.x**: Core programming language
- **pandas**: Data manipulation and analysis
- **NLTK**: Natural Language Processing for sentiment analysis
- **Flask**: Web application framework
- **Bootstrap**: Frontend styling
- **Regular Expressions**: Pattern matching
- **Colorama**: Console text formatting (CLI only)

## How to Use

### Command Line Usage
1. Ensure you have Python and required packages installed:
   ```
   pip install pandas nltk colorama
   ```

2. Prepare a CSV file with chat messages in the following format:
   ```
   id,message
   1,"Your message text here"
   2,"Another message text"
   ```

3. Run the `guardian.py` script:
   ```
   python guardian.py
   ```
   - By default, it will analyze `sample_chats.csv`
   - Results will display in the console and save to `flagged_messages.csv`

### Web Interface Usage
1. Install additional required package:
   ```
   pip install flask
   ```

2. Run the web application:
   ```
   python app.py
   ```

3. Open your browser and navigate to `http://127.0.0.1:5000`

4. Either:
   - Use the default `sample_chats.csv` by clicking "Run Analysis"
   - Upload your own CSV file using the form, then click "Run Analysis"

5. View the analysis results displayed in the table

### Using Your Own Dataset
To analyze your own chat data:

1. Create a CSV file with the following format:
   ```csv
   id,message
   1,"First message text"
   2,"Second message text"
   ...
   ```

2. The file must contain at minimum:
   - A header row with "id" and "message" columns
   - Each message on a separate row
   - Messages enclosed in quotes if they contain commas

3. Either:
   - Replace the existing `sample_chats.csv` file with your CSV
   - Upload your file through the web interface
   - Specify a custom filename in the code

## Customization

### Modifying Detection Patterns
The suspicious patterns are defined in the `suspicious_patterns` list in both `guardian.py` and `app.py`. You can:
- Add new patterns to detect
- Modify existing patterns
- Remove patterns that aren't relevant to your use case

### Adjusting Severity Thresholds
In the `get_severity_level` function, you can modify:
- The match count thresholds (currently ≥2 for "High Risk", 1 for "Suspicious")
- The sentiment score threshold (currently ≤-0.5 for "Suspicious")
- The categorization logic

## Screenshots

### Web Interface
![Web Interface Overview](images/web-interface "The main dashboard")

### Analysis Results
![Sample Analysis Results](images/analysis-results1.png "Example of flagged messages")
![Sample Analysis Results](images/analysis-results2.png "Example of flagged messages")
![Sample Analysis Results](images/analysis-results3.png "Example of flagged messages")
![Sample Analysis Results](images/analysis-results4.png "Example of flagged messages")

## Demo

Watch how the Online Safety Guardian analyzes suspicious patterns:

[![Online Safety Guardian Demo](images/demovideo-sampledata.mp4 "Demo Video")]

## Contribute

Looking to collaborate and improve the Online Safety Guardian? This project has many opportunities for enhancement! 

Some areas for potential improvement:
- Adding machine learning classification
- Creating data visualizations for the analysis results
- Implementing real-time message monitoring
- Supporting additional languages
- Creating a more comprehensive user interface

Feel free to fork the repository and submit pull requests. All contributions are welcome!

## License
This project is for educational purposes to demonstrate text analysis techniques for online safety.
