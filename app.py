from flask import Flask, render_template, request, redirect, url_for
from pipeline import run_pipeline
from database import fetch_summary, fetch_all, init_db
from database import fetch_summary, fetch_all, fetch_sentiment_over_time, init_db
from database import fetch_summary, fetch_all, fetch_sentiment_over_time, init_db, is_data_stale

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    brand = request.form.get("brand", "").strip()
    if not brand:
        return redirect(url_for("index"))

    # Scrape if no data OR data is stale (older than 7 days)
    if not fetch_all(brand) or is_data_stale(brand):
        run_pipeline(brand=brand, num_pages=1, comments_per_post=10)

    return redirect(url_for("results", brand=brand))

@app.route("/refresh")
def refresh():
    brand = request.args.get("brand", "").strip()
    if not brand:
        return redirect(url_for("index"))

    # Force fresh scrape
    run_pipeline(brand=brand, num_pages=1, comments_per_post=10)
    return redirect(url_for("results", brand=brand))

@app.route("/results")
def results():
    brand = request.args.get("brand", "")
    
    summary = fetch_summary(brand)  # [("Positive", 81), ("Neutral", 64), ...]
    comments = fetch_all(brand)     # all rows from DB

    # Build per-post polarity: group by post_title, average polarity
    post_scores = {}
    for row in comments:
        title = row[3]  # post_title column
        score = row[5]  # polarity_score column
        if title not in post_scores:
            post_scores[title] = []
        post_scores[title].append(score)

    post_averages = {
        title: round(sum(scores) / len(scores), 3)
        for title, scores in post_scores.items()
    }

    total = len(comments)
    trend_data = fetch_sentiment_over_time(brand)
    return render_template("results.html",
        brand=brand,
        summary=summary,
        post_averages=post_averages,
        total=total,
        trend_data=trend_data
    )


@app.route("/compare")
def compare():
    brand1 = request.args.get("brand1", "").strip()
    brand2 = request.args.get("brand2", "").strip()

    # Scrape if not already in DB
    if brand1 and not fetch_all(brand1):
        run_pipeline(brand=brand1, num_pages=1, comments_per_post=10)
    if brand2 and not fetch_all(brand2):
        run_pipeline(brand=brand2, num_pages=1, comments_per_post=10)

    def get_summary_dict(brand):
        rows = fetch_summary(brand)
        return {label: count for label, count in rows}

    summary1 = get_summary_dict(brand1) if brand1 else {}
    summary2 = get_summary_dict(brand2) if brand2 else {}

    return render_template("compare.html",
        brand1=brand1,
        brand2=brand2,
        summary1=summary1,
        summary2=summary2
    )


if __name__ == "__main__":
    init_db()
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)