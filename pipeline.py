from scraper import get_post_links, get_comments
from sentiment import analyze
from database import init_db, insert_comment, fetch_summary

def run_pipeline(brand, num_pages=2, comments_per_post=10):
    print(f"\n{'='*50}")
    print(f"  Brand-Pulse Pipeline Starting")
    print(f"  Brand: {brand}")
    print(f"{'='*50}\n")

    # Step 1: Initialize DB
    init_db()

    # Step 2: Scrape post links
    links = get_post_links(brand, num_pages=num_pages)

    if not links:
        print("No posts found. Exiting.")
        return

    # Step 3: For each post, scrape comments, analyze, store
    total_stored = 0

    for i, link in enumerate(links):
        print(f"\n[{i+1}/{len(links)}] Processing post...")
        comments = get_comments(link, post_limit=comments_per_post)

        for c in comments:
            score, label = analyze(c["comment_body"])
            insert_comment(
                brand=brand,
                subreddit=c["subreddit"],
                post_title=c["post_title"],
                comment_body=c["comment_body"],
                polarity_score=score,
                sentiment_label=label
            )
            total_stored += 1

    # Step 4: Print summary
    print(f"\n{'='*50}")
    print(f"  Pipeline Complete!")
    print(f"  Total comments stored: {total_stored}")
    print(f"\n  Sentiment Summary for '{brand}':")
    summary = fetch_summary(brand)
    for label, count in summary:
        pct = round((count / total_stored) * 100, 1) if total_stored else 0
        print(f"    {label:<10} {count:>4} comments ({pct}%)")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    run_pipeline(brand="Nike", num_pages=1, comments_per_post=10)