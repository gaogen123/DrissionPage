# -*- coding:utf-8 -*-
"""
连接到已有浏览器的脚本（速度最快）
适用于：已经有 DrissionPage 启动的浏览器在运行
"""
import sys
import traceback

try:
    print("=" * 50)
    print("连接到已有浏览器...")
    from DrissionPage import ChromiumPage

    # 连接到已有的浏览器（默认端口 9222）
    page = ChromiumPage()

    print(f"✅ 连接成功！")
    print(f"当前页面：{page.url}")

    # 访问 1688 网站
    print("\n正在访问 1688.com...")
    page.get('https://www.1688.com')
    print("页面加载完成！")

    # 显示页面信息
    print("\n" + "=" * 50)
    print(f"当前页面标题：{page.title}")
    print(f"当前页面URL：{page.url}")
    print("=" * 50)

    print("\n✅ 访问成功！")

except Exception as e:
    print("\n" + "=" * 50)
    print("❌ 发生错误：")
    print(str(e))
    print("\n可能的原因：")
    print("1. 没有正在运行的浏览器")
    print("2. 浏览器端口不是 9222")
    print("\n解决方法：")
    print("- 先运行 fast_1688.py 启动浏览器")
    print("- 或者手动启动浏览器并添加参数：--remote-debugging-port=9222")
    print("=" * 50)
    sys.exit(1)
