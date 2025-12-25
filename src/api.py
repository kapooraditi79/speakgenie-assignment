from flask import Flask, jsonify, request
import json
from database import get_db_connection

app = Flask(__name__)

@app.route('/api/workflows', methods=['GET'])
def get_workflows():
    platform = request.args.get('platform')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM workflows WHERE 1=1"
    params = []

    if platform:
        query += " AND platform = %s"
        params.append(platform)
        
    query += " ORDER BY popularity_score DESC LIMIT 50"

    try:
        cursor.execute(query, params)
        workflows = cursor.fetchall()
        
        response_data = []
        for w in workflows:
            # Parse the JSON metadata if it exists
            meta = json.loads(w['meta_data']) if w['meta_data'] else {}

            # DYNAMIC OUTPUT FORMATTING
            if w['platform'] == 'Google Trends':
                # Google Trends Format
                metrics = {
                    "popularity_index": w['popularity_score'], # 0-100 score
                    "growth_percentage": meta.get('trend_growth_percent'),
                    "trend_direction": meta.get('trend_direction'),
                    "insight": meta.get('trend_description')
                }
            else:
                # YouTube/Forum Format
                metrics = {
                    "views": w['views'],
                    "likes": w['likes'],
                    "comments": w['comments'],
                    "engagement_score": w['popularity_score']
                }

            response_data.append({
                "workflow": w['name'],
                "platform": w['platform'],
                "country": w['country'],
                "evidence": metrics, # This object changes shape based on source
                "link": w['url']
            })
            
        return jsonify({"count": len(response_data), "results": response_data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)