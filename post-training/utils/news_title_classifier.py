#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import random
from pathlib import Path
import logging
import time
import sys
from openai import OpenAI

# 获取项目根目录
project_root = Path(__file__).resolve().parents[2]

# 获取脚本名称（不含扩展名）用于日志文件
script_name = Path(__file__).stem

# 创建日志目录
log_dir = project_root / 'post-training' / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

# 配置日志输出到文件和控制台
log_file = log_dir / f"{script_name}.log"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('batch_processor')

# 记录脚本启动信息
logger.info(f"================ 脚本开始执行 ({script_name}) ================")
logger.info(f"日志文件路径: {log_file}")

# 设置OpenAI客户端
client = OpenAI(
    base_url="https://chat.cquservice.top/v1",
    api_key="E4jS7Z_8EMpnXZMl4tfcV0VOhA5xkowVK6LZbYJzAcXDq",
)

def classify_titles_batch(titles, batch_number, total_batches):
    """
    使用AI对一批标题进行分类并生成额外的标题来平衡类别
    """
    prompt = """请将以下新闻标题分类为'technology'或'economy'，并完成以下任务：
1. 为每个提供的标题分配分类
2. 分析当前批次中两个类别的数量差异
3. 额外生成5个新闻标题，使两个类别的总数尽量平衡，注意，新生成的新闻标题没有时效要求，但要确保生成的新闻标题以及对应的类别质量优秀。

只返回JSON格式的结果，格式为：
{
  "results": [
    {
      "title": "原始标题1",
      "label": "分类1"
    },
    ...
  ],
  "generated_titles": [
    {
      "title": "生成的标题1",
      "label": "分类1"
    },
    ...
  ]
}

以下是需要分类的标题：\n\n"""
    
    for title in titles:
        prompt += f"- {title}\n"
    
    logger.info(f"正在处理第 {batch_number}/{total_batches} 批 (共{len(titles)}个标题)")
    logger.info(f"当前处理的标题: {titles}")
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的新闻分类与生成助手，擅长将新闻标题分类为技术类或经济类，并能根据需要生成平衡的新标题。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        response_text = completion.choices[0].message.content
        logger.info(f"API响应: {response_text}")
        
        # 尝试解析JSON响应
        try:
            # 提取JSON部分（防止模型返回额外的文本）
            import re
            json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                parsed_result = json.loads(json_str)
                
                # 合并结果
                results = parsed_result.get('results', [])
                generated_titles = parsed_result.get('generated_titles', [])
                
                # 日志记录生成的标题
                logger.info(f"模型生成的额外标题: {generated_titles}")
                
                # 添加标记以区分原始和生成的标题
                for item in results:
                    item['is_generated'] = False
                
                for item in generated_titles:
                    item['is_generated'] = True
                
                # 返回合并后的结果
                return results + generated_titles
            else:
                logger.error(f"无法从响应中提取JSON: {response_text}")
                return []
        except Exception as e:
            logger.error(f"解析JSON响应出错: {e}")
            logger.error(f"原始响应: {response_text}")
            return []
    
    except Exception as e:
        logger.error(f"API请求出错: {e}")
        return []

