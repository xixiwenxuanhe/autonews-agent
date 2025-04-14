import os
# 指定使用 GPU 1
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

import argparse
import sys

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, DataCollatorForSeq2Seq
from datasets import load_dataset
from peft import LoraConfig, get_peft_model

def load_and_preprocess_dataset(train_file, val_file, tokenizer, max_length=512):
    """
    加载 jsonl 格式的数据集并将数据格式化为适合生成任务的字符串。
    每条样本原始格式：
        {
            "messages": [
                {"role": "user", "content": "分类新闻标题：\"...\""},
                {"role": "assistant", "content": "..."}
            ]
        }
    本函数将每条数据构造为如下字符串：
        "User: {用户输入}\nAssistant: {回答}"
    然后进行 tokenize。
    """
    datasets = load_dataset("json", data_files={"train": train_file, "val": val_file})

    def format_example(example):
        messages = example["messages"]
        user_msg = ""
        assistant_msg = ""
        for msg in messages:
            if msg["role"] == "user":
                user_msg = msg["content"]
            elif msg["role"] == "assistant":
                assistant_msg = msg["content"]
        full_text = f"User: {user_msg}\nAssistant: {assistant_msg}"
        return {"text": full_text}

    def tokenize_fn(example):
        tokenized = tokenizer(
            example["text"],
            truncation=True,
            max_length=max_length,
            padding="max_length"
        )
        # 对于因果语言模型，将输入 ids 同时作为标签
        tokenized["labels"] = tokenized["input_ids"].copy()
        return tokenized

    for split in ["train", "val"]:
        datasets[split] = datasets[split].map(format_example, remove_columns=["messages"])
        datasets[split] = datasets[split].map(tokenize_fn, batched=False)
    return datasets

def main():
    parser = argparse.ArgumentParser(description="LoRA 微调 DeepSeek-R1-Distill-Qwen-14B 示例")
    parser.add_argument("--model_name_or_path", type=str, default="deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
                        help="预训练模型的名称或路径")
    parser.add_argument("--train_file", type=str, default="autonews-agent/post-training/dataset/train.jsonl", help="训练集文件路径")
    parser.add_argument("--val_file", type=str, default="autonews-agent/post-training/dataset/val.jsonl", help="验证集文件路径")
    parser.add_argument("--output_dir", type=str, default="autonews-agent/post-training/checkpoints",
                        help="模型保存目录")
    parser.add_argument("--lora_r", type=int, default=8, help="LoRA 的秩参数")
    parser.add_argument("--lora_alpha", type=int, default=32, help="LoRA 的 alpha 参数")
    parser.add_argument("--lora_dropout", type=float, default=0.1, help="LoRA 的 dropout 参数")
    # 由于拥有两个 80GB 的 GPU，可以适当增大每个 GPU 的 batch size
    parser.add_argument("--per_device_train_batch_size", type=int, default=32, help="每个 GPU 上训练的 batch size")
    parser.add_argument("--per_device_eval_batch_size", type=int, default=32, help="每个 GPU 上评估的 batch size")
    # 如果希望通过梯度累积进一步提高全局 batch size，可设置此参数
    parser.add_argument("--gradient_accumulation_steps", type=int, default=1, help="梯度累积步数")
    parser.add_argument("--num_train_epochs", type=int, default=1, help="训练轮数")
    parser.add_argument("--learning_rate", type=float, default=5e-5, help="学习率")
    parser.add_argument("--max_length", type=int, default=512, help="最大 token 长度")
    parser.add_argument("--logging_steps", type=int, default=10, help="日志记录间隔步数")
    args = parser.parse_args()

    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)

    # 设置wandb目录
    os.environ["WANDB_DIR"] = "autonews-agent/post-training"
    
    # 只在控制台打印信息，不创建日志文件
    print("加载模型和 tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path)
    model = AutoModelForCausalLM.from_pretrained(args.model_name_or_path, torch_dtype=torch.float16)
    # 开启梯度检查点以节省内存（大模型微调时非常有用）
    model.gradient_checkpointing_enable()
    
    # 配置 LoRA，注意 target_modules 根据模型结构可能需要调整
    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_config)
    print("模型已加载，并配置了 LoRA。")

    print("加载并预处理数据集...")
    datasets = load_and_preprocess_dataset(args.train_file, args.val_file, tokenizer, max_length=args.max_length)

    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding="longest")
    
    # 使用固定的输出目录
    output_dir = args.output_dir

    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=args.per_device_train_batch_size,
        per_device_eval_batch_size=args.per_device_eval_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        num_train_epochs=args.num_train_epochs,
        learning_rate=args.learning_rate,
        logging_steps=args.logging_steps,
        evaluation_strategy="steps",
        eval_steps=100,  # 每100步评估一次
        fp16=True,
        save_strategy="no",  # 不在中间步骤保存模型
        report_to="wandb",  # 使用wandb记录训练过程
        logging_dir=None,  # 不创建日志目录
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=datasets["train"],
        eval_dataset=datasets["val"],
        data_collator=data_collator,
    )
    
    print("开始训练...")
    trainer.train()
    print("训练结束。")
    
    print(f"保存模型到 {output_dir}...")
    trainer.save_model(output_dir)
    
    # 创建latest标记文件
    with open(os.path.join(output_dir, "latest"), "w") as f:
        f.write("这是最新的模型版本")
    
    print("模型保存完毕，并已添加latest标记。")

if __name__ == "__main__":
    main()
