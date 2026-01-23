from DrissionPage import ChromiumPage, ChromiumOptions
import json
import time

import sys
import io

# 强制设置标准输出为 utf-8，解决 Windows 下打印 emoji 报错的问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def debug_detail_extraction():
    print("🚀 脚本开始运行...")
    
    # 设置页面对象，去掉 auto_port() 以尝试连接默认已打开的浏览器
    try:
        print("    正在尝试连接 ChromiumPage...")
        page = ChromiumPage()
        print("    ✅ ChromiumPage 连接成功")
    except Exception as e:
        print(f"    ❌ 连接失败: {e}")
        return
    
    # 自动寻找正确的标签页
    target_tab = None
    print(f"📋 当前共有 {page.tabs_count} 个标签页")
    
    # 遍历所有标签页寻找商品页
    for tab in page.get_tabs():
        url = tab.url
        title = tab.title
        print(f"    - 检查标签: {title[:20]}... | {url[:40]}...")
        if "detail.1688.com/offer/" in url:
            target_tab = tab
            break
            
    if target_tab:
        print(f"🚀 切换到目标商品页: {target_tab.title}")
        target_tab.set.activate() # 激活该标签页
        page = target_tab     # 将 page 对象指向该 tab
    else:
        print("⚠️ 未找到明显的 1688 商品详情页，尝试使用当前激活页...")
        # 即使没找到，也继续尝试当前页，万一 URL 格式不对呢
    
    print(f"🚀 当前调试页面: {page.title}")
    
    # print("⏳ 等待页面加载...")
    # page.wait.doc_loaded()
    # time.sleep(2) # 等待可能的动态渲染
    
    html = page.html
    print(f"📄 页面长度: {len(html)}")

    # --- 提取 offerAttribute (商品属性) ---
    # --- 尝试提取全局数据 window.__INIT_DATA ---
    print("\n🔍 尝试提取 window.__INIT_DATA ...")
    import re
    
    # --- 关键词扫描调试模式 ---
    print("\n🔍 启动关键词全页面扫描...")
    
    keywords = ['属性', 'offerAttribute', 'props', 'globalData']
    
    # 获取所有的 script 标签
    scripts = page.eles('tag:script')
    
    # 1. 扫描所有 Script 标签
    print(f"    正在扫描 {len(scripts)} 个 Script 标签...")
    found_in_script = False
    for i, script in enumerate(scripts):
        txt = script.text
        if not txt: continue
        
        for kw in keywords:
            if kw in txt:
                print(f"    ✅ 在 Script[{i}] 中发现关键词 '{kw}'")
                print(f"       >> 片段: {txt[:100].replace('\n', ' ')}...")
                found_in_script = True
                
    if not found_in_script:
        print("    ❌ Script 标签中未发现任何关键信息")

    # 2. 扫描可见文本 (检查是否被反爬阻挡)
    print("\n🔍 检查页面可见文本...")
    body_text = page.ele('tag:body').text
    print(f"    页面文本长度: {len(body_text)}")
    print(f"    页面文本前 200 字: {body_text[:200].replace('\n', ' ')}")
    
    if "验证" in body_text or "登录" in body_text:
        print("    ⚠️ 警告: 页面可能包含验证码或登录提示！")

    # --- 专注调试 SKU 和 价格信息 ---
    print("\n🔍 --- SKU & 价格信息深度调试 ---")
    
    # 1. JSON 变量嗅探
    print("1️⃣ 正在嗅探包含 SKU 信息的 Script 变量...")
    sku_keywords = ['skuMap', 'skuProp', 'originalPrice', 'discountPrice', 'canBookCount']
    
    found_json = False
    for i, script in enumerate(scripts):
        txt = script.text
        if not txt: continue
        
        # 统计命中的关键词
        hit_count = sum(1 for k in sku_keywords if k in txt)
        if hit_count >= 2: # 至少命中两个关键词才认为是相关的
            print(f"    ✅ Script[{i}] 疑似包含 SKU 数据 (命中 {hit_count} 个关键词)")
            print(f"       片段: {txt[:150].replace('\n', ' ')}...")
            
            # 尝试提取变量名
            match = re.search(r'var\s+([a-zA-Z0-9_$]+)\s*=', txt) or re.search(r'window\.([a-zA-Z0-9_$]+)\s*=', txt)
            if match:
                print(f"       👉 发现变量赋值: {match.group(1)}")
            
            found_json = True

    if not found_json:
        print("    ❌ 未在 Script 中发现明显的 SKU 数据结构")

    # 2. DOM 价格/SKU 结构嗅探
    print("\n2️⃣ 正在检查 SKU DOM 结构...")
    
    # 价格
    price_eles = page.eles('.price-text') or page.eles('.discount-price') or page.eles('.offer-price')
    if price_eles:
        print(f"    💰 发现价格元素: {[e.text for e in price_eles[:3]]}")
    else:
        print("    ⚠️ 未找到明显价格元素")

    # SKU 规格区域
    sku_wrappers = page.eles('.sku-item-wrapper') or page.eles('.prop-item') or page.eles('.obj-sku-prop')
    if sku_wrappers:
        print(f"    📦 发现 {len(sku_wrappers)} 个 SKU 规格选项")
    
    # SKU 表格 (如果是表格形式)
    sku_table = page.ele('.table-sku')
    if sku_table:
        print("    📊 发现 SKU 表格布局")
        rows = sku_table.eles('tag:tr')
        print(f"       行数: {len(rows)}")

    # 库存
    stock_ele = page.ele('.mod-detail-purchasing-limit') or page.ele('.start-order-count')
    if stock_ele:
        print(f"    🔢 起订量/库存相关: {stock_ele.text}")

    # --- 专注调试 图片提取 ---
    print("\n🖼️ --- 商品图片信息深度调试 ---")
    
    # 定义一组潜在的图片容器选择器
    img_selectors = [
        '.detail-gallery-img',          # 常见
        '.layout-left .tab-trigger',    # 左侧缩略图
        '.main-image-thumb-item img',   # 另一种缩略图结构
        '.detail-main-image img',       # 主图
        '.gallery-stage img',           # 画廊模式
        '.swipe-image',                # 移动端/响应式
        '.detail-video-image'           # 视频封面图
    ]
    
    for selector in img_selectors:
        imgs = page.eles(selector)
        if imgs:
            print(f"    ✅ 选择器 '{selector}' 匹配到 {len(imgs)} 个元素")
            for i, img in enumerate(imgs[:3]):
                # 打印关键属性
                src = img.attr('src')
                data_src = img.attr('data-src') or img.attr('data-lazy-src')
                style = img.attr('style')
                print(f"       [{i}] tag: {img.tag} | src: {str(src)[:30]}... | data-src: {str(data_src)[:30]}...")
                # print(f"           HTML: {img.html[:100]}...") # 需要看细节时打开
        else:
            print(f"    ❌ 选择器 '{selector}' 未匹配到任何元素")

    # 宽泛搜索：找所有的大图
    print("\n    🔍 尝试宽泛搜索页面中较大的图片...")
    all_imgs = page.eles('tag:img')
    large_imgs = []
    for img in all_imgs:
        # 这里只是简单的通过属性判断，无法直接获取渲染尺寸(除非用 js)
        # 但通常商品图会有 'detail' 或 'gallery' 这样的关键词在 class 或 src 里
        src = img.attr('src') or ""
        cls = img.attr('class') or ""
        if "summ" in src or "search" in src: continue # 跳过小图
        
        if ("这里写过滤条件" == "不需要"): pass
        
        # 简单打印前几个 class 里带 gallery 的
        if "gallery" in cls or "thumb" in cls:
             large_imgs.append(img)
             
    if large_imgs:
        print(f"    ✨ 找到 {len(large_imgs)} 个可能的相关图片元素 (Class含 gallery/thumb):")
        for img in large_imgs[:3]:
            print(f"       src: {img.attr('src')[:50]}... | class: {img.attr('class')}")

    # page.close()

if __name__ == "__main__":
    debug_detail_extraction()
