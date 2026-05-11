import psycopg2
# import boto3

password = "<Enter_DB_Password>"

conn = None
try:
    conn = psycopg2.connect(
        host='database-1-psql.crskgicaqb2p.eu-north-1.rds.amazonaws.com',
        port=5432,
        database='db_name_psql',
        user='postgres',
        password=password,
        sslmode='verify-full',
    sslrootcert='./global-bundle.pem'
    )
    cur = conn.cursor()
    cur.execute('SELECT version();')
    print(cur.fetchone()[0]) #type: ignore
    cur.close()
except Exception as e:
    print(f"Database error: {e}")
    raise
finally:
    if conn:
        conn.close()