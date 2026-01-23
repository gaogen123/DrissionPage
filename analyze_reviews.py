from openai import OpenAI
import database_manager
import os
import math

# DeepSeek API Client Config
client = OpenAI(
    api_key="sk-c190e2d495e942ec83752cc7103ba015",
    base_url="https://api.deepseek.com",
    timeout=120.0 # 设置 2 分钟超时，分批处理应该够了
)

def analyze_batch_reviews(batch_reviews, batch_index, total_batches):
    """
    分析一小批评论，提取关键信息
    """
    reviews_text = "\n".join(batch_reviews)
    prompt = f"""
请阅读以下 {len(batch_reviews)} 条关于【妈咪包/母婴出行包】的用户评论。
请简要提取以下信息（不要长篇大论，用关键词或短语即可）：
1. 用户提到的主要痛点/差评点。
2. 用户喜欢的主要功能/好评点。
3. 提到的典型使用场景或用户身份。

评论内容：
{reviews_text}
    """
    
    try:
        print(f"    🔄 [Batch {batch_index}/{total_batches}] 正在分析 {len(batch_reviews)} 条评论...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"    ⚠️ Batch {batch_index} 分析失败: {e}")
        return ""

def analyze_aggregated_reviews(reviews):
    """
    分批处理并在最后聚合分析所有评论
    """
    if not reviews:
        print("⚠️ 没有评论可供分析")
        return

    print(f"🧠 准备分析 {len(reviews)} 条评论...")
    
    # 1. 分批处理 (每批 100 条)
    BATCH_SIZE = 100
    total_batches = math.ceil(len(reviews) / BATCH_SIZE)
    batch_summaries = []
    
    for i in range(total_batches):
        batch = reviews[i*BATCH_SIZE : (i+1)*BATCH_SIZE]
        summary = analyze_batch_reviews(batch, i+1, total_batches)
        if summary:
            batch_summaries.append(summary)
            
    if not batch_summaries:
        print("❌ 所有批次分析均失败，无法生成总报告")
        return

    # 2. 汇总生成最终报告
    print(f"\n🧠 正在基于 {len(batch_summaries)} 份分批摘要生成最终全量报告...")
    
    combined_summaries = "\n===\n".join(batch_summaries)
    
    final_prompt = f"""
你是一位资深的跨境电商选品专家。我将为你提供几份关于【妈咪包/母婴出行包】的用户评论分析摘要。
这些摘要来自对大量评论的分批处理。
请你综合这些摘要，去除重复信息，进行深度的品类市场分析。

请按以下格式输出最终分析报告：
1. 【市场痛点深挖】：综合所有差评，列出用户最无法忍受的3-5个普遍问题（如拉链易坏、容量虚标、肩带勒肉等）。
2. 【高频好评特征】：用户最在意的爽点是什么？（如分区收纳合理、自重轻、挂车方便等）。
3. 【用户画像与使用场景】：
   - 典型用户是谁？（如新手妈妈、二胎妈妈、背奶职场妈妈）
   - 核心场景有哪些？（如带娃体检、短途旅行、逛街）
4. 【爆品打造建议】：
   - 必备功能：哪些功能是标配，没有就卖不动？
   - 差异化机会：基于痛点，有哪些改进空间可以作为新产品的卖点？
5. 【综合结论】：当前市场竞争焦点在哪里？新产品切入的最佳角度是什么？

分批摘要内容如下：
{combined_summaries}
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": final_prompt},
            ],
            stream=False
        )
        
        result = response.choices[0].message.content
        
        print("\n" + "="*50)
        print(f"📊 【使用分批策略】全量品类分析报告")
        print("="*50)
        print(result)
        print("="*50 + "\n")
        
        # 保存报告
        filename = "report_aggregated_all_v2.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"    ✅ 聚合分析报告已保存: {filename}")
            
    except Exception as e:
        print(f"❌ 最终汇总分析失败: {e}")

def main():
    print("🚀 开始读取数据库中所有评论...")
    
    # 获取所有评论
    all_reviews = database_manager.get_all_reviews()
    
    if not all_reviews:
        print("⚠️ 数据库中没有评论数据，请先运行爬虫脚本采集数据。")
        return
        
    print(f"📚 共找到 {len(all_reviews)} 条评论，准备进行分析...")
    
    # 调用聚合分析
    analyze_aggregated_reviews(all_reviews)

if __name__ == "__main__":
    main()
