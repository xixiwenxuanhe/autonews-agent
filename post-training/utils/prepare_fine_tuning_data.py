#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
将分类好的新闻标题JSON文件转换为适合模型微调的数据格式
"""

import json
import random
import argparse
from pathlib import Path
import logging
import sys
import os

# 获取脚本名称（不含扩展名）
script_name = os.path.splitext(os.path.basename(__file__))[0]

# 获取项目根目录
try:
    project_root = Path(__file__).resolve().parents[2]
except:
    project_root = Path.cwd()

# 创建日志目录
log_dir = project_root / 'post-training' / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

# 配置日志文件
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
logger = logging.getLogger('data_preparator')

# 记录脚本启动信息
logger.info(f"================ 脚本开始执行 ({script_name}) ================")
logger.info(f"日志文件路径: {log_file}")

def load_processed_titles(input_file):
    """加载处理好的标题数据"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('data', [])
    except Exception as e:
        logger.error(f"读取文件出错: {e}")
        return []

def create_instruction_data(titles_data, output_format='jsonl'):
    """将标题数据转换为指令格式的训练数据"""
    instruction_data = []
    for item in titles_data:
        title = item.get('title', '')
        label = item.get('label', '')
        
        if not title or not label:
            continue
            
        # 创建指令格式数据 - 使用单引号和双引号搭配
        conversation = {
            "messages": [
                {"role": "user", "content": f'分类新闻标题："{title}"'},
                {"role": "assistant", "content": label}
            ]
        }
        
        instruction_data.append(conversation)
    
    return instruction_data

def save_training_data(data, output_file, format='jsonl'):
    """保存训练数据到文件"""
    try:
        if format == 'jsonl':
            with open(output_file, 'w', encoding='utf-8') as f:
                for item in data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
        else:  # 保存为单个JSON文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        logger.info(f"训练数据已保存到: {output_file}")
    except Exception as e:
        logger.error(f"保存文件出错: {e}")

def split_train_val(data, val_ratio=0.1):
    """将数据集分割为训练集和验证集"""
    random.shuffle(data)
    split_idx = int(len(data) * (1 - val_ratio))
    return data[:split_idx], data[split_idx:]

def main():
    parser = argparse.ArgumentParser(description='将分类JSON转换为微调训练数据')
    parser.add_argument('--input', '-i', type=str, 
                        default='autonews-agent/post-training/dataset/processed_titles_20250414.json',
                        help='输入的分类JSON文件路径')
    parser.add_argument('--output_dir', '-o', type=str, 
                        default='autonews-agent/post-training/dataset',
                        help='输出训练数据的目录')
    parser.add_argument('--format', '-f', type=str, choices=['jsonl', 'json'], 
                        default='jsonl',
                        help='输出文件格式，jsonl或json')
    parser.add_argument('--val_ratio', '-v', type=float, default=0.1,
                        help='验证集比例，默认0.1')
    parser.add_argument('--exclude_generated', '-e', action='store_true',
                        help='是否排除生成的数据')
    
    args = parser.parse_args()
    
    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 加载数据
    logger.info(f"正在加载数据: {args.input}")
    titles_data = load_processed_titles(args.input)
    
    if not titles_data:
        logger.error("没有找到有效数据!")
        return
    
    logger.info(f"共加载 {len(titles_data)} 条数据")
    
    # 根据设置筛选数据 - 默认包含所有数据
    if args.exclude_generated:
        original_count = len(titles_data)
        titles_data = [item for item in titles_data if not item.get('is_generated', False)]
        filtered_count = original_count - len(titles_data)
        logger.info(f"已过滤 {filtered_count} 条生成数据，剩余 {len(titles_data)} 条真实数据")
    else:
        # 可以选择移除is_generated字段，保持数据干净
        for item in titles_data:
            if 'is_generated' in item:
                del item['is_generated']
        logger.info(f"使用全部 {len(titles_data)} 条数据（包含原始和生成的标题）")
    
    # 创建指令格式的数据
    instruction_data = create_instruction_data(titles_data, args.format)
    
    # 分割训练集和验证集
    train_data, val_data = split_train_val(instruction_data, args.val_ratio)
    
    # 保存数据
    train_file = output_dir / f"train.{args.format}"
    val_file = output_dir / f"val.{args.format}"
    save_training_data(train_data, train_file, args.format)
    save_training_data(val_data, val_file, args.format)
    
    logger.info(f"已分割数据：训练集 {len(train_data)} 条，验证集 {len(val_data)} 条")
    logger.info("数据准备完成！")
    logger.info(f"================ 脚本执行结束 ================")

if __name__ == "__main__":
    main()