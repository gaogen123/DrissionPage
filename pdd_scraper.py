from DrissionPage import ChromiumPage, ChromiumOptions
import json
import time
import sys

def collect_pdd_product_titles(search_keyword="妈妈包", max_items=50):
    """
    采集拼多多商品标题

    Args:
        search_keyword: 搜索关键词
        max_items: 最大采集数量
    """
    # 设置浏览器选项
    co = ChromiumOptions()
    co.set_argument('--no-sandbox')
    co.set_argument('--disable-dev-shm-usage')
    co.set_argument('--disable-blink-features=AutomationControlled')  # 避免检测
    co.set_argument('--disable-web-security')  # 禁用网络安全限制
    co.set_argument('--disable-features=VizDisplayCompositor')  # 禁用可视化合成器
    co.set_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    co.set_argument('--window-size=1200,800')  # 设置窗口大小
    co.set_local_port(9222)
    co.set_browser_path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')
    co.set_retry(times=3, interval=1)  # 设置重试次数和间隔

    # 创建页面对象
    print("正在启动浏览器...")
    page = ChromiumPage(co)

    try:
        print(f"正在搜索关键词: {search_keyword}")
        # 对关键词进行URL编码
        from urllib.parse import quote
        encoded_keyword = quote(search_keyword)
        search_url = f'https://mobile.pinduoduo.com/search_result.html?search_key={encoded_keyword}'

        print(f"访问URL: {search_url}")
        page.get(search_url)

        # 等待页面加载完成 - 使用多种等待策略
        print("等待页面加载...")
        try:
            # 等待页面基本加载完成
            page.wait.load_start(timeout=10)
            # 等待特定的元素出现
            page.wait.ele_displayed('css:body', timeout=15)
            print("页面基本加载完成")
        except Exception as e:
            print(f"等待页面加载超时: {e}")


        titles = []
        collected_count = 0
        scroll_attempts = 0
        max_scroll_attempts = 15
        best_selector = None  # 记录最佳选择器

        # 智能选择器发现
        def find_best_selector():
            """智能发现最适合的商品标题选择器"""
            # 多种可能的CSS选择器，按优先级排序
            candidate_selectors = [
                # 基于文本内容的选择器
                'text^商品',  # 以"商品"开头的文本
                'text^【',     # 以【开头的标题
                'text^爆款',   # 爆款商品
                'text^热销',   # 热销商品

                # 基于属性的选择器
                'css:[data-testid*="title"]',     # 包含title的测试ID
                'css:[aria-label*="商品"]',       # 商品相关aria标签
                'css:[class*="title"]',           # 包含title的class
                'css:[class*="goods"]',           # 包含goods的class
                'css:[class*="product"]',         # 包含product的class
                'css:[class*="item"]',            # 包含item的class

                # 具体的CSS类名
                'css:.goods-title',
                'css:.title',
                'css:.goods-name',
                'css:.item-title',
                'css:.product-title',
                'css:.product-name',
                'css:.item-name',
                'css:.goods-item-title',
                'css:.product-item-title',

                # 移动端常见的类名
                'css:.J9WPy2Wu',      # 从现有代码保留
                'css:._3U6cVd',       # 可能的新类名
                'css:._2W5K1x',       # 可能的新类名
                'css:._1j8EhN',       # 可能的新类名

                # 通用选择器
                'css:h3',             # h3标签
                'css:h4',             # h4标签
                'css:.name',          # 通用name类
                'css:.title-text',    # 标题文本
            ]

            best_score = 0
            best_sel = None
            best_elements = []

            print("正在检测最适合的选择器...")

            for selector in candidate_selectors:
                try:
                    elements = page.eles(selector, timeout=2)
                    if elements and len(elements) > 0:
                        # 计算选择器的评分
                        score = len(elements) * 10  # 基础分数

                        # 检查元素文本质量
                        valid_texts = 0
                        for elem in elements[:10]:  # 只检查前10个
                            text = elem.text.strip()
                            if len(text) > 5 and len(text) < 100:  # 合理长度
                                valid_texts += 1

                        score += valid_texts * 5  # 文本质量加分

                        # 检查是否包含商品相关关键词
                        sample_text = elements[0].text.lower() if elements else ""
                        if any(keyword in sample_text for keyword in ['包', '鞋', '衣', '手机', '电脑']):
                            score += 20  # 商品关键词加分

                        print(f"选择器 '{selector}' -> {len(elements)} 个元素, 评分: {score}")

                        if score > best_score:
                            best_score = score
                            best_sel = selector
                            best_elements = elements

                except Exception as e:
                    continue

            return best_sel, best_elements

        # 首次运行时发现最佳选择器
        if not best_selector:
            best_selector, initial_elements = find_best_selector()
            if best_selector:
                print(f"找到最佳选择器: {best_selector}")
            else:
                print("警告: 未找到合适的商品标题选择器")

        while collected_count < max_items and scroll_attempts < max_scroll_attempts:
            current_titles = []

            # 使用最佳选择器获取标题
            if best_selector:
                try:
                    elements = page.eles(best_selector, timeout=3)
                    if elements:
                        for element in elements:
                            title_text = element.text.strip()
                            # 过滤有效的标题
                            if (title_text and
                                len(title_text) > 2 and
                                len(title_text) < 200 and  # 避免过长文本
                                not title_text.isdigit() and  # 避免纯数字
                                title_text not in titles):  # 避免重复

                                current_titles.append(title_text)

                        print(f"本次找到 {len(current_titles)} 个新标题")
                    else:
                        print("本次未找到标题元素")
                except Exception as e:
                    print(f"获取标题时出错: {e}")
            else:
                # 如果没有最佳选择器，重新尝试发现
                best_selector, elements = find_best_selector()
                if elements:
                    current_titles = [elem.text.strip() for elem in elements
                                    if elem.text.strip() and len(elem.text.strip()) > 2]

            # 如果没找到新标题，尝试滚动页面
            if not current_titles:
                print(f"第 {scroll_attempts + 1} 次尝试未找到新标题，滚动页面...")
                page.scroll.to_bottom()
                time.sleep(2)
                scroll_attempts += 1
                continue

            # 添加新标题到总列表
            for title in current_titles:
                if title not in titles:
                    titles.append(title)
                    collected_count += 1
                    print(f"[{collected_count}] {title}")

                    # 每采集10个标题保存一次进度
                    if collected_count % 10 == 0:
                        progress_result = {
                            "search_keyword": search_keyword,
                            "progress_count": collected_count,
                            "total_expected": max_items,
                            "titles": titles,
                            "timestamp": int(time.time())
                        }
                        progress_filename = f"pdd_progress_{search_keyword}_{int(time.time())}.json"
                        try:
                            with open(progress_filename, 'w', encoding='utf-8') as f:
                                json.dump(progress_result, f, ensure_ascii=False, indent=2)
                            print(f"进度已保存: {progress_filename}")
                        except:
                            pass

                    if collected_count >= max_items:
                        break

            # 如果还有空间，继续滚动加载更多内容
            if collected_count < max_items:
                print("滚动页面加载更多商品...")
                page.scroll.to_bottom()
                time.sleep(2)
                scroll_attempts += 1

        # 输出结果
        print(f"\n成功采集到 {len(titles)} 个商品标题")
        print("\n商品标题列表:")

        result = {
            "search_keyword": search_keyword,
            "total_count": len(titles),
            "titles": titles
        }

        # 保存到文件
        timestamp = int(time.time())
        filename = f"pdd_titles_{search_keyword}_{timestamp}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"结果已保存到文件: {filename}")
        except Exception as save_error:
            print(f"保存文件时出错: {save_error}")
            # 尝试保存到当前目录
            try:
                current_dir_filename = f"titles_{timestamp}.json"
                with open(current_dir_filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"结果已保存到当前目录: {current_dir_filename}")
            except:
                print("无法保存结果文件")

        # 打印前20个标题作为预览
        print("\n前20个标题预览:")
        for i, title in enumerate(titles[:20], 1):
            print(f"{i:2d}. {title}")

        return result

    except KeyboardInterrupt:
        print("\n用户中断操作")
        return None

    except Exception as e:
        print(f"发生错误: {e}")
        print("错误详情:")
        import traceback
        traceback.print_exc()

        # 尝试保存已采集的数据
        if titles:
            try:
                emergency_result = {
                    "search_keyword": search_keyword,
                    "total_count": len(titles),
                    "error_occurred": True,
                    "error_message": str(e),
                    "titles": titles
                }
                emergency_filename = f"pdd_titles_emergency_{search_keyword}_{int(time.time())}.json"
                with open(emergency_filename, 'w', encoding='utf-8') as f:
                    json.dump(emergency_result, f, ensure_ascii=False, indent=2)
                print(f"已保存已采集数据到: {emergency_filename}")
            except:
                print("无法保存紧急数据")

        return None

    finally:
        # 保持浏览器打开一段时间用于检查（如果没有错误）
        if 'result' in locals() and result:
            print("采集完成，浏览器将在5秒后关闭...")
            time.sleep(5)

