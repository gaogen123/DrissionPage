import sqlite3
import datetime
import json

DB_NAME = 'reviews_data_v7.db'

def init_db():
    """初始化数据库，创建表结构"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 启用外键支持
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. 商品表 (goods)
    # 新增 sku_info_json 存储原始的 skuModel.skuProps
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform_goods_id TEXT UNIQUE,
        title TEXT NOT NULL,
        url TEXT,
        price_range TEXT,            -- 价格范围
        sku_info_json TEXT,          -- 商品SKU元数据 (原始 skuProps)
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ); 
    """)
    
    # 2. 评论表 (reviews)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goods_id INTEGER NOT NULL,
        platform_goods_id TEXT,
        content TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (goods_id) REFERENCES goods(id) ON DELETE CASCADE,
        UNIQUE(goods_id, content)
    );
    """)

    # 3. 商品 SKU 表 (goods_skus)
    # 新增 spec_id 存储原始 key
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goods_skus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goods_id INTEGER NOT NULL,
        platform_goods_id TEXT,
        spec_id TEXT,               -- SKU规格ID (原始Key)
        sku_name TEXT,              -- 规格组合名称 (如: 红色 128G)
        props_json TEXT,            -- 规格属性详情 (JSON)
        price TEXT,                 -- 价格
        stock TEXT,                 -- 库存
        info TEXT,                  -- 原始描述信息
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (goods_id) REFERENCES goods(id) ON DELETE CASCADE
    );
    """)

    # 4. 商品图片表 (goods_images)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goods_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goods_id INTEGER NOT NULL,
        platform_goods_id TEXT,
        image_url TEXT NOT NULL,
        is_main INTEGER DEFAULT 0,  -- 是否主图 (保留字段)
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (goods_id) REFERENCES goods(id) ON DELETE CASCADE,
        UNIQUE(goods_id, image_url)
    );
    """)

    # 5. 商品属性表 (goods_attributes)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goods_attributes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goods_id INTEGER NOT NULL,
        platform_goods_id TEXT,
        attr_name TEXT NOT NULL,    -- 属性名 (如: 品牌)
        attr_value TEXT,            -- 属性值 (如: 华为)
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (goods_id) REFERENCES goods(id) ON DELETE CASCADE,
        UNIQUE(goods_id, attr_name)
    );
    """)
    
    conn.commit()
    conn.close()
    print("✅ 数据库表结构已初始化 (goods, reviews, skus, images, attributes)")

def save_product(title, url, platform_id=None, price_range=None, sku_info_json=None):
    """保存商品基础信息"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    goods_id = None
    
    if platform_id:
        cursor.execute("SELECT id FROM goods WHERE platform_goods_id = ?", (platform_id,))
        row = cursor.fetchone()
        if row:
            goods_id = row[0]
            # Update
            cursor.execute("""
                UPDATE goods SET title=?, url=?, price_range=?, sku_info_json=?, created_at=CURRENT_TIMESTAMP 
                WHERE id=?
            """, (title, url, price_range, sku_info_json, goods_id))
        else:
            # Insert
            cursor.execute("""
                INSERT INTO goods (platform_goods_id, title, url, price_range, sku_info_json) 
                VALUES (?, ?, ?, ?, ?)
            """, (platform_id, title, url, price_range, sku_info_json))
            goods_id = cursor.lastrowid
            
    conn.commit()
    conn.close()
    return goods_id

def save_full_product_data(goods_id, platform_id, skus, images, attributes, reviews):
    """
    保存商品的所有关联信息 (SKU, 图片, 属性, 评价)。
    全部使用事务处理，确保数据完整性。
    """
    print(f"    🔍 [DEBUG] save_full_product_data 接收到 {len(skus)} 个 SKU")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # 1. 保存 SKU
        # 先清除旧的 SKU (或者你可以选择增量更新，简单起见先全删全插)
        cursor.execute("DELETE FROM goods_skus WHERE goods_id = ?", (goods_id,))
        if skus:
            # s.get('props_json') 我们的解析代码提供
            sku_data = [(goods_id, platform_id, s.get('spec_id'), s.get('name'), s.get('props_json'), s.get('price'), s.get('stock'), s.get('info')) for s in skus]
            cursor.executemany("INSERT INTO goods_skus (goods_id, platform_goods_id, spec_id, sku_name, props_json, price, stock, info) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", sku_data)
        
        # 2. 保存图片
        # 图片通过 UNIQUE 约束去重，所以使用 INSERT OR IGNORE
        if images:
            img_data = [(goods_id, platform_id, img_url) for img_url in images]
            cursor.executemany("INSERT OR IGNORE INTO goods_images (goods_id, platform_goods_id, image_url) VALUES (?, ?, ?)", img_data)

        # 3. 保存属性
        # 同样先清除旧属性
        cursor.execute("DELETE FROM goods_attributes WHERE goods_id = ?", (goods_id,))
        if attributes:
            # attributes 格式可能是 ["品牌: 华为", ...] 或者字典
            # 使用字典去重，防止同一属性名出现多次导致 UNIQUE 报错
            unique_attrs = {}
            
            for item in attributes:
                k, v = None, None
                if isinstance(item, str):
                    if ':' in item:
                        k, v = item.split(':', 1)
                elif isinstance(item, dict):
                    k = item.get('name') or item.get('propName')
                    v = item.get('value')
                
                if k and v:
                    unique_attrs[k.strip()] = v.strip()
            
            # 转换为插入列表
            attr_data = [(goods_id, platform_id, k, v) for k, v in unique_attrs.items()]
            
            if attr_data:
                cursor.executemany("INSERT INTO goods_attributes (goods_id, platform_goods_id, attr_name, attr_value) VALUES (?, ?, ?, ?)", attr_data)

        # 4. 保存评论
        if reviews:
            rev_data = [(goods_id, platform_id, content) for content in reviews]
            cursor.executemany("INSERT OR IGNORE INTO reviews (goods_id, platform_goods_id, content) VALUES (?, ?, ?)", rev_data)

        conn.commit()
        print(f"    💾 数据入库成功: {len(skus)}个SKU, {len(images)}张图片, {len(attributes) if attributes else 0}个属性, {len(reviews)}条评论")
        
    except Exception as e:
        conn.rollback()
        print(f"    ❌ 数据保存失败: {e}")
    finally:
        conn.close()

def get_products(limit=20):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM goods LIMIT ?", (limit,))
    products = cursor.fetchall()
    conn.close()
    return products

def get_all_reviews():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM reviews")
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

if __name__ == "__main__":
    init_db()
