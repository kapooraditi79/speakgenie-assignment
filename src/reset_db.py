from database import get_db_connection

def reset_table():
    conn = get_db_connection()
    if conn is None: return
    cursor = conn.cursor()

    # Drop the old table
    cursor.execute("DROP TABLE IF EXISTS workflows;")

    # Create the new table
    create_query = """
    CREATE TABLE workflows (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        platform VARCHAR(50),
        views INT DEFAULT 0,
        likes INT DEFAULT 0,
        comments INT DEFAULT 0,
        url VARCHAR(500) UNIQUE,
        popularity_score FLOAT DEFAULT 0.0,
        country VARCHAR(10) DEFAULT 'Global',
        meta_data JSON DEFAULT NULL,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(create_query)
        conn.commit()
        print("Success: Database table 'workflows' has been reset to the final schema (UTF-8 enabled).")
    except Exception as e:
        print(f"Failed to create table: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    confirm = input("WARNING: This will DELETE all existing data. Type 'yes' to proceed: ")
    if confirm.lower() == 'yes':
        reset_table()
    else:
        print("Cancelled.")