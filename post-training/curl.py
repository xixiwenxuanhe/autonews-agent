import requests
import json
import sys
import re

def query_llm(messages, model="deepseek-ai/DeepSeek-R1-Distill-Qwen-14B", temperature=0.7, max_tokens=800):
    """
    向本地API发送请求获取LLM回复
    
    参数:
    messages (list): 对话历史消息列表
    model (str): 使用的模型名称
    temperature (float): 温度参数，控制输出的随机性
    max_tokens (int): 最大生成的token数量
    
    返回:
    dict: API的完整响应
    """
    
    url = "http://localhost:8000/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # 如果响应包含错误状态码，则抛出异常
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None

def clean_response(text):
    """
    清理响应文本，删除</think>之前的内容
    
    参数:
    text (str): 原始响应文本
    
    返回:
    str: 清理后的文本
    """
    # 查找</think>标记
    if "</think>" in text:
        # 提取</think>后的内容
        cleaned_text = text.split("</think>")[-1].strip()
        return cleaned_text
    else:
        # 如果没有</think>标记，返回原文本
        return text

def interactive_chat():
    """
    交互式对话函数，支持多轮对话
    """
    # 初始化对话历史
    conversation_history = []
    
    print("欢迎使用模型对话系统！输入'q'退出对话。")
    print("=" * 50)
    
    while True:
        # 获取用户输入
        user_input = input("\n用户: ")
        
        # 检查是否退出
        if user_input.lower() == 'q':
            print("再见！")
            break
        
        # 添加用户消息到历史
        conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        print("正在思考...")
        
        # 发送请求，包含完整对话历史
        response = query_llm(conversation_history)
        
        if response:
            # 提取助手的回复
            raw_message = response["choices"][0]["message"]["content"]
            
            # 清理回复，移除</think>之前的内容
            assistant_message = clean_response(raw_message)
            
            print("\n助手: " + assistant_message)
            
            # 将清理后的助手回复添加到对话历史
            conversation_history.append({
                "role": "assistant",
                "content": assistant_message  # 使用清理后的文本
            })
        else:
            print("获取回复失败，请重试")

if __name__ == "__main__":
    # 如果有命令行参数，则使用单次查询模式；否则进入交互式对话模式
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
        print(f"发送提示词: {prompt}")
        print("正在等待响应...")
        
        response = query_llm([{"role": "user", "content": prompt}])
        
        if response:
            # 提取助手的回复并清理
            raw_message = response["choices"][0]["message"]["content"]
            assistant_message = clean_response(raw_message)
            
            print("\n--- 回复 ---")
            print(assistant_message)
    else:
        # 启动交互式对话
        interactive_chat()