from DrissionPage import ChromiumPage, ChromiumOptions
import time
import sys

import re
import json

# 设置标准输出编码为 UTF-8，防止表情符号报错解决Windows控制台打印emoji乱码报错问题
sys.stdout.reconfigure(encoding='utf-8')

import database_manager

# ... (之前 imports)

def search_1688():
    # 初始化数据库
    database_manager.init_db()

    # 用户指定的完整搜索连接
    search_url = "https://s.1688.com/selloffer/offer_search.htm?keywords=%E6%89%8B%E6%9C%BA&spm=a26352.13672862.searchbox.0&charset=utf8"
    
    # 移除手动编码逻辑，直接使用该 URL
    print(f"🚀 正在打开搜索页: {search_url}")
    page = ChromiumPage()
    page.get(search_url)
    
    print("⏳ 等待页面和商品列表加载...")
    time.sleep(5) # 简单等待，确保内容渲染
    
    print(f"✅ 连接成功！当前页面: {page.title}")

    try:
        # Define target URLs list
        target_urls = []
        
        print("🔄 正在提取商品数据...")
        
        # Strategy 1: CSS Selector (Original)
        print("🔍 尝试策略 1: CSS 选择器 (.search-offer-wrapper)")
        cards = page.eles('.search-offer-wrapper')
        if cards:
            print(f"✅ 策略 1 (CSS): 找到了 {len(cards)} 个商品卡片。")
            for card in cards:
                # Try to find URL in card
                url = None
                if card.tag == 'a':
                    url = card.link
                else:
                    link_ele = card.ele('tag:a', timeout=0.1)
                    if link_ele:
                        url = link_ele.link
                    else:
                        current = card
                        for _ in range(3):
                            parent = current.parent()
                            if parent:
                                if parent.tag == 'a':
                                    url = parent.link
                                    break
                                current = parent
                            else:
                                break
                if url:
                    target_urls.append(url)

        # Strategy 2: Window Data (JSON)
        if not target_urls:
            print("⚠️ 策略 1 失败，尝试策略 2 (window.data JSON 提取)...")
            try:
                data = page.run_js("return window.data;")
                if data:
                    items = []
                    # Path A: offerV2 -> ... -> items
                    if 'offerV2' in data:
                        items = data['offerV2'].get('response', {}).get('data', {}).get('OFFER', {}).get('items', [])
                    
                    # Path B: offerV2Showed -> offerList
                    if not items and 'offerV2Showed' in data:
                        print("    ℹ️ 使用 offerV2Showed 数据源...")
                        items = data['offerV2Showed'].get('offerList', [])

                    if items:
                        print(f"✅ 策略 2 (JSON): 找到了 {len(items)} 个商品数据。正在尝试按位置排序...")
                        
                        def get_item_pos(it):
                            try:
                                track_info = it.get('trackInfo', {})
                                expo_args = track_info.get('expoArgs', {})
                                ext_data = expo_args.get('ext_expo_data', '')
                                if not ext_data:
                                   ext_data = it.get('dataProcessed', {}).get('trackAttrs', {}).get('data-aplus-report', '')
                                if ext_data:
                                    match = re.search(r'position@(\d+)', ext_data)
                                    if match: return int(match.group(1))
                            except: pass
                            return 9999

                        items.sort(key=get_item_pos)

                        for item in items:
                            pos = get_item_pos(item)
                            print(f"    🔎 分析商品 (位置: {pos if pos != 9999 else '未知'})...")
                            oid = item.get('jumpArgs', {}).get('offerId') or item.get('data', {}).get('offerId') or item.get('offerId')
                            if oid:
                                pc_url = f"https://detail.1688.com/offer/{oid}.html"
                                target_urls.append(pc_url)
            except Exception as e:
                print(f"❌ 策略 2 执行出错: {e}")

        # Strategy 3: Raw Link Scan
        if not target_urls:
            print("⚠️ 策略 2 失败，尝试策略 3 (全页面链接扫描)...")
            all_links = page.ele('tag:body').eles('tag:a')
            seen_urls = set()
            for link in all_links:
                url = link.link
                if url and 'detail.1688.com/offer/' in url:
                    if url not in seen_urls:
                        target_urls.append(url)
                        seen_urls.add(url)
            if target_urls:
                print(f"✅ 策略 3 (链接扫描): 找到了 {len(target_urls)} 个潜在商品链接。")

        # Processing Loop
        if target_urls:
            print(f"\n🎉 找到了 {len(target_urls)} 个商品，准备处理所有商品...")
            print("=" * 80)
            
            for i, url in enumerate(target_urls):
                print(f"\n🚀 [第 {i+1} 个商品] 打开链接: {url} ...")
                new_tab = page.new_tab(url)
                
                try:
                    print("    ⏳ 正在加载详情页...")
                    new_tab.wait.doc_loaded()
                    
                    # 提取 offerId (platform_id)
                    import re
                    offer_id_match = re.search(r'offer/(\d+)\.html', url)
                    platform_id = offer_id_match.group(1) if offer_id_match else None
                    
                    title = new_tab.title
                    
                    # 提取所有信息
                    skus, sku_model, attributes_json, sku_info_json = _extract_product_details(new_tab)
                    attributes_dom, images, reviews = _extract_reviews_from_page(new_tab)
                    
                    # 合并属性 (优先保留格式化好的 JSON 属性，如果为空则使用 DOM 抓取的)                    final_attributes = attributes_json if attributes_json else attributes_dom
                    
                    if final_attributes:
                        print(f"    📝 准备入库属性 {len(final_attributes)} 个: {str(final_attributes)[:100]}...")
                    else:
                        print("    ⚠️ 警告：最终属性列表为空！")
                    
                    # 入库
                    print(f"    💾 正在保存数据到数据库 (goods_id: {platform_id})...")
                    # save_product 更新了参数
                    goods_id = database_manager.save_product(title, url, platform_id, sku_info_json=sku_info_json)
                    
                    # 保存关联数据
                    database_manager.save_full_product_data(
                        goods_id, 
                        platform_id, 
                        skus, 
                        images, 
                        final_attributes, 
                        reviews
                    )

                except Exception as e:
                    print(f"    ❌ 详情页处理出错: {e}")
                finally:
                    print("    ❌ 关闭当前详情页")
                    new_tab.close()
            
            print("=" * 80)
            print("🎉 所有商品采集任务完成！")
        else:
            print("❌ 所有策略均失败，未能找到任何有效商品链接。")
            # Save HTML for debug
            with open('debug_1688.html', 'w', encoding='utf-8') as f:
                f.write(page.html)
            print("💾 已保存页面源码到 debug_1688.html 以供分析。")

    except Exception as e:
        print(f"❌ 程序发生错误: {e}")

