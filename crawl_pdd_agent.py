from DrissionPage import ChromiumPage
import time

def crawl_pdd():
    # 用户提供的拼多多搜索链接
    url = "https://mobile.pinduoduo.com/search_result.html?search_key=%E5%A6%88%E5%92%AA%E5%8C%85&search_type=goods&source=index&options=3&search_met_track=manual&refer_page_el_sn=99884&refer_page_name=search_result&refer_page_id=10015_1768376320960_usqkfxqhwf&refer_page_sn=10015"
    
    page = ChromiumPage()
    print(f"🚀 正在打开拼多多搜索页...")
    page.get(url)
    
    print("⏳ 等待页面加载...")
    time.sleep(3)
    
    # 尝试定位商品列表
    print("🔄 正在分析商品列表...")
    
    # 使用用户提供的列表 class: _3glhOBhU
    product_cards = page.eles('._3glhOBhU')
    
    # 过滤掉无效或隐藏的卡片（没有 rect 的）
    valid_cards = []
    if product_cards:
        for card in product_cards:
            try:
                if card.rect.size[0] > 0 and card.rect.size[1] > 0:
                    valid_cards.append(card)
            except:
                pass
    product_cards = valid_cards

    if not product_cards:
        print("⚠️ 未找到 class 为 '_3glhOBhU' 的元素，尝试模糊查找或通用策略...")
        # 备用：有时候 class 是动态生成的，可能需要部分匹配或者找图片
        candidates = page.eles('tag:img')
        for img in candidates:
            try:
                if img.rect.size[0] > 50 and img.rect.size[1] > 50:
                    card = img.parent(2)
                    if card:
                        product_cards.append(card)
            except:
                pass

        # 去重并排序
        product_cards = list(set(product_cards)) if isinstance(product_cards, list) else list(product_cards)
        
        # 安全排序
        try:
            product_cards.sort(key=lambda x: x.rect.top)
        except:
            pass # 排序失败不影响使用

    if product_cards:
        print(f"🎉 识别到 {len(product_cards)} 个可能的商品，准备采集前 5 个...")
        
    if product_cards:
        print(f"🎉 识别到 {len(product_cards)} 个可能的商品，准备采集前 5 个...")
        
        # 只取前 2 个
        # ⚠️ 注意：由于我们要点击-后退，页面 DOM 会刷新，导致之前的 card 元素失效
        # 所以必须在每次循环时重新获取列表
        
        for i in range(2):
            print(f"\n🚀 [第 {i+1} 个商品] 准备处理...")
            
            try:
                # 重新获取卡片列表
                # 页面可能需要重新滚动加载
                # 简单的处理：每次都重新找一次
                current_cards = page.eles('._3glhOBhU')
                if not current_cards or i >= len(current_cards):
                    print("    ⚠️ 无法获取第 {i+1} 个卡片（可能数量不足或加载失败）")
                    break
                
                card = current_cards[i]
                
                # --- 在搜索页提取价格 (用户提供 class: _3_U04GgA) ---
                list_price = "未知"
                p_ele = card.ele('._3_U04GgA')
                if p_ele:
                    list_price = p_ele.text
                
                print(f"    💰 列表页价格: {list_price}")
                
                # 记录 URL
                current_url = page.url
                
                # 点击
                card.click()
                time.sleep(3) 
                
                if page.url == current_url:
                    print("    ⚠️ 点击未跳转")
                    continue
                    
                print(f"    📄 进入详情页: {page.title[:20]}...")
                
                # --- 提取数据 ---
                # 1. 标题
                print("    🔍 正在查找标题 (class: Vrv3bF_E)...")
                title_ele = page.ele('.Vrv3bF_E', timeout=5)
                title = title_ele.text if title_ele else "⚠️ 未找到标题元素"
                print(f"    📌 [商品标题]: {title}")
                
                # 1.5. 价格 (用户提供 class: kxqW0mMz)
                print("    🔍 正在查找价格 (class: kxqW0mMz)...")
                price_ele = page.ele('.kxqW0mMz', timeout=2)
                price = price_ele.text if price_ele else "⚠️ 未找到价格元素"
                print(f"    💰 [商品价格]: {price}")

                # 1.6. 商品详情 (用户提供 class: jvsKAdEs)
                print("    🔍 正在查找商品详情 (class: jvsKAdEs)...")
                detail_ele = page.ele('.jvsKAdEs', timeout=2)
                
                if detail_ele:
                    raw_text = detail_ele.text
                    # 分割并去除空行
                    parts = [p.strip() for p in raw_text.split('\n') if p.strip()]
                    formatted_pairs = []
                    
                    # 两两一组组成 键:值
                    for k in range(0, len(parts) - 1, 2):
                        formatted_pairs.append(f"{parts[k]}:{parts[k+1]}")
                    
                    detail_str = " ".join(formatted_pairs)
                    print(f"    📝 [商品详情]: {detail_str}")
                else:
                    print("    ⚠️ 未找到商品详情元素")
                
                # 2. 图片 (用户提供 class: PPuOGFfM)
                # 提取所有展示图片
                print("    🖼️ 正在提取并下载所有展示图片...")
                img_containers = page.eles('.PPuOGFfM')
                
                if img_containers:
                    print(f"      📸 找到 {len(img_containers)} 张图片候选...")
                    
                    import os
                    if not os.path.exists('pdd_images'):
                        os.makedirs('pdd_images')
                        
                    import requests
                    
                    for idx, img_container in enumerate(img_containers):
                        img_ele = img_container.ele('tag:img')
                        if img_ele:
                            try:
                                # 尝试获取链接，处理懒加载
                                img_url = img_ele.link
                                if not img_url:
                                    img_url = img_ele.attr('data-src') or img_ele.attr('data-url')
                                
                                if img_url:
                                    # 清理 url 也是个好习惯 (比如去除多余参数，或者补全协议)
                                    if img_url.startswith('//'):
                                        img_url = 'https:' + img_url
                                        
                                    # 保存名字：product_{i+1}_{idx}.jpg
                                    save_path = f"pdd_images/product_{i+1}_{idx}.jpg"
                                    
                                    # 如果存在同名文件夹，先删除
                                    if os.path.isdir(save_path):
                                        import shutil
                                        try:
                                            # 尝试删除文件夹
                                            shutil.rmtree(save_path)
                                            print(f"      🗑️ 已删除冲突的文件夹: {save_path}")
                                        except Exception as ignored:
                                            print(f"      ⚠️ 删除文件夹失败: {ignored}")

                                    # 使用 requests 下载，完全控制文件名
                                    try:
                                        res = requests.get(img_url, timeout=10)
                                        if res.status_code == 200:
                                            with open(save_path, 'wb') as f:
                                                f.write(res.content)
                                            print(f"      ✅ 图片 [{idx+1}] 已保存: {save_path}")
                                        else:
                                            print(f"      ❌ 图片 [{idx+1}] 下载失败，状态码: {res.status_code}")
                                    except Exception as e:
                                        print(f"      ❌ 图片请求出错: {e}")

                                else:
                                    print(f"      ⚠️ 图片 [{idx+1}] 无有效 URL (可能未加载)")
                            except Exception as e:
                                print(f"      ❌ 图片处理异常: {e}")
                else:
                    print("      ⚠️ 未找到图片容器 (.PPuOGFfM)")

                
                # 尝试点击“查看更多评价” (class: IpR_6z4r)
                print("    👉 尝试点击“查看全部评价”...")
                view_more_btn = page.ele('.IpR_6z4r')
                has_clicked_reviews = False
                
                if view_more_btn:
                    view_more_btn.click()
                    time.sleep(2) # 等待评价列表页加载
                    print("    📄 已进入评价列表页")
                    has_clicked_reviews = True
                else:
                    print("    ⚠️ 未找到“查看全部评价”按钮，仅抓取当前页评价")
                    page.scroll.down(300)
                
                # 滚动加载更多
                if has_clicked_reviews:
                    print("    🔄 正在滚动加载更多评论 (最大 20 次)...")
                    # 滚动多次以加载更多
                    for _ in range(20): 
                        page.scroll.down(1000)
                        time.sleep(0.5)
                    
                    # 用户指定全部评论页面的 class: QznBag3Z
                    reviews = page.eles('.QznBag3Z')
                else:
                    reviews = page.eles('.BMUTYZnz')
                
                print(f"    📌 标题: {title}")
                
                if reviews:
                    print(f"    ✅ 抓取到 {len(reviews)} 条评论：")
                    for r in reviews: # 打印全部
                        print(f"      - {r.text.replace('\n', ' ')[:40]}...")
                else:
                    print(f"    ❌ 未找到评论 (尝试过的 class: {'.QznBag3Z' if has_clicked_reviews else '.BMUTYZnz'})")
                
                # --- 后退 ---
                print("    🔙 后退...")
                page.back()
                
                # 如果点过“查看全部”，需要再次后退
                if has_clicked_reviews:
                    print("    🔙 再次后退(退出评价页)...")
                    time.sleep(1)
                    page.back()
                
                time.sleep(3) # 等待搜索页重新渲染
                
            except Exception as e:
                print(f"    ❌ 操作失败: {e}")
                # 尝试恢复
                if "search_result" not in page.url:
                    page.back()
                    time.sleep(3)
                    
    else:
        print("❌ 未能在搜索页找到可点击的商品元素。")

if __name__ == "__main__":
    crawl_pdd()
