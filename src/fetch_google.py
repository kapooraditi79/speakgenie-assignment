import time
import random
from pytrends.request import TrendReq
import pandas as pd

def fetch_google_trends(keywords=None):
    """
    Fetches Google Trends data for US and India.
    Analyzes the last ~75 days (2.5 months) within a 3-month window.
    """
    if keywords is None:
        keywords = ["n8n workflow", "n8n automation", "n8n tutorial", "n8n vs zapier", "n8n integration"]

    kw_list = keywords[:5]
    
    # fetch US and IN seperately
    target_geos = ['US', 'IN'] 
    
    results = []
    
    # Initialize Pytrends with retries
    pytrends = TrendReq(hl='en-US', tz=360)
    for geo in target_geos:
        print(f"[{geo}] Connecting to Google Trends for: {keywords}...")
        
        try:
            # 'today 3-m' returns DAILY data for the last 90 days
            pytrends.build_payload(kw_list, cat=0, timeframe='today 3-m', geo=geo) 

            # Interest Over Time
            data = pytrends.interest_over_time()    # returns pandas dataframe. 
            
            if data.empty:
                print(f"[{geo}] No data returned.")
                continue

            # Process Each Keyword
            for keyword in keywords:
                if keyword not in data.columns:
                    continue
                
                series = data[keyword]
                
                # Since 'today 3-m' gives daily data, need 30 points for a month.
                
                data_points = len(series)
                if data_points > 80: 
                    # Daily Data (~90 points)
                    window_size = 30 
                else:
                    # Weekly Data (~12 points)
                    window_size = 4 

                # Calculate Trend: Last 30 days vs Previous 30 days
                last_window = series.tail(window_size)
                prev_window = series.iloc[-2*window_size : -window_size]
                
                avg_current = last_window.mean()
                avg_prev = prev_window.mean()
                
                # Avoid DivisionByZero
                if avg_prev == 0:
                    growth_percent = 100.0 if avg_current > 0 else 0.0
                else:
                    growth_percent = ((avg_current - avg_prev) / avg_prev) * 100
                
                current_score = int(series.iloc[-1]) # The score on the very last day
                trend_direction = "UP" if growth_percent > 0 else "DOWN"
                
                entry = {
                    "name": keyword,
                    "url": f"https://trends.google.com/trends/explore?date=today%203-m&geo={geo}&q={keyword.replace(' ', '%20')}",
                    "platform": "Google Trends",
                    "views": 0,
                    # store Growth % in 'likes' and Current Score (0-100) in 'comments'
                    "likes": int(growth_percent), 
                    "comments": current_score, 
                    "popularity_score": current_score + (growth_percent * 2),
                    "country": geo, # 'US' or 'IN'
                    "meta_growth": f"{trend_direction} {round(growth_percent, 1)}% in last 30 days"
                }
                results.append(entry)

            time.sleep(random.uniform(2, 5))

        except Exception as e:
            print(f"[{geo}] Google Trends API failed: {e}")
            continue

    print(f"Processed {len(results)} trend entries for US & IN.")
    return results

if __name__ == "__main__":
    data = fetch_google_trends()
    import json
    print(json.dumps(data, indent=2))