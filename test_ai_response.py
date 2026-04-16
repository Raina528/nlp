# test_ai_response.py
# AI 响应测试脚本 - 测试不同动作的 AI 输出格式

import requests
import json
import re

# 配置
API_URL = "https://router.huggingface.co/v1/chat/completions"
API_TOKEN = "请在此输入自己的 token"
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"

def load_system_prompt():
    """加载 system prompt"""
    try:
        with open("system_prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("警告：未找到 system_prompt.txt")
        return ""

def call_ai(state_json: str, action: str) -> str:
    """调用 AI"""
    system_prompt = load_system_prompt()
    
    user_prompt = f"""当前游戏状态：
{state_json}

玩家操作：{action}

**重要：你必须严格按照以下格式输出：**

【剧情】
（1-3 句简短剧情描述）

【状态变更】
{{
  "字段名": 新数值
}}

注意：
1. 只输出变化的字段，不变的字段不要出现
2. JSON 必须标准可解析
3. 不要输出任何解释、分析或额外内容

请根据以上状态和操作，生成剧情和状态变更。"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": 300,
        "temperature": 0.7
    }
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"].get("content", "")
        else:
            print(f"API 调用失败：{response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"异常：{e}")
    
    return None

def parse_response(text: str):
    """解析 AI 响应"""
    # 提取剧情
    drama_match = re.search(r'【剧情】\s*(.*?)\s*【状态变更】', text, re.DOTALL)
    drama = drama_match.group(1).strip() if drama_match else "❌ 未找到剧情"
    
    # 提取 JSON
    json_match = re.search(r'【状态变更】\s*\{([^}]+)\}', text, re.DOTALL)
    if json_match:
        try:
            json_str = '{' + json_match.group(1) + '}'
            json_str = json_str.replace('\n', '').replace('  ', '')
            changes = json.loads(json_str)
            return drama, changes
        except:
            return drama, {}
    else:
        return drama, {}

def test_action(action: str, state: dict):
    """测试单个动作"""
    print(f"\n{'='*60}")
    print(f"测试动作：{action}")
    print('='*60)
    
    state_json = json.dumps(state, ensure_ascii=False)
    response = call_ai(state_json, action)
    
    if not response:
        print("❌ AI 返回为空")
        return
    
    print(f"\nAI 原始回复:\n{response}\n")
    
    drama, changes = parse_response(response)
    
    print(f"✅ 解析结果:")
    print(f"剧情：{drama}")
    print(f"状态变更：{changes if changes else '❌ 无'}")

def main():
    """主测试函数"""
    print("="*60)
    print("AI 响应格式测试")
    print("="*60)
    
    # 初始状态
    initial_state = {
        "oxygen": 100,
        "oxygen_max": 100,
        "depth": 0,
        "max_depth": 50,
        "gold": 0,
        "fish": 0,
        "lvl_oxy": 0,
        "lvl_suit": 0,
        "lvl_retractable_claw": 0,
        "lvl_engine": 0,
        "lvl_scan": 0,
        "lvl_inn": 0
    }
    
    # 测试各种动作
    actions = ["下潜", "探测", "捕获", "撤离", "全部卖出"]
    
    for action in actions:
        test_action(action, initial_state)
    
    # 测试升级
    test_action("升级氧气瓶", initial_state)
    
    # 测试深度状态
    deep_state = initial_state.copy()
    deep_state["depth"] = 100
    deep_state["oxygen"] = 80
    test_action("撤离", deep_state)
    
    # 测试有鱼状态
    fish_state = initial_state.copy()
    fish_state["depth"] = 0
    fish_state["fish"] = 3
    test_action("全部卖出", fish_state)
    
    print(f"\n{'='*60}")
    print("测试完成")
    print('='*60)

if __name__ == "__main__":
    main()
