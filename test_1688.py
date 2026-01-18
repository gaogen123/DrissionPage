# -*- coding:utf-8 -*-
"""
测试脚本：打开调试浏览器并访问 1688
"""
from DrissionPage import ChromiumPage

# 创建浏览器页面对象
page = ChromiumPage()

# 访问 1688 网站
print("正在访问 1688.com...")
page.get('https://www.1688.com')

print("页面加载完成！")
print(f"当前页面标题：{page.title}")
print(f"当前页面URL：{page.url}")

# 浏览器将保持打开状态
print("\n浏览器已打开，可以手动操作")
print("脚本执行完毕，浏览器将继续运行")
