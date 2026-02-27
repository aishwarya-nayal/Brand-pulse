from textblob import TextBlob

def analyze(text):
    if not text or not text.strip():
        return 0.0, "Neutral"
    
    polarity = TextBlob(text).sentiment.polarity

    if polarity > 0.1:
        label = "Positive"
    elif polarity < -0.1:
        label = "Negative"
    else:
        label = "Neutral"

    return round(polarity, 4), label

if __name__ == "__main__":
    test_comments = [
        "This product is absolutely amazing, I love it!",
        "Terrible experience, would never buy again.",
        "It's okay, nothing special about it.",
        "  ",  # edge case: blank
    ]

    for comment in test_comments:
        score, label = analyze(comment)
        print(f"[{label}] ({score}) → {comment.strip()}")