# -*- coding:utf-8 -*-
"""
连接到用户手动打开的浏览器进行数据采集
使用方法：
1. 先手动启动浏览器（参考下面的命令）
2. 运行此脚本连接到浏览器
"""
import sys

try:
    print("=" * 60)
    print("连接到现有浏览器...")
    print("=" * 60)

    from DrissionPage import ChromiumPage

    # 连接到已有浏览器（默认端口 9222）
    page = ChromiumPage()

    print(f"\n✅ 成功连接到浏览器！")
    print(f"当前标签页数量：{len(page.get_tabs())}")
    print(f"当前页面：{page.title}")
    print(f"URL：{page.url}")

    print("\n" + "=" * 60)
    print("现在可以开始数据采集了！")
    print("=" * 60)

    # 示例：采集当前页面的标题和链接
    print("\n[示例] 采集当前页面的所有链接：")
    links = page.eles('tag:a')
    print(f"找到 {len(links)} 个链接")

    # 显示前 5 个链接
    for i, link in enumerate(links[:5], 1):
        text = link.text.strip()
        href = link.attr('href')
        if text and href:
            print(f"{i}. {text[:30]:<30} -> {href[:50]}")

    print("\n提示：浏览器保持打开，你可以继续操作或编写采集脚本")

except Exception as e:
    print("\n" + "=" * 60)
    print("❌ 连接失败！")
    print("=" * 60)
    print(f"错误：{e}")
    print("\n可能的原因：")
    print("1. 浏览器没有以调试模式启动")
    print("2. 浏览器端口不是 9222")
    print("\n解决方法：")
    print("请先关闭所有 Chrome/Edge 浏览器，然后运行以下命令之一：")
    print("\n【macOS Chrome】")
    print('/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome_debug" &')
    print("\n【macOS Edge】")
    print('/Applications/Microsoft\\ Edge.app/Contents/MacOS/Microsoft\\ Edge --remote-debugging-port=9222 --user-data-dir="/tmp/edge_debug" &')
    print("\n然后再运行此脚本")
    print("=" * 60)
    sys.exit(1)
