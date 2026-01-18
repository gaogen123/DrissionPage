#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
简化版演示脚本：打开浏览器并访问 1688
"""
import sys

# 强制刷新输出
sys.stdout = open(sys.stdout.fileno(), 'w', buffering=1)

print("步骤 1: 导入 DrissionPage...")
sys.stdout.flush()

from DrissionPage import ChromiumPage

print("步骤 2: 创建浏览器页面...")
sys.stdout.flush()

page = ChromiumPage()

print("步骤 3: 访问 1688.com...")
sys.stdout.flush()

page.get('https://www.1688.com')

print(f"✅ 成功！标题：{page.title}")
print(f"✅ URL：{page.url}")
sys.stdout.flush()

print("\n浏览器已打开，可以进行手动操作")
print("脚本执行完毕")
sys.stdout.flush()
