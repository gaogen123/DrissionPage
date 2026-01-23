from DrissionPage import ChromiumPage, ChromiumOptions
import json

def search_and_collect():
    # 设置浏览器选项
    co = ChromiumOptions()
    co.set_argument('--no-sandbox')
    co.set_argument('--disable-dev-shm-usage')
    co.set_local_port(9222)
    co.set_browser_path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')

    # 创建页面对象
    print("正在启动浏览器...")
    page = ChromiumPage(co)

    try:
        print("正在自动执行搜索...")
        page.get('https://mobile.pinduoduo.com/search_result.html?search_key=妈妈包')

        # 用户手动操作完成后，开始采集数据
        print("开始采集数据...")

        products = []

        # 使用用户提供的CSS类名查找商品
        title_elements = page.eles('css:.J9WPy2Wu')
        price_elements = page.eles('css:.m9lfFP_K.IkXI5oRB')
        image_elements = page.eles('css:.K5TL3mx3')
        sales_elements = page.eles('css:._6paW_jPc.wiTsvojT')

        print(f"找到标题元素: {len(title_elements)}")
        print(f"找到价格元素: {len(price_elements)}")
        print(f"找到图片元素: {len(image_elements)}")
        print(f"找到销量元素: {len(sales_elements)}")

        # 获取前10个商品
        max_items = min(10, len(title_elements))

        for i in range(max_items):
            product = {}

            # 获取标题
            if i < len(title_elements):
                product['title'] = title_elements[i].text

            # 获取价格
            if i < len(price_elements):
                product['price'] = price_elements[i].text

            # 获取主图
            if i < len(image_elements):
                product['image'] = image_elements[i].attr('src')

            # 获取销量
            if i < len(sales_elements):
                product['sales'] = sales_elements[i].text

            products.append(product)
            print(f"采集第{i+1}个商品: {product.get('title', 'N/A')}")

        # 输出结果
        print("\n采集结果:")
        print(json.dumps(products, ensure_ascii=False, indent=2))

        print("\n数据采集完成！")
        # 保持浏览器打开5秒用于检查
        import time
        time.sleep(5)

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    search_and_collect()
