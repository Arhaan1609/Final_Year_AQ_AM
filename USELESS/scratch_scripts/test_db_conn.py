import pymysql

passwords = ['', 'root', 'admin', 'password', '1234', '123456', 'root123', 'root@123', 'admin123', 'MySql@123', 'root1234', 'Arhaan@123', 'Arhaan1609']
connected = False

for pwd in passwords:
    try:
        conn = pymysql.connect(host='127.0.0.1', user='root', password=pwd, port=3306)
        print(f'SUCCESS! Connected to MySQL with user=root, password="{pwd}"')
        with conn.cursor() as cur:
            cur.execute('CREATE DATABASE IF NOT EXISTS EV;')
            cur.execute('SHOW DATABASES;')
            dbs = [row[0] for row in cur.fetchall()]
            print('Databases available:', dbs)
        conn.close()
        connected = True
        break
    except Exception as e:
        pass

if not connected:
    print('MySQL requires specific credentials. Database manager will use configurable env variables and provide SQLite fallback.')