def process_titles_in_batches():
    """读取标题文件，每次处理5个标题，打上标签并存储结果"""
    # 文件路径
    input_file = project_root / 'post-training' / 'dataset' / 'news_titles_20250414.txt'
    output_file = project_root / 'post-training' / 'dataset' / 'processed_titles_20250414.json'
    
    logger.info(f"输入文件: {input_file}")
    logger.info(f"输出文件: {output_file}")
    
    # 读取所有标题
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            all_titles = [line.strip() for line in f if line.strip()]
        
        total_titles = len(all_titles)
        logger.info(f"共读取到 {total_titles} 个标题")
        
        # 计算需要处理的批次数
        batch_size = 5
        total_batches = (total_titles + batch_size - 1) // batch_size
        
        # 存储所有处理结果（包括原始和生成的标题）
        all_results = []
        
        # 按批次处理数据
        for batch_idx in range(total_batches):
            # 获取当前批次的标题
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, total_titles)
            current_batch = all_titles[start_idx:end_idx]
            
            # 记录分隔符，使日志更清晰
            logger.info(f"-------- 批次 {batch_idx+1}/{total_batches} 开始处理 --------")
            
            # 处理当前批次
            batch_results = classify_titles_batch(current_batch, batch_idx + 1, total_batches)
            
            # 将结果分为原始和生成的（仅用于统计）
            original_results = [item for item in batch_results if not item.get('is_generated', False)]
            gen_titles = [item for item in batch_results if item.get('is_generated', True)]
            
            # 添加到总结果
            all_results.extend(batch_results)
            
            # 每处理1个批次保存一次中间结果，方便断点续传
            if (batch_idx + 1) % 1 == 0 or batch_idx == total_batches - 1:
                # 保存所有结果到同一个文件
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({'data': all_results}, f, ensure_ascii=False, indent=2)
                    
                # 统计当前总体结果
                total_original = sum(1 for item in all_results if not item.get('is_generated', False))
                total_generated = sum(1 for item in all_results if item.get('is_generated', False))
                
                logger.info(f"已处理 {min(end_idx, total_titles)}/{total_titles} 个标题，中间结果已保存")
                logger.info(f"当前已处理 {total_original} 个原始标题和 {total_generated} 个生成标题")
            
            # 显示进度
            progress_percent = min(end_idx, total_titles)/total_titles*100
            logger.info(f"处理进度: {min(end_idx, total_titles)}/{total_titles} ({progress_percent:.2f}%)")
            
            # 记录当前批次的统计信息
            tech_count_batch_orig = sum(1 for item in original_results if item.get('label') == 'technology')
            econ_count_batch_orig = sum(1 for item in original_results if item.get('label') == 'economy')
            tech_count_batch_gen = sum(1 for item in gen_titles if item.get('label') == 'technology')
            econ_count_batch_gen = sum(1 for item in gen_titles if item.get('label') == 'economy')
            
            logger.info(f"本批次原始标题 - 技术类: {tech_count_batch_orig}, 经济类: {econ_count_batch_orig}")
            logger.info(f"本批次生成标题 - 技术类: {tech_count_batch_gen}, 经济类: {econ_count_batch_gen}")
            logger.info(f"-------- 批次 {batch_idx+1}/{total_batches} 处理完成 --------")
            
            # 避免API请求过于频繁
            time.sleep(1)
        
        # 最终保存
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({'data': all_results}, f, ensure_ascii=False, indent=2)
        
        # 统计结果
        original_titles = [item for item in all_results if not item.get('is_generated', False)]
        generated_titles = [item for item in all_results if item.get('is_generated', False)]
        
        tech_count_orig = sum(1 for item in original_titles if item.get('label') == 'technology')
        econ_count_orig = sum(1 for item in original_titles if item.get('label') == 'economy')
        
        tech_count_gen = sum(1 for item in generated_titles if item.get('label') == 'technology')
        econ_count_gen = sum(1 for item in generated_titles if item.get('label') == 'economy')
        
        logger.info(f"================ 最终统计 ================")
        logger.info(f"处理完成！共处理 {len(original_titles)} 个原始标题和 {len(generated_titles)} 个生成标题")
        logger.info(f"原始标题 - 技术类: {tech_count_orig}, 经济类: {econ_count_orig}")
        logger.info(f"生成标题 - 技术类: {tech_count_gen}, 经济类: {econ_count_gen}")
        logger.info(f"总计 - 技术类: {tech_count_orig + tech_count_gen}, 经济类: {econ_count_orig + econ_count_gen}")
        logger.info(f"结果已保存到: {output_file}")
        
    except Exception as e:
        logger.error(f"处理文件时出错: {e}")
        logger.exception(e)

def main():
    logger.info("开始处理新闻标题...")
    
    # 使用API进行分类
    process_titles_in_batches()
    
    logger.info("处理完成")
    logger.info(f"================ 脚本执行结束 ================")

if __name__ == "__main__":
    main() 