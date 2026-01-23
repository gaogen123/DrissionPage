from DrissionPage import ChromiumPage
import time
import database_manager
import analyze_reviews
import os

def crawl_to_db():
    # 初始化数据库
    database_manager.init_db()

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
    
    if product_cards:
        print(f"🎉 识别到 {len(product_cards)} 个可能的商品，准备采集前 20 个...")
        
        # 采集前 20 个商品 (如果不足 20 个则采集所有)
        target_count = 20
        count_to_crawl = min(len(product_cards), target_count)
        
        for i in range(count_to_crawl):
            print(f"\n🚀 [第 {i+1} 个商品] 准备处理...")
            
            try:
                # 重新获取卡片列表（因为DOM更新）
                current_cards = page.eles('._3glhOBhU')
                if not current_cards or i >= len(current_cards):
                    print(f"    ⚠️ 无法获取第 {i+1} 个卡片")
                    break
                
                card = current_cards[i]
                current_url = page.url
                
                # 点击进入详情
                card.click()
                time.sleep(3) 
                
                if page.url == current_url:
                    print("    ⚠️ 点击未跳转")
                    continue
                    
                print(f"    📄 进入详情页: {page.title[:20]}...")
                
                # 获取标题
                title_ele = page.ele('.Vrv3bF_E', timeout=5)
                title = title_ele.text if title_ele else "未知商品"
                print(f"    📌 [商品标题]: {title}")
                
                # 解析 platform_goods_id
                from urllib.parse import urlparse, parse_qs
                parsed_url = urlparse(page.url)
                query_params = parse_qs(parsed_url.query)
                platform_id = query_params.get('goods_id', [None])[0]
                if platform_id:
                    print(f"    🆔 [商品ID]: {platform_id}")
                else:
                    print(f"    ⚠️ 未从URL解析到 goods_id")
                
                # 尝试点击“查看更多评价”
                print("    👉 尝试点击“查看全部评价”...")
                view_more_btn = page.ele('.IpR_6z4r')
                has_clicked_reviews = False
                
                if view_more_btn:
                    view_more_btn.click()
                    time.sleep(2)
                    print("    📄 已进入评价列表页")
                    has_clicked_reviews = True
                else:
                    print("    ⚠️ 未找到“查看全部评价”按钮，仅抓取当前页评价")
                    page.scroll.down(300)

                # --- 无论是否有评论，先保存商品信息 ---
                print(f"    💾 保存商品信息: {title[:20]}...")
                goods_id = database_manager.save_product(title, page.url, platform_id)
                
                # 收集评论
                collected_reviews = []
                
                if has_clicked_reviews:
                    print("    🔄 正在滚动加载更多评论 (最大 20 次)...")
                    for _ in range(20): 
                        page.scroll.down(1000)
                        time.sleep(0.5)
                    
                    reviews_elements = page.eles('.QznBag3Z')
                else:
                    reviews_elements = page.eles('.BMUTYZnz')
                
                if reviews_elements:
                    print(f"    ✅ 抓取到 {len(reviews_elements)} 条评论，正在提取文本...")
                    for r in reviews_elements:
                        text = r.text.replace('\n', ' ').strip()
                        if text:
                            collected_reviews.append(text)
                            
                    if collected_reviews:
                        # 过滤无效评论
                        filtered_reviews = [
                            r for r in collected_reviews 
                            if "该用户觉得商品很好，给出了5星好评" not in r and len(r) > 2
                        ]
                        
                        if filtered_reviews:
                            # 保存评论
                            database_manager.save_reviews(goods_id, filtered_reviews, platform_id)
                            print(f"    ✅ 实际入库: {len(filtered_reviews)} 条 (已过滤无效评论)")
                        else:
                            print("    ⚠️ 经过过滤后无有效评论")
                    else:
                        print("    ⚠️ 虽找到元素但无文本内容")
                else:
                    print(f"    ❌ 未找到评论")
                
                # 后退
                print("    🔙 后退...")
                page.back()
                if has_clicked_reviews:
                    time.sleep(1)
                    page.back()
                
                time.sleep(3) # 等待搜索页重新渲染
                
            except Exception as e:
                print(f"    ❌ 操作失败: {e}")
                if "search_result" not in page.url:
                    page.back()
                    time.sleep(3)
    
    # 采集完成，启动分析
    print("\n" + "="*50)
    print("🎉 采集任务完成，即将开始 DeepSeek 聚合分析...")
    print("="*50 + "\n")
    analyze_reviews.main()

if __name__ == "__main__":
    crawl_to_db()