def main():
    """主函数"""
    print("=" * 60)
    print("拼多多商品标题采集工具 v2.0")
    print("=" * 60)
    print("功能: 自动采集拼多多搜索结果中的商品标题")
    print("特点: 智能选择器识别，自动滚动加载，进度保存")
    print("-" * 60)

    # 解析命令行参数
    search_keyword = "妈妈包"  # 默认值
    max_items = 50  # 默认值

    if len(sys.argv) >= 2:
        search_keyword = sys.argv[1]

    if len(sys.argv) >= 3:
        try:
            max_items = int(sys.argv[2])
            if max_items <= 0:
                max_items = 50
            elif max_items > 500:  # 限制最大数量
                max_items = 500
                print("采集数量已限制为500")
        except ValueError:
            print("采集数量参数无效，使用默认值50")
            max_items = 50

    # 如果没有命令行参数且在交互式环境中，尝试获取用户输入
    if len(sys.argv) == 1 and sys.stdin.isatty():
        try:
            user_keyword = input("请输入搜索关键词 (默认: 妈妈包): ").strip()
            if user_keyword:
                search_keyword = user_keyword

            user_count = input("请输入采集数量 (默认: 50): ").strip()
            if user_count:
                try:
                    max_items = int(user_count)
                    if max_items <= 0:
                        max_items = 50
                    elif max_items > 500:
                        max_items = 500
                        print("采集数量已限制为500")
                except ValueError:
                    print("输入无效，使用默认采集数量50")

        except (KeyboardInterrupt, EOFError):
            print("\n使用默认参数继续...")
    else:
        print("使用默认参数运行...")

    print("\n配置:")
    print(f"  搜索关键词: {search_keyword}")
    print(f"  采集数量: {max_items}")
    print("-" * 60)

    # 开始采集
    start_time = time.time()
    result = collect_pdd_product_titles(search_keyword, max_items)
    end_time = time.time()

    print("\n" + "=" * 60)
    if result:
        elapsed_time = end_time - start_time
        print(f"采集完成！用时: {elapsed_time:.1f}秒")
        print(f"共获取 {result['total_count']} 个商品标题")
        print(f"采集速度: {result['total_count']/elapsed_time:.1f} 个/秒")
        if result['total_count'] > 0:
            print(f"采集效率: {result['total_count']/elapsed_time:.1f} 个/秒")
    else:
        print("采集失败，请检查错误信息")
    print("=" * 60)

if __name__ == "__main__":
    main()