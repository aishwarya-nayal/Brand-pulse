import requests
import time
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

BASE_URL = "https://old.reddit.com"

def get_post_links(brand, subreddit="all", num_pages=2):
    """Scrape search results and return a list of post URLs."""
    post_links = []
    after = None

    for page in range(num_pages):
        url = f"{BASE_URL}/r/{subreddit}/search/?q={brand}&restrict_sr=0&sort=relevance&t=month"
        if after:
            url += f"&after={after}"

        print(f"Fetching page {page + 1}: {url}")
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            print(f"Failed — status {response.status_code}")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        things = soup.find_all("div", class_="search-result-link")  # only posts, not subreddits
        for thing in things:
            a_tag = thing.find("a", class_="search-title")
            if a_tag and a_tag.get("href"):
                link = a_tag["href"]
                # handle both relative and absolute URLs
                if link.startswith("http"):
                    post_links.append(link)
                else:
                    post_links.append(BASE_URL + link)

        # Pagination
        next_button = soup.find("a", rel="nofollow next")
        if next_button:
            after_param = next_button["href"].split("after=")[-1].split("&")[0]
            after = after_param
        else:
            print("No more pages.")
            break

        time.sleep(2)

    print(f"Found {len(post_links)} posts.")
    return post_links


def get_comments(post_url, post_limit=10):
    """Given a post URL, scrape comments and return a list of dicts."""
    comments = []

    print(f"Scraping comments from: {post_url}")
    response = requests.get(post_url, headers=HEADERS)

    if response.status_code != 200:
        print(f"Failed — status {response.status_code}")
        return comments

    soup = BeautifulSoup(response.text, "html.parser")

    # Post title
    title_tag = soup.find("a", class_="title")
    post_title = title_tag.text.strip() if title_tag else "Unknown"

    # Subreddit
    subreddit_tag = soup.find("a", class_="subreddit")
    subreddit = subreddit_tag.text.strip() if subreddit_tag else "Unknown"

    # Comments
    comment_divs = soup.find_all("div", class_="usertext-body", limit=post_limit)
    for div in comment_divs:
        p_tags = div.find_all("p")
        text = " ".join(p.text.strip() for p in p_tags).strip()
        if text and len(text) > 40 and "Subscribers" not in text and "Beginner Guide" not in text:
            comments.append({
                "post_title": post_title,
                "subreddit": subreddit,
                "comment_body": text
            })

    time.sleep(2)  # rate limiting
    return comments


if __name__ == "__main__":
    BRAND = "Nike"

    links = get_post_links(BRAND, num_pages=1)

    # Test comments on first post only
    if links:
        comments = get_comments(links[0])
        print(f"\nScraped {len(comments)} comments from first post\n")
        for c in comments[:3]:
            print(f"Post:    {c['post_title']}")
            print(f"Comment: {c['comment_body'][:120]}")
            print("-" * 60)