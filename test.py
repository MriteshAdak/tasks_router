import psycopg2
import boto3

auth_token = boto3.client('rds', region_name='eu-central-1').generate_db_auth_token(DBHostname='database-1-instance-1.crck6826scxq.eu-central-1.rds.amazonaws.com', Port=5432, DBUsername='postgres', Region='eu-central-1')

conn = None
try:
    conn = psycopg2.connect(
        host='database-1-instance-1.crck6826scxq.eu-central-1.rds.amazonaws.com',
        port=5432,
        database='postgres',
        user='postgres',
        password=auth_token,
        sslmode='require'
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute('SELECT version();')
    print(cur.fetchone()[0])
    print("Successfully connected to the database!")
    cur.close()
except Exception as e:
    print(f"Database error: {e}")
    raise
finally:
    if conn:
        conn.close()