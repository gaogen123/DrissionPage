# -*- coding:utf-8 -*-
"""
诊断脚本：检测浏览器启动和访问慢的原因
"""
import sys
import time

print("=" * 60)
print("DrissionPage 性能诊断工具")
print("=" * 60)

# 1. 检查导入速度
print("\n[1] 检查模块导入速度...")
start = time.time()
from DrissionPage import ChromiumPage, ChromiumOptions
elapsed = time.time() - start
print(f"    导入耗时：{elapsed:.2f} 秒")
if elapsed > 2:
    print("    ⚠️  导入较慢，可能是首次导入或系统负载高")

# 2. 检查浏览器启动速度
print("\n[2] 检查浏览器启动速度...")
co = ChromiumOptions()
co.set_argument('--no-first-run')
co.set_argument('--no-default-browser-check')

start = time.time()
try:
    page = ChromiumPage(addr_or_opts=co)
    elapsed = time.time() - start
    print(f"    浏览器启动耗时：{elapsed:.2f} 秒")
    if elapsed > 5:
        print("    ⚠️  启动较慢")
        print("        可能原因：")
        print("        - 系统资源不足")
        print("        - 浏览器路径配置问题")
        print("        - 用户数据目录权限问题")
except Exception as e:
    print(f"    ❌ 启动失败：{e}")
    sys.exit(1)

# 3. 检查页面加载速度（简单页面）
print("\n[3] 测试加载简单页面（example.com）...")
start = time.time()
try:
    page.get('https://example.com')
    elapsed = time.time() - start
    print(f"    加载耗时：{elapsed:.2f} 秒")
    if elapsed > 3:
        print("    ⚠️  加载较慢")
        print("        可能原因：")
        print("        - 网络连接问题")
        print("        - DNS 解析慢")
        print("        - 代理设置问题")
    else:
        print("    ✅ 加载速度正常")
except Exception as e:
    print(f"    ❌ 加载失败：{e}")

# 4. 检查页面加载速度（复杂页面）
print("\n[4] 测试加载复杂页面（百度）...")
start = time.time()
try:
    page.get('https://www.baidu.com')
    elapsed = time.time() - start
    print(f"    加载耗时：{elapsed:.2f} 秒")
    if elapsed > 5:
        print("    ⚠️  加载较慢")
    else:
        print("    ✅ 加载速度正常")
except Exception as e:
    print(f"    ❌ 加载失败：{e}")

# 5. 检查网络连接
print("\n[5] 检查网络连接...")
import subprocess
try:
    result = subprocess.run(['ping', '-c', '3', 'www.baidu.com'],
                          capture_output=True, text=True, timeout=10)
    if 'time=' in result.stdout:
        print("    ✅ 网络连接正常")
        # 提取平均延迟
        lines = result.stdout.split('\n')
        for line in lines:
            if 'avg' in line or '平均' in line:
                print(f"    {line.strip()}")
    else:
        print("    ⚠️  网络可能有问题")
except Exception as e:
    print(f"    ⚠️  无法检测：{e}")

# 6. 检查系统资源
print("\n[6] 检查系统资源...")
try:
    import psutil
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    print(f"    CPU 使用率：{cpu_percent}%")
    print(f"    内存使用率：{memory.percent}%")
    print(f"    可用内存：{memory.available / (1024**3):.2f} GB")

    if cpu_percent > 80:
        print("    ⚠️  CPU 使用率过高")
    if memory.percent > 90:
        print("    ⚠️  内存使用率过高")
except Exception as e:
    print(f"    ⚠️  无法检测：{e}")

# 7. 总结和建议
print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
print("\n建议：")
print("1. 如果浏览器启动慢，尝试清理用户数据目录")
print("2. 如果网页加载慢，检查网络和 DNS 设置")
print("3. 如果系统资源不足，关闭其他程序")
print("4. 使用 ultra_fast.py 脚本禁用图片等资源加载")
print("\n浏览器将保持打开状态以供检查")
