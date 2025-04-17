#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
从验证集中提取新闻标题和对应的类别，生成简化的数据集用于模型评估。
提取的格式为：
{
    "title": "新闻标题",
    "category": "technology或economy"
}
"""

import os
import json
import argparse
import re

def extract_title_from_prompt(prompt):
    """从用户提示中提取新闻标题"""
    # 尝试匹配引号内的标题
    match = re.search(r'[:：][\s]*[\"\'""「](.+?)[\""」\'"]', prompt)
    if match:
        return match.group(1)
    
    # 如果没有引号，尝试直接提取冒号后的内容
    match = re.search(r'[:：][\s]*(.+)', prompt)
    if match:
        return match.group(1).strip()
    
    # 如果以上方法都失败，返回整个提示
    return prompt

def extract_data(input_file, output_file):
    """从JSONL文件中提取标题和类别信息"""
    data = []
    
    # 读取输入文件
    with open(input_file, 'r', encoding='utf-8') as f:
        line_count = 0
        for line in f:
            try:
                line_count += 1
                item = json.loads(line)
                
                # 提取用户输入和助手回复
                user_msg = ""
                category = ""
                
                for msg in item["messages"]:
                    if msg["role"] == "user":
                        user_msg = msg["content"]
                    elif msg["role"] == "assistant":
                        category = msg["content"].strip().lower()
                
                # 从用户消息中提取标题
                title = extract_title_from_prompt(user_msg)
                
                # 验证类别是否有效
                if category not in ["technology", "economy"]:
                    print(f"警告: 行 {line_count} 的类别 '{category}' 不是预期的值")
                
                # 添加到结果列表
                data.append({
                    "title": title,
                    "category": category
                })
                
            except json.JSONDecodeError:
                print(f"警告: 无法解析第 {line_count} 行")
    
    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"处理完成，共提取了 {len(data)} 条数据，保存到 {output_file}")
    return data

def stats_on_data(data):
    """统计数据集中的类别分布"""
    categories = {}
    for item in data:
        cat = item["category"]
        if cat in categories:
            categories[cat] += 1
        else:
            categories[cat] = 1
    
    print("\n类别分布:")
    for cat, count in categories.items():
        print(f"  - {cat}: {count} ({count/len(data)*100:.2f}%)")
    
    # 打印几个示例
    print("\n示例:")
    for i, item in enumerate(data[:5]):
        print(f"  {i+1}. 标题: {item['title']}")
        print(f"     类别: {item['category']}")
        print()

def main():
    parser = argparse.ArgumentParser(description="从验证集提取新闻标题和类别，生成简化数据集")
    parser.add_argument("--input", type=str, default="autonews-agent/post-training/dataset/val.jsonl",
                       help="输入的JSONL文件")
    parser.add_argument("--output", type=str, default="autonews-agent/post-training/dataset/inference.json",
                        help="输出的JSON文件")
    
    args = parser.parse_args()
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # 提取数据
    data = extract_data(args.input, args.output)
    
    # 显示统计信息
    stats_on_data(data)
    
    # 创建TSV格式版本，便于查看和编辑
    tsv_output = args.output.replace('.json', '.tsv')
    with open(tsv_output, 'w', encoding='utf-8') as f:
        f.write("title\tcategory\n")  # 表头
        for item in data:
            # 处理标题中可能存在的制表符
            clean_title = item["title"].replace('\t', ' ')
            f.write(f"{clean_title}\t{item['category']}\n")
    
    print(f"同时生成了TSV格式文件: {tsv_output}")

if __name__ == "__main__":
    main() 