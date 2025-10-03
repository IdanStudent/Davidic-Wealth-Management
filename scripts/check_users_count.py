import sqlite3
conn = sqlite3.connect('app.db')
cur = conn.cursor()
try:
    cur.execute('SELECT count(*) FROM users')
    print('Users remaining:', cur.fetchone()[0])
except Exception as e:
    print('Error checking users count:', e)
finally:
    conn.close()
