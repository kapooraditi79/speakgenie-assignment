import requests
import time


def fetch_forum_workflows(query="workflow", max_pages=4):
    """
    Fetches popular workflows from n8n Forum (Discourse).
    Uses replies + likes proxy (views not available in search API).
    """

    base_url = "https://community.n8n.io/search.json"
    search_query = f"{query} order:latest"

    headers = {
        "User-Agent": "n8n-popularity-bot/1.0",
        "Accept": "application/json"
    }

    print(f"Searching n8n Forum for: '{search_query}'...")

    results = []
    page = 1

    while page <= max_pages:
        params = {"q": search_query, "page": page}

        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=10)

            if response.status_code >= 400:
                print(f"Stopping at Page {page}: API returned {response.status_code}")
                break

            data = response.json()
            topics = data.get("topics", [])

            if not topics:
                print("No more results found.")
                break

            print(f"Page {page}: Found {len(topics)} topics")

            for topic in topics:
                replies = int(topic.get("reply_count", 0))
                posts = int(topic.get("posts_count", 0))

                # likes are NOT provided as count in search API
                likes = 1 if topic.get("liked", False) else 0

                if replies <= 0:
                    continue

                # Replies matter more than likes here
                popularity_score = (replies * 20) + (likes * 5)

                workflow_entry = {
                    "name": topic.get("title"),
                    "url": f"https://community.n8n.io/t/{topic.get('slug')}/{topic.get('id')}",
                    "platform": "n8n Forum",
                    "replies": replies,
                    "posts": posts,
                    "likes_proxy": likes,
                    "popularity_score": popularity_score,
                    "country": "Global"
                }

                results.append(workflow_entry)

            page += 1
            time.sleep(1.2)

        except Exception as e:
            print(f"Failed to fetch forum data: {e}")
            break

    print(f"Total Processed: {len(results)} workflows.")
    return results


if __name__ == "__main__":
    data = fetch_forum_workflows()
    import json
    if data:
        print(json.dumps(data[:2], indent=2))