def _extract_product_details(tab):
    """提取商品详细信息（SKU、价格、库存）"""
    print("\n    📊 [商品详情提取]")
    try:
        # 尝试从 window.__INIT_DATA 提取
        init_data = tab.run_js("return window.__INIT_DATA;")
        sku_model = None
        
        if init_data:
            # 路径 1: 直接在根目录
            sku_model = init_data.get('skuModel')
            # 路径 2: 在 globalData 中
            if not sku_model:
                sku_model = init_data.get('globalData', {}).get('skuModel')
                
        # Fallback: 手动解析 HTML (当 JS 变量未直接暴露时)
        if not sku_model:
            print("    ⚠️ window.__INIT_DATA 未找到，尝试 HTML 文本解析...")
            html = tab.html
            
            # --- 1. 提取 skuModel ---
            start_marker = '"skuModel":'
            idx = html.find(start_marker)
            if idx != -1:
                start_brace = html.find('{', idx)
                if start_brace != -1:
                    brace_count = 0
                    json_str = ""
                    for i in range(start_brace, len(html)):
                        char = html[i]
                        json_str += char
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                break
                    
                    if json_str:
                        try:
                            sku_model_data = json.loads(json_str)
                            print("    ✅ 成功从 HTML 解析出 SKU 数据")
                            sku_model = sku_model_data
                        except Exception as e:
                            print(f"    ❌ SKU JSON 解析失败: {e}")

            # --- 2. 提取 offerAttribute (商品属性) ---
            # 这是一个数组，所以找 [ ... ]
            attr_marker = '"offerAttribute":'
            idx_attr = html.find(attr_marker)
            offer_attributes = []
            
            if idx_attr != -1:
                start_bracket = html.find('[', idx_attr)
                if start_bracket != -1:
                    bracket_count = 0
                    attr_json_str = ""
                    # 设置一个合理的扫描长度上限，防止死循环
                    for i in range(start_bracket, len(html)):
                        char = html[i]
                        attr_json_str += char
                        if char == '[':
                            bracket_count += 1
                        elif char == ']':
                            bracket_count -= 1
                            if bracket_count == 0:
                                break
                    
                    if attr_json_str:
                        try:
                            offer_attributes = json.loads(attr_json_str)
                            print("    ✅ 成功从 HTML 解析出商品属性数据")
                        except Exception as e:
                            print(f"    ❌ 属性 JSON 解析失败: {e}")

        # --- 输出结果展示 ---
        
        # 展示商品属性
        if offer_attributes:
             print("\n    📝 [商品详细参数]")
             for attr in offer_attributes:
                 # 常见结构 {"name": "品牌", "value": "华为"}
                 name = attr.get('name') or attr.get('propName')
                 value = attr.get('value')
                 if name and value:
                     print(f"      - {name}: {value}")
        
        # 构造统一的 skus 列表
        final_skus = []
        
        # 构造统一的 skus 列表
        final_skus = []
        
        if sku_model:
            # 1. 解析 SKU 属性字典 (构建 valueId -> {prop: "颜色", name: "黑色"} 的映射)
            sku_props = sku_model.get('skuProps', [])


            
            value_id_map = {} # 映射 valueId (str) -> {'prop': propName, 'name': valueName}
            
            if sku_props:
                for prop in sku_props:
                    prop_name = prop.get('prop')
                    fid = prop.get('fid')
                    
                    for v in prop.get('value', []):
                        # valueId 可能是 int 或 str，统一转 str
                        # 注意: 1688 这里的 valueId 很多时候是 imageUrl 这种不一样的结构，
                        # 但通常 v 里面应该有类似 unique id 的字段，或者是 name 本身
                        # 我们先假设 v 里面有 'name'，不确定有没有 id，先看看
                        v_name = v.get('name')
                        # 有些情况 JSON 里没有显示 valueId，如果 skuInfoMap 用的是中文组合作为 key
                        # 那么我们就不需要这个 ID 映射了。
                        # 但如果 skuInfoMap 用的是数字 ID，我们就需要这个映射。
                        # 这里我们只存 name，假设 key 可能是中文
                        if v_name:
                             # 如果未来发现 key 是数字，需要在这里找对应的 ID 字段（如 'valueId' 或 'vid'）
                             # 目前截图显示 key 已经是中文混合了
                             pass

            # 2. 尝试从 skuInfoMap 中提取
            sku_map = sku_model.get('skuInfoMap', {})
            print(f"    🔍 [DEBUG] skuInfoMap 长度: {len(sku_map)}")
            
            # 辅助函数：标准化文本（处理全角符号等）
            def normalize_text(text):
                if not text: return ""
                return text.replace('（', '(').replace('）', ')').replace('＋', '+').strip()

            # 构建属性值到属性名的映射，加速匹配
            name_to_prop = {}
            if sku_props:
                for prop_item in sku_props:
                    p_name = prop_item.get('prop')
                    for val in prop_item.get('value', []):
                        val_name = val.get('name')
                        if val_name:
                            name_to_prop[normalize_text(val_name)] = p_name
                            name_to_prop[val_name] = p_name
            
            print(f"    🔍 [DEBUG] 已构建属性映射表，共 {len(name_to_prop)} 个值")

            for k, v in sku_map.items():
                


                print(f"    🔍 [DEBUG] 处理 SKU Key: {k}")
                # k 的格式通常是 "128GB&gt;蓝色"，需要清洗
                clean_k = k.replace('&gt;', '>').replace(';', '>')
                parts = [p.strip() for p in clean_k.split('>') if p.strip()]
                
                sku_name_parts = []
                current_props = {}
                
                # 遍历 key 的每一部分，匹配属性名
                for part in parts:
                    sku_name_parts.append(part)
                    # 查找 part 属于哪个属性
                    norm_part = normalize_text(part)
                    if norm_part in name_to_prop:
                        prop_key = name_to_prop[norm_part]
                        current_props[prop_key] = part
                    elif part in name_to_prop:
                        prop_key = name_to_prop[part]
                        current_props[prop_key] = part
                    else:
                        # 如果没有匹配到，可能是未列出的属性，暂时忽略或按默认 key 处理
                        pass
                
                # 如果没有解析出任何属性，但 key 确实有内容，使用规格索引兜底
                if not current_props and parts:
                    for i, part in enumerate(parts):
                        current_props[f"规格{i+1}"] = part

                sku_name = " ".join(sku_name_parts)
                props_json_str = json.dumps(current_props, ensure_ascii=False)
                if len(final_skus) < 3:
                     print(f"      -> 原始: {clean_k} => 解析: {props_json_str}")
                
                price = v.get('price') or v.get('discountPrice')
                stock = v.get('canBookCount')
                
                final_skus.append({
                    'spec_id': k,
                    'name': sku_name,
                    'props_json': props_json_str,
                    'price': str(price) if price else None,
                    'stock': str(stock) if stock else None,
                    'info': json.dumps(v, ensure_ascii=False)
                })
        
        # 将原始 SKU Props 转为 JSON 字符串返回 (sku_info_json)
        sku_info_json = json.dumps(sku_model.get('skuProps', []), ensure_ascii=False) if sku_model else None
        
        print(f"    🔍 [DEBUG] _extract_product_details 返回: {len(final_skus)} 个 SKU")
        return final_skus, sku_model, offer_attributes, sku_info_json

    except Exception as e:
        print(f"    ❌ 提取商品详情失败: {e}")
        return [], None, [], None

    except Exception as e:
        print(f"    ❌ 提取商品详情失败: {e}")

