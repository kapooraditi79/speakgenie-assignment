# search the yt videos using words- "n8n workflow", "n8n automation", "n8n tutorials"
# get the enrichment using batching of the videos from step 1
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

def fetch_youtube_workflows(query="n8n popular workflows", max_results=50):
    """
    Fetches videos gets their stats, and calculates popularity metrics
    """
    api_key= os.getenv('YOUTUBE_API_KEY')
    youtube= build('youtube','v3', developerKey= api_key)
    next_page_token= None
    print(f"Searching the youtube for query: {query}")


    search_response= youtube.search().list(
        q= query,
        part= 'id, snippet',
        maxResults=max_results,
        type='video',
        relevanceLanguage='en',
        pageToken= next_page_token,
    ).execute()

    video_ids=[]
    video_map={} 

    for item in search_response.get('items',[]):
        vid_id= item['id']['videoId']
        video_ids.append(vid_id)

        video_map[vid_id]={
            'name': item['snippet']['title'],
            'url': f"https://www.youtube.com/watch?v={vid_id}",
            "platform": "YouTube",
            'country': 'US' # default
            
        }

    next_page_token= search_response.get('nextPageToken')
    if not video_ids:
        print("No videos found")
        return []
    
    print(f"Getting the stats for {len(video_ids)} videos")

    stats_response = youtube.videos().list(
        part="statistics,snippet",
        id=",".join(video_ids) # Join IDs with commas for batch request
    ).execute()

    results=[]

    for item in stats_response.get('items',[]):
        vid_id=item['id']
        stats= item.get('statistics')
        if not stats:
            continue

        views=int(stats.get('viewCount',  0))
        likes= int(stats.get('likeCount', 0))
        comments= int(stats.get('commentCount',0))

        if views==0:
            continue

        like_ratio = round(likes / views, 4)       
        comment_ratio = round(comments / views, 4) 
        
        popularity_score = views + (likes * 10) + (comments * 20)

        video_data= video_map[vid_id]
        video_data.update({
            'views': views,
            'likes': likes,
            'comments': comments,
            'popularity_score': popularity_score,
        })

        results.append(video_data)

    print(f"Processed {len(results)} videos.")
    return results

if __name__ == "__main__":
    data = fetch_youtube_workflows()
    import json