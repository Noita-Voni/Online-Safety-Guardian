from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import re
from colorama import Fore  # Only for console output, not used in web
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import os
import json
from collections import Counter

# Initialize NLTK and download the lexicon if necessary
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# Initialize Flask app
app = Flask(__name__)

# Define suspicious regex patterns (same as before)
suspicious_patterns = [
    r"don'?t\s+tell",                   
    r"keep.*between\s+us",                    
    r"only\s+between\s+us",                   
    r"(secret|private|special)\s+(chat|talk)?", 
    r"(just|only)\s+you\s+and\s+me",            
    r"don't\s+share\s+this\s+with\s+anyone",    
    r"it's\s+our\s+little\s+secret",            
    r"you're\s+so\s+(mature|grown\s+up)",       
    r"you're\s+so\s+beautiful\s+for\s+your\s+age", 
    r"(let'?s|lets)\s+meet.*alone",             
    r"i\s+want\s+to\s+meet\s+you\s+in\s+person",  
    r"are\s+your\s+parents\s+(home|around)",     
    r"let'?s\s+hang\s+out\s+just\s+us",        
    r"tell\s+me\s+more\s+about\s+your\s+family",
    r"send\s+me\s+a\s+pic",                   
    r"i\s+can\s+keep\s+secrets",           
    r"show\s+me\s+what\s+you're\s+wearing",   
    r"you\s+owe\s+me\s+(something|a\s+favor)",  
    r"just\s+trust\s+me",                        
    r"you\s+don't\s+have\s+to\s+tell\s+anyone",   
    r"it\s+won'?t\s+hurt",                       
    r"if\s+you\s+tell\s+anyone\s+we\s+can'?t\s+talk\s+anymore",
    r"i\s+won'?t\s+tell\s+anyone\s+promise",       
    r"this\s+is\s+our\s+secret\s+to\s+keep",       
    r"secret", 
    r"don't tell anyone",
    r"just between us", 
    r"you're so mature",
    r"send.*(pic|photo|picture)", 
    r"what.*wearing", 
    r"come over", 
    r"alone.*(meet|see)",
    r"i won.t tell", 
    r"you can trust me", 
    r"age.*doesn't matter",
    r"it.*our.*secret", 
    r"if.*tell.*anyone", 
    r"i.*like.*you.*(so much|a lot)",
    r"nobody will know", 
    r"this.*is.*between.*us", 
    r"promise.*won't.*tell",
    r"(i|we).*won.t.*get.*caught", 
    r"(touch|touching)", 
    r"(kiss|kissing)",
    r"(undress|take.*clothes.*off|naked|nude)"
]

# Function to get severity level using pattern matches and sentiment analysis
def get_severity_level(message):
    match_count = 0
    for pattern in suspicious_patterns:
        if re.search(pattern, message, re.IGNORECASE):
            match_count += 1

    sentiment = sia.polarity_scores(message)
    compound = sentiment['compound']

    if match_count >= 2:
        return "High Risk", match_count
    elif match_count == 1 or compound <= -0.5:
        return "Suspicious", match_count
    else:
        return "Safe", match_count

# Function to process a DataFrame of messages
def process_messages(df):
    df['match_count'] = df['message'].apply(lambda msg: get_severity_level(msg)[1])
    df['severity'] = df['message'].apply(lambda msg: get_severity_level(msg)[0])
    df['flagged'] = df['severity'] != "Safe"
    flagged = df[df['flagged'] == True]
    
    # Also add sentiment compound score for display
    flagged['compound'] = flagged['message'].apply(lambda msg: sia.polarity_scores(msg)['compound'])
    
    return flagged

# Home page route with file upload form
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if a file was uploaded
        file = request.files.get('file')
        if file:
            # Save the uploaded file temporarily
            file_path = os.path.join("uploads", file.filename)
            os.makedirs("uploads", exist_ok=True)
            file.save(file_path)
            df = pd.read_csv(file_path)
        else:
            # Use default file if none uploaded
            df = pd.read_csv("sample_chats.csv")
          # Process messages (existing code)
        flagged = process_messages(df)
        
        # Prepare data for charts
        # 1. Risk level distribution
        risk_counts = df['severity'].value_counts().to_dict()
        risk_data = [
            risk_counts.get('High Risk', 0),
            risk_counts.get('Suspicious', 0),
            risk_counts.get('Safe', 0)
        ]
        
        # 2. Pattern detection frequency
        pattern_matches = []
        for _, row in df.iterrows():
            message = row['message']
            for pattern in suspicious_patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    # Use a simplified pattern name for the chart
                    pattern_name = pattern.replace('r"', '').replace('"', '')
                    pattern_name = pattern_name[:15] + '...' if len(pattern_name) > 15 else pattern_name
                    pattern_matches.append(pattern_name)
        
        pattern_counter = Counter(pattern_matches)
        top_patterns = pattern_counter.most_common(5)
        pattern_labels = [p[0] for p in top_patterns]
        pattern_counts = [p[1] for p in top_patterns]
        
        # 3. Sentiment distribution
        sentiment_ranges = {
            'Very Negative': (-1.0, -0.6),
            'Negative': (-0.6, -0.2),
            'Neutral': (-0.2, 0.2),
            'Positive': (0.2, 0.6),
            'Very Positive': (0.6, 1.0)
        }
        
        sentiment_counts = {k: 0 for k in sentiment_ranges.keys()}
        for _, row in df.iterrows():
            compound = sia.polarity_scores(row['message'])['compound']
            for label, (min_val, max_val) in sentiment_ranges.items():
                if min_val <= compound < max_val:
                    sentiment_counts[label] += 1
        
        sentiment_data = list(sentiment_counts.values())
        
        # 4. Match count distribution
        match_count_data = [0, 0, 0, 0]  # 0, 1, 2, 3+
        for count in df['match_count']:
            if count >= 3:
                match_count_data[3] += 1
            else:
                match_count_data[count] += 1
        
        # Convert flagged messages to HTML table for display
        flagged_html = flagged.to_html(classes="table table-striped", index=False)
        
        return render_template(
            "index.html", 
            flagged_html=flagged_html,
            risk_counts=json.dumps(risk_data),
            pattern_labels=json.dumps(pattern_labels),
            pattern_counts=json.dumps(pattern_counts),
            sentiment_counts=json.dumps(sentiment_data),
            match_counts=json.dumps(match_count_data)
        )
    
    # GET request – render the upload form
    return render_template("index.html", flagged_html=None)

if __name__ == '__main__':
    app.run(debug=True)