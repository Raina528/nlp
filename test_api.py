# test_api.py
# API 调用测试脚本 - 用于本地调试

import requests
import json

# 配置
API_URL = "https://router.huggingface.co/v1/chat/completions"
API_TOKEN = "请在此输入自己的 token"

# 可用的模型列表（常见的）
AVAILABLE_MODELS = [
    "Qwen/Qwen3.5-35B-A3B",
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen2-7B-Instruct", 
    "meta-llama/Llama-3.2-3B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "google/gemma-2b-it"
]

def test_model(model_name):
    """测试指定模型是否可用"""
    print(f"\n{'='*60}")
    print(f"测试模型：{model_name}")
    print('='*60)
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 测试数据
    messages = [
        {"role": "system", "content": "你是一个游戏叙述引擎。"},
        {"role": "user", "content": "当前游戏状态：{\"oxygen\": 100, \"depth\": 0}\n玩家操作：下潜\n请生成剧情和状态变更。"}
    ]
    
    payload = {
        "model": model_name,
        "messages": messages,
        "max_tokens": 200,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"状态码：{response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 调用成功！")
            print("\n响应内容:")
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"].get("content", "")
                print(f"AI 回复:\n{content}")
                
                # 尝试解析 JSON
                import re
                json_match = re.search(r'【状态变更】\s*\{([^}]+)\}', content, re.DOTALL)
                if json_match:
                    json_str = '{' + json_match.group(1) + '}'
                    json_str = json_str.replace('\n', '').replace('  ', '')
                    try:
                        changes = json.loads(json_str)
                        print(f"\n✅ 成功解析状态变更 JSON: {changes}")
                    except:
                        print(f"\n❌ JSON 解析失败：{json_str}")
            
            return True
        else:
            print("❌ 调用失败")
            print(f"错误信息：{response.text}")
            
            # 尝试解析错误
            try:
                error = response.json()
                if "error" in error:
                    print(f"错误详情：{error['error'].get('message', '')}")
            except:
                pass
            
            return False
            
    except Exception as e:
        print(f"❌ 异常：{e}")
        return False


def main():
    """主函数"""
    print("="*60)
    print("HuggingFace API 模型可用性测试")
    print("="*60)
    
    # 测试所有可用模型
    available_models = []
    
    for model in AVAILABLE_MODELS:
        if test_model(model):
            available_models.append(model)
    
    # 输出结果
    print(f"\n{'='*60}")
    print("测试结果汇总")
    print('='*60)
    
    if available_models:
        print(f"\n✅ 可用的模型 ({len(available_models)} 个):")
        for i, model in enumerate(available_models, 1):
            print(f"{i}. {model}")
        
        print(f"\n💡 建议：将 config.py 中的 MODEL_NAME 修改为第一个可用模型")
        print(f"   MODEL_NAME = \"{available_models[0]}\"")
    else:
        print("\n❌ 所有模型都不可用")
        print("可能原因:")
        print("1. API Token 无效")
        print("2. 网络连接问题")
        print("3. HuggingFace 路由服务不可用")


if __name__ == "__main__":
    main()
