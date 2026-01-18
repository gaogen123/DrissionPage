# -*- coding:utf-8 -*-
"""
演示脚本：打开浏览器并访问 1688
"""
import sys
import traceback

try:
    print("=" * 50)
    print("开始导入 DrissionPage...")
    from DrissionPage import ChromiumPage, ChromiumOptions
    print("导入成功！")

    # 配置浏览器选项（可选）
    print("\n配置浏览器选项...")
    co = ChromiumOptions()
    # co.headless(False)  # 确保不是无头模式
    print("配置完成！")

    # 创建浏览器页面对象
    print("\n创建浏览器页面对象...")
    page = ChromiumPage()
    print("创建成功！")

    # 访问 1688 网站
    print("\n正在访问 1688.com...")
    page.get('https://www.1688.com')
    print("页面加载完成！")

    # 显示页面信息
    print("\n" + "=" * 50)
    print(f"当前页面标题：{page.title}")
    print(f"当前页面URL：{page.url}")
    print("=" * 50)

    print("\n✅ 浏览器已成功打开并访问 1688")
    print("浏览器将保持打开状态，你可以继续手动操作")
    print("脚本执行完毕")

except Exception as e:
    print("\n" + "=" * 50)
    print("❌ 发生错误：")
    print(str(e))
    print("\n详细错误信息：")
    traceback.print_exc()
    print("=" * 50)
    sys.exit(1)
