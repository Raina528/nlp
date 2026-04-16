"""
Qwen2-7B 4bit 最小化推理 Demo
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# 模型路径
MODEL_PATH = "../models/qwen2-7b"

print("加载模型中...\n")

# 4bit 量化配置
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# 加载分词器
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)

# 加载模型
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

print("✓ 模型加载完成\n")
print("输入 'quit' 退出\n")

while True:
    user_input = input("你：")
    if user_input.lower() in ['quit', 'exit', 'q']:
        break
    
    # 构建消息
    messages = [{"role": "user", "content": user_input}]
    
    # 应用对话模板
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    # 编码
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    
    # 生成回复
    with torch.inference_mode():
        outputs = model.generate(**inputs, max_new_tokens=512)
    
    # 解码回复
    response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    print(f"AI: {response}\n")
