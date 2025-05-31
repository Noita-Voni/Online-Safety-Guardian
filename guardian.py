import pandas as pd
import re
from colorama import init, Fore, Style
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Initialize colorama
init(autoreset=True)

# Download the VADER lexicon for sentiment analysis if not already downloaded
nltk.download('vader_lexicon')

# Initialize the Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

# Step 1: Load the chat messages
try:
    df = pd.read_csv("sample_chats.csv")
except FileNotFoundError:
    print(Fore.RED + "CSV file not found. Make sure 'sample_chats.csv' is in the same folder.")
    exit()

# Step 2: Define suspicious regex patterns (Expanded)
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

# Step 3: Function to count regex matches and determine severity including sentiment analysis
def get_severity_level(message):
    match_count = 0
    for pattern in suspicious_patterns:
        if re.search(pattern, message, re.IGNORECASE):
            match_count += 1

    sentiment = sia.polarity_scores(message)
    compound = sentiment['compound']

    # Determine severity:
    if match_count >= 2:
        return "High Risk", match_count
    elif match_count == 1 or compound <= -0.5:
        return "Suspicious", match_count
    else:
        return "Safe", match_count

# Apply detection and add severity level using the updated function
df['match_count'] = df['message'].apply(lambda msg: get_severity_level(msg)[1])
df['severity'] = df['message'].apply(lambda msg: get_severity_level(msg)[0])
# Flag messages if severity is not "Safe"
df['flagged'] = df['severity'] != "Safe"

# Step 4: Print flagged messages with color-coded output and sentiment analysis
flagged = df[df['flagged'] == True]

print("\n--- Flagged Messages ---\n")
if flagged.empty:
    print(Fore.GREEN + "No flagged messages found!")
else:
    for index, row in flagged.iterrows():
        sentiment = sia.polarity_scores(row['message'])
        sentiment_info = f"(Compound Sentiment: {sentiment['compound']})"
        
        # Choose color based on severity:
        if row['severity'] == "High Risk":
            color = Fore.RED
        elif row['severity'] == "Suspicious":
            color = Fore.YELLOW
        else:
            color = Fore.GREEN  # This case won't happen since safe messages aren't flagged
        
        print(color + f"ID: {row['id']} | Severity: {row['severity']} | Matches: {row['match_count']} | Message: {row['message']} {sentiment_info}")

# Step 5: Save flagged messages to a CSV file
flagged.to_csv("flagged_messages.csv", index=False)
print(Fore.CYAN + "\nFlagged messages saved to 'flagged_messages.csv'")

