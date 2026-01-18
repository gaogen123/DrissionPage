# -*- coding:utf-8 -*-
"""
连接到调试模式浏览器并搜索采集 1688 商品信息
"""
import sys
import time

try:
    print("=" * 60)
    print("连接到浏览器...")

    from DrissionPage import ChromiumPage

    # 连接到调试模式浏览器
    page = ChromiumPage()

    print("✅ 连接成功！")
    print(f"当前页面：{page.title}")

    # 直接访问搜索结果页（更可靠）
    print("\n搜索关键词：妈妈包")
    search_keyword = "妈妈包"
    search_url = f"https://s.1688.com/selloffer/offer_search.htm?keywords={search_keyword}"

    print(f"访问搜索结果页：{search_url}")
    page.get(search_url)

    # 等待页面加载
    time.sleep(5)

    print(f"✅ 搜索结果页加载完成")
    print(f"当前页面：{page.title}")
    print(f"当前 URL：{page.url}")

    # 查找商品（尝试多种选择器）
    print("\n查找商品...")

    # 尝试多种可能的商品选择器
    product_links = None
    selectors = [
        'tag:a@@href^=https://detail.1688.com',  # 商品详情链接
        '.main-img',  # 主图
        '.img',  # 图片
        'tag:img@@src:img.alicdn.com',  # 阿里云图片
    ]

    for selector in selectors:
        elements = page.eles(selector, timeout=2)
        if elements and len(elements) > 0:
            print(f"✅ 使用选择器 '{selector}' 找到 {len(elements)} 个元素")
            product_links = elements
            break
        else:
            print(f"尝试选择器 '{selector}' - 未找到")

    if product_links:
        # 点击第一个商品
        first_product = product_links[0]
        print(f"\n点击第一个商品...")

        first_product.click()

        # 等待新标签页打开并切换过去
        time.sleep(2)

        # 获取所有标签页
        tabs = page.get_tabs()
        print(f"\n当前标签页数量：{len(tabs)}")

        # 切换到最新的标签页（最后一个）
        if len(tabs) > 1:
            # 获取最新打开的标签页对象
            new_tab = page.get_tab(id_or_num=-1)
            # 将 page 重新赋值为新标签页
            page = new_tab
            print(f"✅ 已切换到新标签页")
            time.sleep(1)

        print("✅ 已进入商品详情页")
        print(f"当前页面：{page.title}")
        print(f"当前 URL：{page.url}")

        # 等待页面加载完成
        time.sleep(3)

        # 获取商品价格（尝试多个选择器）
        print("\n获取商品价格...")
        price_element = page.ele('#mainPrice', timeout=2)

        if not price_element:
            # 尝试其他选择器
            price_element = page.ele('.price-comp', timeout=2)

        if not price_element:
            price_element = page.ele('@class:price', timeout=2)

        if price_element:
            price_text = price_element.text
            print(f"✅ 找到价格元素")
            print(f"价格信息：{price_text}")
        else:
            print("❌ 未找到价格元素")

        # 获取商品属性
        print("\n获取商品属性...")
        attributes_element = page.ele('#productAttributes', timeout=2)

        if attributes_element:
            attributes_text = attributes_element.text
            print(f"✅ 找到商品属性")
            print(f"商品属性：\n{attributes_text}")
        else:
            print("❌ 未找到商品属性")

    else:
        print("❌ 未找到商品")

    print("\n" + "=" * 60)
    print("操作完成")
    print("你可以继续手动操作浏览器")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ 错误：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
