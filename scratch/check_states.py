import sqlite3

conn = sqlite3.connect("fleet_intelligence.db")
cur = conn.cursor()

for prefix in ["DL", "GJ", "MH", "TS", "KA", "TN"]:
    cur.execute(f"SELECT id, model, soc, soh, battery_temp, voltage, current FROM vehicles WHERE id LIKE '{prefix}%' LIMIT 2")
    rows = cur.fetchall()
    print(f"Prefix {prefix} ({len(rows)} samples):")
    for r in rows:
        print(" ", r)

conn.close()
