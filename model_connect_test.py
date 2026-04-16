from gradio_client import Client

# 1. 连接到你的 Space
# 注意：如果你的项目名是 nlp_ft，请确保 URL 拼写完全一致
client = Client("bigorange074/nlp_ft")

# 2. 调用预测函数
# 如果你刚才在 app.py 里设置了 api_name="generate_story"，
# 那么 client 内部通常会自动识别为 "/generate_story"
try:
    result = client.predict(
        user_input="猎杀三文鱼",
        api_name="/generate_story"
    )
    # 3. 打印结果（确保换行）
    print("--- 模型输出的 JSON ---")
    print(result)

except Exception as e:
    print(f"❌ 调用失败: {e}")
    print("💡 提示：如果依然报 ValueError，请尝试将 api_name='/generate_story' 改为 fn_index=0")