def _extract_reviews_from_page(tab_obj):
    """封装的抓取逻辑，传入标签页对象"""
    print(f"    📄 正在抓取详情: {tab_obj.title}")
    
    # --- 1. 抓取商品属性 (基于调试结果: 数据都在 td 或 .offer-attr 中) ---
    print("    🔍 正在提取商品属性...")
    attributes = []
    # 尝试查找包含属性的容器
    # 策略: 查找所有 td，通常是 key-value 相邻
    tds = tab_obj.eles('tag:td')
    if tds:
        # 简单处理：把所有 td 文本收集起来
        # 如果是标准的 key-value 表格，通常是偶数个
        temp_attrs = [td.text.strip() for td in tds if td.text.strip()]
        # 尝试成对打印
        for i in range(0, len(temp_attrs), 2):
            if i+1 < len(temp_attrs):
                key = temp_attrs[i]
                val = temp_attrs[i+1]
                # 过滤掉显然不是属性的短文本或长文本
                if len(key) < 20 and len(val) < 50:
                    attributes.append(f"{key}: {val}")
    
    # 备选: .de-feature 或 .offer-attr
    if not attributes:
        other_eles = tab_obj.eles('.de-feature') or tab_obj.eles('.offer-attr') or tab_obj.eles('.offer-attr-item')
        attributes = [e.text.strip() for e in other_eles if e.text.strip()]

    if attributes:
        print(f"    ✅ 抓取到 {len(attributes)} 个属性:")
        for attr in attributes[:5]: # 只打印前5个
            print(f"      - {attr}")
    else:
        print("    ⚠️ 未找到明显属性信息")

    # --- 1.5 抓取商品主图 ---
    print("    🔍 正在提取商品图片...")
    images = []
    # 常见的图片容器 - 增强版列表
    img_selectors = [
        '.od-gallery-img',          # 常见 PC
    ]
    
    img_eles = []
    for sel in img_selectors:
        found = tab_obj.eles(sel)
        if found:
            img_eles.extend(found)
    
    # 如果以上都没找到，尝试宽泛抓取 class 包含 gallery 的
    if not img_eles:
        all_imgs = tab_obj.eles('tag:img')
        for img in all_imgs:
            cls = img.attr('class') or ""
            if "gallery" in cls or "thumb" in cls:
                img_eles.append(img)
    
    for img in img_eles:
        src = img.attr('src') or img.attr('data-src')
        if src:
            # 简单的清洗，取大图 (去掉尺寸后缀如 .60x60.jpg)
            if '.jpg' in src:
                # 尝试去掉尺寸后缀，还原大图
                # 示例: xxx.jpg_60x60.jpg -> xxx.jpg
                clean_src = src.split('.jpg_')[0] + '.jpg'
                images.append(clean_src)
            else:
                images.append(src)
                
    # 去重
    images = list(set(images))
    if images:
        print(f"    ✅ 抓取到 {len(images)} 张图片")
        for img in images[:3]:
            print(f"      - {img[:60]}...")
    else:
        print("    ⚠️ 未找到商品图片")

    # --- 1.8 抓取 SKU 信息 (价格/库存) ---
    print("    🔍 正在提取 SKU 信息...")
    skus = []
    
    # 尝试找到 SKU 选项容器
    sku_cards = tab_obj.eles('.sku-item-wrapper') or tab_obj.eles('.prop-item')
    
    # 如果是复杂的表格型 SKU (截图右下角显示了 价格/库存)
    # 通常这种需要点击或者直接从 DOM 读取对应的属性
    if not sku_cards:
        # 尝试读取表格行
        sku_rows = tab_obj.eles('.table-sku tr')
        if sku_rows:
            print(f"      发现表格型 SKU，共 {len(sku_rows)} 行")
        else:
            # 尝试通过 SKU 名称列表读取
            sku_names = tab_obj.eles('.sku-name') or tab_obj.eles('.prop-name')
            for name_ele in sku_names:
                name = name_ele.text.strip()
                if name:
                    # 尝试寻找同级或附近的库存/价格信息
                    # 这里可能比较难精准对应，先只存名字
                    skus.append({'name': name})
    
    # 如果找到了 SKU 卡片（如截图中的规格选择框）
    if sku_cards:
        for card in sku_cards:
            name = card.ele('.sku-item-name').text.strip() if card.ele('.sku-item-name') else card.text.strip()
            # 尝试找价格，有时候价格悬浮或者是点击后显示，这里先尽力抓静态文本
            price_guess = ""
            stock_guess = ""
            
            # 有些页面直接在 SKU 旁边显示库存
            sub_text = card.text # 获取整个卡片文本
            if "元" in sub_text or "¥" in sub_text:
                 price_guess = sub_text
            
            if name:
                skus.append({'name': name, 'info': sub_text})

    if skus:
        print(f"    ✅ 抓取到 {len(skus)} 个 SKU 选项")
        for sku in skus[:5]:
            print(f"      - {sku}")
    else:
        print("    ⚠️ 未找到明显 SKU 选项")


    # --- 2. 抓取评价 ---
    print("    🔍 正在提取评价...")
    collected_reviews = []
    try:
        # 点击评价标签
        tab = tab_obj.ele('text:评价', timeout=3) or tab_obj.ele('text:Reviews', timeout=1)
        if tab:
            if 'selected' not in (tab.attr('class') or ''):
                tab.click()
                time.sleep(2)
        else:
            print("    ⚠️ 未找到评价标签，尝试直接抓取")

        # 触发加载
        tab_obj.scroll.down(500)
        time.sleep(1)
        
        review_texts = tab_obj.eles('.content-text')
        
        if review_texts:
            print(f"    ✅ 抓取到 {len(review_texts)} 条评价")
            for j, r in enumerate(review_texts): 
                r_text = r.text.replace('\n', ' ').strip()
                if r_text:
                    collected_reviews.append(r_text)
                    if j < 3: print(f"      - {r_text[:40]}...")
        else:
            print("    ❌ 暂无评价")
            
    except Exception as e:
        print(f"    ❌ 评价抓取出错: {e}")
        
    return attributes, images, collected_reviews

if __name__ == "__main__":
    search_1688()
