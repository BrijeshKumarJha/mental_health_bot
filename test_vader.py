import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download('vader_lexicon', quiet=True)
sia = SentimentIntensityAnalyzer()

sentence = "I am very stressed, I have my studies pending but i don't know where to start. i have so much burden of others expectations on me"

# 1. View the Overall Sentence Score
overall_score = sia.polarity_scores(sentence)
print("--- OVERALL SCORE ---")
print(f"Negative: {overall_score['neg']}")
print(f"Neutral:  {overall_score['neu']}")
print(f"Positive: {overall_score['pos']}")
print(f"Compound: {overall_score['compound']}\n")

# 2. View the Individual Word Scores from the Master Lexicon
print("--- INDIVIDUAL WORD SCORES ---")
# Clean the sentence of punctuation and split it into words
words = sentence.lower().replace(".", "").split()
words = sentence.lower().replace(",", "").split()

for word in words:
    # Check if the word exists in the VADER dictionary
    if word in sia.lexicon:
        print(f"'{word}': {sia.lexicon[word]}")
    else:
        print(f"'{word}': (Not in lexicon, score is 0.0)")