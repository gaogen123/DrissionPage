# -*- coding:utf-8 -*-
"""
检查页面元素结构
"""
from DrissionPage import ChromiumPage

# 连接到浏览器
page = ChromiumPage()

print("=" * 60)
print(f"当前页面：{page.title}")
print(f"当前 URL：{page.url}")
print("=" * 60)

# 尝试多种选择器查找商品元素
print("\n尝试查找商品元素...")

# 方法1：通过 class 名称
selectors = [
    '.offer-title-row',
    '.title',
    '.mojar-element-title',
    '.organic-list-offer',
    'tag:a@@text:包',
    '.card-info',
    '.offer-title',
]

for selector in selectors:
    elements = page.eles(selector)
    if elements:
        print(f"\n✅ 找到元素：{selector}")
        print(f"   数量：{len(elements)}")
        if len(elements) > 0:
            print(f"   第一个元素文本：{elements[0].text[:50]}...")
            print(f"   元素标签：{elements[0].tag}")
            if elements[0].attrs:
                print(f"   元素class：{elements[0].attr('class')}")
    else:
        print(f"❌ 未找到：{selector}")

# 获取页面 HTML 片段，查看结构
print("\n" + "=" * 60)
print("页面主要容器元素：")
containers = page.eles('tag:div@@class^=')
if containers:
    # 显示前10个主要div的class
    for i, container in enumerate(containers[:15]):
        class_name = container.attr('class')
        if class_name and len(class_name) > 5:
            print(f"{i+1}. class=\"{class_name[:80]}\"")
