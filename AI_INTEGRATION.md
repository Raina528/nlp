# NLP-GroupProject AI 交互模块说明

## 项目结构

本项目已成功集成 Hugging Face 千问模型 API，实现了 AI 驱动的知识图谱冒险游戏。

### 新增文件列表

1. **config.py** - AI 配置文件
   - Hugging Face API URL 和 Token
   - 模型名称（Qwen/Qwen3.5-9B）
   - 游戏参数配置

2. **ai_client.py** - AI 客户端模块
   - 负责与 Hugging Face API 通信
   - 处理 API 调用、重试机制
   - 从 reasoning 字段提取有效内容

3. **game_engine.py** - 游戏引擎模块
   - 管理游戏状态（深度、能量、金币、装备等）
   - 实现游戏核心逻辑（能量消耗、捕获、升级等）
   - 提供状态栏生成接口

4. **prompt_builder.py** - 提示词构建器模块
   - 构建给 AI 的提示词
   - 解析 AI 返回的响应
   - 提取状态栏、环境描述等信息

5. **game_controller.py** - 游戏控制器模块
   - 协调游戏逻辑和 AI 交互
   - 处理玩家行动
   - 提供备用回复和失败处理

6. **system_prompt.txt** - 系统提示词文件
   - 定义游戏规则和世界观
   - 规定输出格式模板
   - 包含初始引导语

7. **qwen_api.py** - 简化的 API 调用示例
   - 快速测试 API 连接
   - 简单的对话功能

8. **game_ui.py** (已修改) - 主界面（AI 驱动版）
   - 集成 GameController
   - 绑定事件处理
   - 实现 AI 实时交互

## 运行方法

### 1. 安装依赖

```bash
pip install requests
pip install gradio
```

或一次性安装所有依赖：
```bash
pip install -r requirements.txt
```

### 2. 测试 API 连接

```bash
python qwen_api.py
```

如果成功，会看到 AI 的回复。

### 3. 启动游戏

```bash
python game_ui.py
```

游戏会自动在浏览器中打开（默认端口：7869）

## 游戏说明

### 世界观
你是一位探索知识海洋的探险家，在深海中发现概念、建立知识联系，构建完整的知识图谱。

### 核心机制
- **能量系统**：每次行动消耗能量，能量归零则任务失败
- **捕获系统**：使用概念捕捉器抓取知识点
- **升级系统**：用金币升级装备和知识馆
- **随机事件**：遇到知识暖流、概念漩涡等

### 操作方式
- **A. 探索**：向更深处潜行，发现新知识领域
- **B. 捕获**：使用概念捕捉器抓取概念
- **C. 特殊**：开启知识探测器寻找隐藏知识
- **D. 撤离**：返回海面进行知识整理

## API 配置

如需更换 API Token，请编辑 `config.py` 文件：

```python
HF_API_TOKEN = "你的新 token"
```

## 自定义提示词

可以修改 `system_prompt.txt` 来调整游戏设定、叙事风格等。

## 技术栈

- **前端**：Gradio
- **AI 模型**：Qwen/Qwen3.5-9B (Hugging Face)
- **语言**：Python 3.x

## 注意事项

1. 确保网络连接正常，能够访问 Hugging Face API
2. API Token 需要有效且有足够的配额
3. 如遇 API 调用失败，系统会自动重试（最多 2 次）
4. 如果 AI 服务完全不可用，系统会使用备用回复

## 扩展建议

- 添加更多随机事件类型
- 实现多人协作模式
- 增加知识图谱可视化功能
- 添加成就系统
