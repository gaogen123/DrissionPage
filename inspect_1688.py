from DrissionPage import ChromiumPage

def inspect_page():
    page = ChromiumPage()
    print(f"当前页面: {page.title}")
    
    # 打印前 5000 个字符的 HTML Body，让我看看结构
    # 或者打印所有包含 'title' 或 'offer' 的 class 名
    
    print("正在搜集页面上的 class ...")
    
    # 查找所有 div
    divs = page.eles('tag:div')
    seen_classes = set()
    for d in divs:
         cls = d.attr('class')
         if cls:
             for c in cls.split():
                 if 'offer' in c or 'item' in c or 'card' in c:
                    seen_classes.add(c)
    
    print("可能的商品卡片 class:")
    print(list(seen_classes))
    
    # 也可以直接保存一份 HTML 让我分析
    with open('debug_page.html', 'w', encoding='utf-8') as f:
        f.write(page.html)
        print("页面 HTML 已保存的 debug_page.html")

if __name__ == "__main__":
    inspect_page()
