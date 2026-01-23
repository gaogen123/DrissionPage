import sqlite3
import database_manager

db_path = database_manager.DB_NAME
print(f"Checking database file: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(goods)")
    columns = cursor.fetchall()
    
    print("\n[Table: goods] Columns:")
    found = False
    for col in columns:
        # col format: (cid, name, type, notnull, dflt_value, pk)
        print(f"  - {col[1]} ({col[2]})")
        if col[1] == 'platform_goods_id':
            found = True
            
    if found:
        print("\n✅ 字段 'platform_goods_id' 存在！")
    else:
        print("\n❌ 字段 'platform_goods_id' 未找到！")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
