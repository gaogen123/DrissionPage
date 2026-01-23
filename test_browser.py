from DrissionPage import ChromiumPage, ChromiumOptions
import time

# 设置浏览器选项
co = ChromiumOptions()
co.set_argument('--no-sandbox')
co.set_argument('--disable-dev-shm-usage')
co.set_local_port(9222)
co.set_browser_path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')

print("正在启动浏览器...")
page = ChromiumPage(co)

try:
    print("访问百度首页...")
    page.get('https://www.baidu.com')

    print("等待页面加载...")
    time.sleep(3)

    print(f"页面标题: {page.title}")
    print(f"当前URL: {page.url}")

    # 截图
    page.get_screenshot('test_baidu.png')
    print("已保存截图: test_baidu.png")

    print("浏览器保持打开，按Enter关闭...")
    input()

except Exception as e:
    print(f"发生错误: {e}")
    input()

finally:
    print("脚本结束")