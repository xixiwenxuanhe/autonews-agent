#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版测试脚本：支持单个测试和批量测试
"""

import json
import requests
import re
import threading
import os
import sys

# 分类提示模板
CLASSIFICATION_PROMPT = """你是一个新闻分类助手。你的任务是将新闻标题分类为"economy"（经济）或"technology"（技术）类别。

规则：
1. 你必须只输出一个单词作为答案："economy"或"technology"
2. 不要输出任何解释、标点符号或其他文字
3. 不要重复标题或添加任何前缀

示例问答对：
用户："從公視《極樂世界3》談失智症：從日常生活的細節中，該如何照顧與陪伴患者？"
助手：economy

用户："智能医疗辅助诊断：深度解析与实战教程 - TechSynapse"
助手：technology

用户："New Advances in Robotics Could Transform Manufacturing Industries"
助手：technology

用户："全球人工智能市场的商业化发展：趋势与挑战"
助手：economy

用户："5 Charts Show The S&P 500 Falling To 4,850"
助手：economy

以下是需要你分类的标题：
用户："{title}"
助手："""

class TeeLogger:
    def __init__(self, log_path):
        self.terminal = sys.stdout
        self.log = open(log_path, "w", encoding="utf-8")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        self.terminal.flush()
        self.log.flush()
    def close(self):
        self.log.close()

def get_log_path(json_file):
    logs_dir = os.path.join(os.path.dirname(json_file), "../logs")
    logs_dir = os.path.abspath(logs_dir)
    os.makedirs(logs_dir, exist_ok=True)
    
    # 使用脚本名而不是json文件名
    script_name = os.path.basename(__file__)
    log_name = os.path.splitext(script_name)[0] + ".log"
    
    return os.path.join(logs_dir, log_name)

def test(
    title="宁波银行：2024年营业收入增速8.19%，拟每10股派现金红利9元",
    api_url="http://localhost:8001/v1/chat/completions",
    expected_category="economy"
):
    """
    直接测试函数，用于观察API的完整输出
    
    参数:
    title: 要测试的新闻标题
    api_url: API服务的URL地址
    expected_category: 预期的分类结果，用于判断分类是否正确
    """
    print("\n" + "=" * 80)
    print(f"测试标题: {title}")
    print(f"预期分类: {expected_category}")
    print("=" * 80)
    
    # 构建提示
    prompt = CLASSIFICATION_PROMPT.format(title=title)
    
    # 准备API请求
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-model",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.01,
        "max_tokens": 500,  # 确保获取完整响应
        "top_p": 0.95
    }
    
    print("\n提示内容:")
    print("-" * 80)
    print(prompt)
    print("-" * 80)
    
    # 发送API请求
    print("\n发送API请求...")
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        print(f"收到响应: 状态码 {response.status_code}")
        
        if response.status_code != 200:
            print(f"错误: API返回非200状态码")
            print(response.text)
            return
        
        # 解析JSON响应
        result = response.json()
        
        # 打印完整响应
        print("\nAPI完整响应:")
        print("-" * 80)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("-" * 80)
        
        # 提取生成的文本
        content = result["choices"][0]["message"]["content"].strip()
        
        print("\n生成的原始文本:")
        print("-" * 80)
        print(content)
        print("-" * 80)
        
        # 从回复尾部提取分类结果
        # 尝试匹配最后出现的technology或economy单词
        tech_match = re.search(r'(technology)\s*$', content.lower())
        econ_match = re.search(r'(economy)\s*$', content.lower())
        
        if tech_match:
            classification = "technology"
        elif econ_match:
            classification = "economy"
        else:
            classification = None
        
        # 输出分类结果
        print("\n分类结果:")
        print(f"预测类别: {classification if classification else '无法提取分类结果'}")
        
        # 判断分类是否正确
        if classification:
            is_correct = classification.lower() == expected_category.lower()
            print(f"是否正确: {'✓' if is_correct else '✗'}")
            return classification, is_correct
        else:
            print("无法提取分类结果")
            return None, False
            
    except Exception as e:
        print(f"请求出错: {e}")
        return None, False

def main_inference(
    json_file="autonews-agent/post-training/dataset/inference.json",
    api_url="http://localhost:8001/v1/chat/completions",
    num_samples=5
):
    """
    单API批量测试，并将所有终端输出保存到日志文件
    """
    log_path = get_log_path(json_file)
    tee_logger = TeeLogger(log_path)
    sys.stdout = tee_logger

    try:
        print(f"\n{'='*40} 开始批量测试 {'='*40}")
        print(f"数据文件: {json_file}")
        print(f"API: {api_url}")
        print(f"测试样本数: {num_samples}")
        print('='*90)

        # 读取json文件
        samples = []
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data_list = json.load(f)
                if isinstance(data_list, list):
                    if num_samples == "all":
                        samples = [d for d in data_list if d.get("title") and d.get("category") and d["title"].strip() and d["category"].strip()]
                    else:
                        count = 0
                        for data in data_list:
                            if data.get("title") and data.get("category") and data["title"].strip() and data["category"].strip():
                                samples.append(data)
                                count += 1
                                if count >= int(num_samples):
                                    break
                else:
                    print(f"数据格式错误：预期是样本列表，但得到了 {type(data_list)}")
        except Exception as e:
            print(f"读取文件出错: {e}")
            return

        if not samples:
            print("没有找到有效样本，请检查文件格式")
            return

        print(f"成功读取 {len(samples)} 个有效样本")

        # 结果统计结构
        results = {
            "total": len(samples),
            "correct": 0,
            "incorrect": 0,
            "failed": 0,
            "samples": []
        }

        for i, sample in enumerate(samples):
            title = sample.get("title", "").strip()
            category = sample.get("category", "").strip()
            print(f"\n{'#'*40} 样本 {i+1}/{len(samples)} {'#'*40}")
            prediction, is_correct = test(title=title, api_url=api_url, expected_category=category)
            sample_result = {
                "title": title,
                "expected": category,
                "prediction": prediction,
                "is_correct": is_correct
            }
            results["samples"].append(sample_result)
            if prediction is None:
                results["failed"] += 1
            elif is_correct:
                results["correct"] += 1
            else:
                results["incorrect"] += 1
            # 实时打印准确率
            total_done = i + 1
            correct = results["correct"]
            print(f"[{api_url}] 当前准确率: {correct/total_done*100:.2f}% ({correct}/{total_done})")

        # 输出最终统计
        print(f"\n{'='*40} 测试结果摘要 {'='*40}")
        print(f"\nAPI: {api_url}")
        print(f"总样本数: {results['total']}")
        print(f"正确分类: {results['correct']} ({results['correct']/results['total']*100:.2f}%)")
        print(f"错误分类: {results['incorrect']} ({results['incorrect']/results['total']*100:.2f}%)")
        print(f"分类失败: {results['failed']} ({results['failed']/results['total']*100:.2f}%)")
        print('='*90)
        return results
    finally:
        sys.stdout = tee_logger.terminal
        tee_logger.close()

# 直接运行
if __name__ == "__main__":
    # # 单样本测试
    # test()
    # 或批量测试
    # main_inference(num_samples=1)
    main_inference(num_samples="all")

