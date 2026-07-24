import sqlite3

DB_NAME='analytics.db'

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_table():
    conn=get_connection()
    cursor=conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS llm_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        session_id TEXT,
        model_name TEXT,
        user_query TEXT,
        input_tokens INTEGER,
        output_tokens INTEGER,
        total_tokens INTEGER,
        latency_ms REAL,
        feedback TEXT
    )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    
def log_request(
    session_id,
    model_name,
    user_query,
    input_tokens,
    output_tokens,
    total_tokens,
    latency_ms
):
    # get connection
    conn=get_connection()
    cursor=conn.cursor()
    
    cursor.execute("""
    INSERT INTO llm_logs(
        session_id,
        model_name,
        user_query,
        input_tokens,
        output_tokens,
        total_tokens,
        latency_ms
    )
    VALUES(?,?,?,?,?,?,?)
    """,
    (
        session_id,
        model_name,
        user_query,
        input_tokens,
        output_tokens,
        total_tokens,
        latency_ms
    )
    )
    conn.commit() # to add changes to the table
    log_id=cursor.lastrowid # SQL assign ids and we extract that id so that later we can attch the feedback in the same row
    
    cursor.close()
    conn.close()
    return log_id

# next function to update the llm_logs table when the user clicks thumbs up or down
def update_feedback(log_id,feedback):
    conn=get_connection()
    cursor=conn.cursor()
    
    cursor.execute("""
    UPDATE llm_logs
    SET feedback = ?
    WHERE id=?
    """,
    (feedback,log_id))
    
    # add the changes
    conn.commit()
    # close the connection and cursor
    cursor.close()
    conn.close()
    
# analytics functions
def get_all_logs():
    conn=get_connection()
    cursor=conn.cursor()
    
    cursor.execute("""
    SELECT *
    FROM llm_logs
    ORDER BY created_at DESC
    """)
    rows=cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return rows

def get_total_requests():
    conn=get_connection()
    cursor=conn.cursor()
    
    cursor.execute("""
    SELECT COUNT(*)
    FROM llm_logs
    """)
    
    count=cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return count

def get_avg_latency():
    conn=get_connection()
    cursor=conn.cursor()
    
    cursor.execute("""
    SELECT AVG(latency_ms)
    FROM llm_logs
    """)
    
    avg=cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return round(avg or 0,2)

def get_avg_input_tokens():
    conn=get_connection()
    cursor=conn.cursor()
    
    cursor.execute("""
    SELECT AVG(input_tokens)
    FROM llm_logs
    """)
    
    avg=cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    return round(avg or 0,2)

def get_avg_output_tokens():
    conn=get_connection()
    cursor=conn.cursor()
    
    cursor.execute("""
    SELECT AVG(output_tokens)
    FROM llm_logs
    """)
    
    avg=cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    return round(avg or 0,2)

def get_feedback_counts():
    conn=get_connection()
    cursor=conn.cursor()
    
    cursor.execute("""
    SELECT feedback,
    COUNT(*)
    FROM llm_logs
    WHERE feedback IS NOT NULL
    GROUP BY feedback
    """)
    
    rows=cursor.fetchall()
    cursor.close()
    conn.close()
    
    return rows

def get_model_usage():
    conn=get_connection()
    cursor=conn.cursor()
    
    cursor.execute("""
    SELECT model_name,
    COUNT(*)
    FROM llm_logs
    GROUP BY model_name
    """)
    
    rows=cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return rows

