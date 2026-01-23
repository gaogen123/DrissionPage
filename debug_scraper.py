from DrissionPage import ChromiumPage, ChromiumOptions
import time
import json

# 设置浏览器选项
co = ChromiumOptions()
co.set_argument('--no-sandbox')
co.set_argument('--disable-dev-shm-usage')
co.set_local_port(9222)
co.set_browser_path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')

# 创建页面对象
page = ChromiumPage(co)

try:
    # 访问拼多多搜索页面
    print("正在访问拼多多搜索页面...")
    page.get('https://mobile.pinduoduo.com/search_result.html?search_key=妈妈包')

    # 等待页面加载
    print("等待页面加载...")
    time.sleep(5)

    # 检查页面状态
    print(f"当前URL: {page.url}")
    page.wait.doc_loaded()
    print(f"页面加载状态: {page.states.ready_state}")

    # 再次等待，确保页面完全加载
    time.sleep(3)

    print(f"页面标题: {page.title}")

    # 调试：输出页面HTML结构的前500个字符
    print("\n=== 页面HTML结构（前500字符）===")
    html_content = page.html
    print(html_content[:500])

    # 调试：查找所有可能的商品相关元素
    print("\n=== 查找可能的商品容器 ===")

    # 常见的商品容器选择器
    possible_containers = [
        'css:.goods-item',
        'css:.item',
        'css:.product',
        'css:.product-item',
        'css:[data-testid*="product"]',
        'css:[class*="item"]',
        'css:[class*="goods"]',
        'css:[class*="product"]'
    ]

    for selector in possible_containers:
        elements = page.eles(selector)
        if len(elements) > 0:
            print(f"{selector}: 找到 {len(elements)} 个元素")
            if len(elements) <= 5:  # 只显示前5个
                for i, elem in enumerate(elements):
                    print(f"  元素{i+1}: {elem.html[:100]}...")
        else:
            print(f"{selector}: 未找到元素")

    # 调试：查找所有包含"商品"或"价格"文本的元素
    print("\n=== 查找包含关键词的元素 ===")
    all_text_elements = page.eles('tag:*')

    # 查找包含价格符号的元素
    price_candidates = []
    title_candidates = []

    for elem in all_text_elements[:50]:  # 只检查前50个元素
        text = elem.text.strip()
        if text and len(text) > 0:
            if '¥' in text or '￥' in text or any(char.isdigit() for char in text):
                if len(text) < 20:  # 价格通常较短
                    price_candidates.append((elem, text))
            elif len(text) > 3 and len(text) < 50:  # 标题通常中等长度
                title_candidates.append((elem, text))

    print("可能的标题元素:")
    for elem, text in title_candidates[:10]:
        print(f"  文本: '{text}' | 标签: {elem.tag} | 类名: {elem.attr('class')}")

    print("\n可能的價格元素:")
    for elem, text in price_candidates[:10]:
        print(f"  文本: '{text}' | 标签: {elem.tag} | 类名: {elem.attr('class')}")

    # 调试：查找所有图片元素
    print("\n=== 查找图片元素 ===")
    images = page.eles('tag:img')
    print(f"找到 {len(images)} 个图片元素")
    for i, img in enumerate(images[:10]):
        src = img.attr('src') or img.attr('data-src')
        alt = img.attr('alt')
        print(f"  图片{i+1}: src='{src}' alt='{alt}'")

    # 让用户手动检查页面
    input("\n请检查浏览器中的页面，按回车键继续...")

except Exception as e:
    print(f"发生错误: {e}")
    import traceback
    traceback.print_exc()

finally:
    # 保持浏览器打开以便调试
    print("调试脚本执行完毕，浏览器保持打开")
