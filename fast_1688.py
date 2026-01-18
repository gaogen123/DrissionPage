# -*- coding:utf-8 -*-
"""
优化版演示脚本：打开浏览器并快速访问 1688
"""
import sys
import traceback

try:
    print("=" * 50)
    print("开始导入 DrissionPage...")
    from DrissionPage import ChromiumPage, ChromiumOptions
    print("导入成功！")

    # 配置浏览器选项（性能优化，保留有头模式）
    print("\n配置浏览器选项...")
    co = ChromiumOptions()

    # 性能优化设置
    co.set_argument('--disable-blink-features=AutomationControlled')  # 隐藏自动化特征
    co.set_argument('--disable-dev-shm-usage')  # 优化内存使用

    # 加快页面加载速度
    co.set_argument('--disable-extensions')  # 禁用扩展
    co.set_argument('--disable-plugins-discovery')  # 禁用插件发现

    # 禁用一些不必要的功能
    co.set_pref('profile.default_content_setting_values.notifications', 2)  # 禁用通知
    co.set_pref('credentials_enable_service', False)  # 禁用密码保存提示
    co.set_pref('profile.password_manager_enabled', False)  # 禁用密码管理器

    # 网络优化
    co.set_argument('--disk-cache-size=0')  # 禁用磁盘缓存（使用内存缓存更快）
    co.set_argument('--media-cache-size=0')  # 禁用媒体缓存

    print("配置完成！")

    # 创建浏览器页面对象
    print("\n创建浏览器页面对象...")
    page = ChromiumPage(addr_or_opts=co)
    print("创建成功！")

    # 访问 1688 网站
    print("\n正在访问 1688.com...")
    print("提示：首次访问可能需要加载较多资源，请稍候...")

    page.get('https://www.1688.com')
    print("页面加载完成！")

    # 显示页面信息
    print("\n" + "=" * 50)
    print(f"当前页面标题：{page.title}")
    print(f"当前页面URL：{page.url}")
    print("=" * 50)

    print("\n✅ 浏览器已成功打开并访问 1688")
    print("浏览器将保持打开状态，你可以继续手动操作")
    print("\n优化提示：")
    print("- 如果还是很慢，可能是网络问题或 1688 网站本身加载慢")
    print("- 可以在浏览器中按 F12 打开开发者工具查看网络请求")
    print("\n脚本执行完毕")

except Exception as e:
    print("\n" + "=" * 50)
    print("❌ 发生错误：")
    print(str(e))
    print("\n详细错误信息：")
    traceback.print_exc()
    print("=" * 50)
    sys.exit(1)
