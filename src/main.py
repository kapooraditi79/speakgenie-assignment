import sys
import json
import time
from database import get_db_connection

try:
    from fetch_youtube import fetch_youtube_workflows
    from fetch_forum import fetch_forum_workflows
    from fetch_google import fetch_google_trends
except ImportError as e:
    print(f"Error importing fetchers: {e}")
    sys.exit(1)

def save_to_database(data_list, source_name):
    if not data_list:
        print(f"[{source_name}] No data to save.")
        return

    conn = get_db_connection()
    if conn is None: return
    cursor = conn.cursor()

    # Updated Query: Handles the new meta_data JSON column
    query = """
    INSERT INTO workflows 
    (name, platform, views, likes, comments, url, popularity_score, country, meta_data)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        views = VALUES(views),
        likes = VALUES(likes),
        comments = VALUES(comments),
        popularity_score = VALUES(popularity_score),
        meta_data = VALUES(meta_data),
        last_updated = CURRENT_TIMESTAMP
    """

    rows_to_insert = []
    
    for item in data_list:
        # Handle Google Trends differently than others
        if source_name == "Google Trends":
            # For Trends: Views/Likes/Comments are not applicable (set to 0)
            # store the specific trend metrics in the JSON column
            views = 0
            likes = 0
            comments = 0
            
            meta_json = json.dumps({
                "trend_growth_percent": item.get('likes'),
                "trend_direction": item.get('meta_growth').split()[0] if 'meta_growth' in item else "N/A",
                "trend_description": item.get('meta_growth')
            })
        else:
            # For YouTube/Forums, use standard columns
            views = item.get('views', 0)
            likes = item.get('likes', 0)
            comments = item.get('comments', 0)
            meta_json = None # No special metadata needed

        rows_to_insert.append((
            item['name'],
            item['platform'],
            views,
            likes,
            comments,
            item['url'],
            item['popularity_score'],
            item['country'],
            meta_json 
        ))

    try:
        cursor.executemany(query, rows_to_insert)
        conn.commit()
        print(f"[{source_name}] Successfully saved {cursor.rowcount} records.")
    except Exception as e:
        print(f"[{source_name}] DB Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def main():
    print("--- Starting n8n Popularity Engine ---")
    
    # YouTube 
    try:
        data = fetch_youtube_workflows()
        save_to_database(data, "YouTube")
    except Exception as e: print(f"YT Error: {e}")

    # Forum
    try:
        data = fetch_forum_workflows()
        save_to_database(data, "n8n Forum")
    except Exception as e: print(f"Forum Error: {e}")

    # Google Trends 
    try:
        data = fetch_google_trends()
        save_to_database(data, "Google Trends")
    except Exception as e: print(f"Trends Error: {e}")

if __name__ == "__main__":
    main()