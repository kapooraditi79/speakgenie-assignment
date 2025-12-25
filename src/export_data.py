import os
from database import get_db_connection

def export_sql():
    conn = get_db_connection()
    if conn is None: return
    cursor = conn.cursor()
    
    # Open a file to write the SQL
    with open("workflows_dump.sql", "w", encoding="utf-8") as f:
        # Write the Table Creation Logic
        f.write("DROP TABLE IF EXISTS workflows;\n")
        f.write("""
CREATE TABLE workflows (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    platform VARCHAR(50),
    url VARCHAR(500) UNIQUE,
    country VARCHAR(10) DEFAULT 'Global',
    views INT DEFAULT 0,
    likes INT DEFAULT 0,
    comments INT DEFAULT 0,
    popularity_score FLOAT DEFAULT 0.0,
    meta_data JSON DEFAULT NULL,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);\n\n""")

        # Fetch all data
        cursor.execute("SELECT * FROM workflows")
        rows = cursor.fetchall()
        
        # Write the Insert Statements
        f.write("INSERT INTO workflows (name, platform, url, country, views, likes, comments, popularity_score, meta_data) VALUES\n")
        
        values_list = []
        for r in rows:
            # Format strings safely
            name = r[1].replace("'", "''").replace("\\", "\\\\")
            platform = r[2]
            url = r[3]
            country = r[4]
            views = r[5]
            likes = r[6]
            comments = r[7]
            score = r[8]
            meta = f"'{r[9]}'" if r[9] else "NULL"
            
            val = f"('{name}', '{platform}', '{url}', '{country}', {views}, {likes}, {comments}, {score}, {meta})"
            values_list.append(val)
        
        f.write(",\n".join(values_list))
        f.write(";\n")
        
    print(f"Success! Exported {len(rows)} workflows to 'workflows_dump.sql'.")

if __name__ == "__main__":
    export_sql()