# -*- coding:utf-8 -*-
"""
极速模式：禁用大部分资源加载，只保留HTML
适合需要快速访问网页但不需要完整渲染的场景
"""
import sys
import traceback

try:
    print("=" * 50)
    print("配置极速模式浏览器...")
    from DrissionPage import ChromiumPage, ChromiumOptions

    co = ChromiumOptions()

    # 禁用图片加载（大幅提升速度）
    co.set_argument('--blink-settings=imagesEnabled=false')

    # 禁用 JavaScript（如果不需要的话，可以极大提升速度）
    # 注意：很多网站依赖 JS，禁用后可能无法正常使用
    # co.set_argument('--disable-javascript')

    # 性能优化
    co.set_argument('--disable-gpu')  # 禁用 GPU
    co.set_argument('--disable-software-rasterizer')
    co.set_argument('--disable-dev-shm-usage')
    co.set_argument('--no-sandbox')

    # 禁用各种不必要的功能
    co.set_argument('--disable-extensions')
    co.set_argument('--disable-plugins')
    co.set_argument('--disable-web-security')
    co.set_argument('--disable-features=IsolateOrigins,site-per-process')

    # 禁用自动化检测
    co.set_argument('--disable-blink-features=AutomationControlled')

    # 设置浏览器偏好
    co.set_pref('profile.managed_default_content_settings.images', 2)  # 禁用图片
    co.set_pref('profile.default_content_setting_values.notifications', 2)  # 禁用通知

    # 网络优化
    co.set_argument('--proxy-server="direct://"')
    co.set_argument('--proxy-bypass-list=*')

    print("创建浏览器实例...")
    page = ChromiumPage(addr_or_opts=co)

    print("\n✅ 浏览器已启动（极速模式）")
    print("注意：此模式下不会加载图片，页面可能显示不完整")

    # 访问百度测试速度
    print("\n测试访问百度...")
    import time
    start = time.time()
    page.get('https://www.baidu.com')
    elapsed = time.time() - start
    print(f"✅ 百度加载完成，耗时：{elapsed:.2f} 秒")

    # 访问 1688
    print("\n访问 1688.com...")
    start = time.time()
    page.get('https://www.1688.com')
    elapsed = time.time() - start
    print(f"✅ 1688 加载完成，耗时：{elapsed:.2f} 秒")

    print(f"\n当前页面：{page.title}")
    print(f"URL：{page.url}")

    print("\n浏览器将保持打开状态")

except Exception as e:
    print("\n" + "=" * 50)
    print("❌ 发生错误：")
    print(str(e))
    traceback.print_exc()
    print("=" * 50)
    sys.exit(1)
