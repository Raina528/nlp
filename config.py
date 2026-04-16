# config.py
# NLP-GroupProject AI 配置

import os


def _load_env_file(path: str = ".env") -> None:
	"""读取本地 .env 文件，将其中的键值写入环境变量。"""
	if not os.path.exists(path):
		return

	with open(path, "r", encoding="utf-8") as env_file:
		for raw_line in env_file:
			line = raw_line.strip()
			if not line or line.startswith("#") or "=" not in line:
				continue

			key, value = line.split("=", 1)
			key = key.strip()
			value = value.strip().strip('"').strip("'")

			if key and key not in os.environ:
				os.environ[key] = value


_load_env_file()

# 阿里云 DashScope API 配置（OpenAI 兼容格式）
HF_API_URL = os.getenv("HF_API_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5-14b-instruct")  # 千问指令模型

# 游戏参数
INITIAL_OXYGEN = 100  # 初始氧气值
INITIAL_GOLD = 0  # 初始金币
INITIAL_DEPTH = 0  # 初始深度

# API 调用参数
TEMPERATURE = 0.7
MAX_NEW_TOKENS = 500
TOP_P = 0.9

# 文件路径
SYSTEM_PROMPT_FILE = "system_prompt.txt"
