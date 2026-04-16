# ai_service.py
# 统一 AI 服务模块 - 整合 Hugging Face Space 和阿里云 API

import requests
import json
import time
import re
from typing import Optional, List, Dict, Any, Tuple, Iterator
import config

try:
    from gradio_client import Client
    HAS_GRADIO_CLIENT = True
except ImportError:
    HAS_GRADIO_CLIENT = False


class RawAPICaller:
    """原始 API 调用封装层 - 负责底层 HTTP/gRPC 通信"""
    
    # HF Space 客户端缓存
    _hf_client = None
    _hf_space_id = "bigorange074/nlp_ft"
    
    @staticmethod
    def call_hf_space(user_input: str, api_name: str = "/generate_story") -> Optional[str]:
        """
        调用 Hugging Face Space
        
        Args:
            user_input: 用户输入
            api_name: Space 的 API 端点名称
            
        Returns:
            AI 回复文本，失败返回 None
        """
        if not HAS_GRADIO_CLIENT:
            print("⚠️ 未安装 gradio_client")
            return None
        
        try:
            # 复用已创建的客户端，避免重复加载
            if RawAPICaller._hf_client is None:
                RawAPICaller._hf_client = Client(RawAPICaller._hf_space_id)
            
            result = RawAPICaller._hf_client.predict(
                user_input=user_input,
                api_name=api_name
            )
            return result
        except Exception as e:
            print(f"⚠️ HF Space 调用失败: {e}")
            # 出错时重置客户端，下次重新创建
            RawAPICaller._hf_client = None
            return None
    
    @staticmethod
    def call_aliyun_normal(
        user_prompt: str,
        system_prompt: str = None,
        history: List[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        调用阿里云 DashScope API（非流式）
        
        Args:
            user_prompt: 用户输入
            system_prompt: 系统提示词
            history: 对话历史
            
        Returns:
            AI 回复文本，失败返回 None
        """
        headers = {
            "Authorization": f"Bearer {config.HF_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt and system_prompt.strip():
            messages.append({"role": "system", "content": system_prompt.strip()})
        
        if history and isinstance(history, list):
            for msg in history:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    messages.append({"role": msg["role"], "content": str(msg["content"])})
        
        if not user_prompt.strip():
            user_prompt = "请继续游戏。"
        messages.append({"role": "user", "content": user_prompt.strip()})
        
        payload = {
            "model": config.MODEL_NAME,
            "messages": messages,
            "max_tokens": config.MAX_NEW_TOKENS,
            "temperature": config.TEMPERATURE,
            "top_p": config.TOP_P
        }
        
        try:
            response = requests.post(
                config.HF_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"].get("content", "")
            else:
                print(f"API 错误: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"API 调用异常：{e}")
        
        return None
    
    @staticmethod
    def call_aliyun_stream(
        user_prompt: str,
        system_prompt: str
    ) -> Iterator[str]:
        """
        调用阿里云 DashScope API（流式）
        
        Args:
            user_prompt: 用户输入
            system_prompt: 系统提示词
            
        Yields:
            逐字生成的文本片段
        """
        headers = {
            "Authorization": f"Bearer {config.HF_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": config.MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": True
        }
        
        try:
            response = requests.post(
                config.HF_API_URL,
                headers=headers,
                json=payload,
                stream=True,
                timeout=60
            )
            
            if response.status_code != 200:
                yield f"[错误] API 请求失败: {response.text}"
                return
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith("data: "):
                        data_str = line_str[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            content = data["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            yield f"[网络错误] {str(e)}"


class ResponseParser:
    """AI 响应解析器 - 负责从 AI 回复中提取剧情和状态变更"""
    
    @staticmethod
    def parse(response_text: str) -> Tuple[str, Dict[str, Any]]:
        """
        解析 AI 返回的响应（支持多种格式）
        
        Args:
            response_text: AI 原始回复文本
            
        Returns:
            (剧情文本，状态变更字典)
        """
        drama = response_text
        changes = {}
        
        # 尝试 1：标准格式【剧情】+【状态变更】JSON
        drama_match = re.search(r'【剧情】\s*(.*?)\s*【状态变更】', response_text, re.DOTALL)
        json_match = re.search(r'【状态变更】\s*\{([^}]+)\}', response_text, re.DOTALL)
        
        if drama_match:
            drama = drama_match.group(1).strip()
        
        if json_match:
            try:
                json_str = '{' + json_match.group(1) + '}'
                json_str = json_str.replace('\n', '').replace('  ', '')
                changes = json.loads(json_str)
                print(f"✓ 解析成功：{changes}")
                return drama, changes
            except Exception as e:
                print(f"JSON解析失败：{e}")
        
        # 尝试 2：在整个文本中查找 JSON 对象（更宽松的匹配）
        json_patterns = [
            r'\{\s*"(?:depth|oxygen|gold|fish|lvl_)[^"]*"\s*:\s*\d+[^}]*\}',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response_text, re.DOTALL)
            for match in matches:
                try:
                    clean_json = match.replace('\n', ' ').strip()
                    changes = json.loads(clean_json)
                    if changes:
                        print(f"✓ 宽松解析成功：{changes}")
                        return drama, changes
                except:
                    continue
        
        # 尝试 3：从文本中提取状态字段（兜底方案）
        print(f"⚠ 非标准格式，尝试智能解析")
        
        # 提取深度
        depth_patterns = [
            r'深度.*?(\d+)\s*米？',
            r'当前深度\s*(\d+)',
            r'depth.*?(\d+)'
        ]
        for pattern in depth_patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                changes['depth'] = int(match.group(1))
                break
        
        # 提取氧气
        oxygen_patterns = [
            r'氧气.*?(\d+)[%\s]?',
            r'当前氧气\s*(\d+)',
            r'oxygen.*?(\d+)'
        ]
        for pattern in oxygen_patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                changes['oxygen'] = int(match.group(1))
                break
        
        # 提取金币
        gold_patterns = [
            r'黄金.*?(\d+)',
            r'金(?:币)?.*?(\d+)',
            r'gold.*?(\d+)'
        ]
        for pattern in gold_patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                changes['gold'] = int(match.group(1))
                break
        
        # 提取鱼数量
        fish_patterns = [
            r'鱼\s*(\d+)\s*条',
            r'捕获\s*(\d+)\s*条',
            r'fish.*?(\d+)',
            r'鱼.*?(\d+)'
        ]
        for pattern in fish_patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                changes['fish'] = int(match.group(1))
                break
        
        # 提取等级
        level_patterns = {
            'lvl_oxy': r'(?:氧气瓶|lvl_oxy).*?(\d+)',
            'lvl_suit': r'(?:潜水服|lvl_suit).*?(\d+)',
            'lvl_retractable_claw': r'(?:伸缩爪|lvl_retractable_claw).*?(\d+)',
            'lvl_engine': r'(?:推进器|lvl_engine).*?(\d+)',
            'lvl_scan': r'(?:探测器|lvl_scan).*?(\d+)',
            'lvl_inn': r'(?:居酒屋|lvl_inn).*?(\d+)'
        }
        
        for key, pattern in level_patterns.items():
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                changes[key] = int(match.group(1))
        
        if not changes:
            print("❌ 无法从回复中提取状态信息")
            return drama, {}
        
        print(f"✓ 智能提取状态变更：{changes}")
        return drama, changes

# 对外接口
class AIService:
    """统一 AI 服务 - 提供简化的调用接口，支持后端切换和重试"""
    
    def __init__(self, backend: str = "hf_space"):
        """
        初始化 AI 服务
        
        Args:
            backend: 后端类型 ("hf_space" | "aliyun")
        """
        self.backend = backend
        self.parser = ResponseParser()
    
    def call_model(
        self,
        user_prompt: str,
        system_prompt: str = None,
        history: List[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        调用 AI 模型生成回复（非流式）
        
        Args:
            user_prompt: 用户输入
            system_prompt: 系统提示词
            history: 对话历史
            
        Returns:
            AI 回复文本，失败返回 None
        """
        if self.backend == "hf_space":
            return RawAPICaller.call_hf_space(user_prompt)
        else:
            return RawAPICaller.call_aliyun_normal(user_prompt, system_prompt, history)
    
    def call_with_retry(
        self,
        user_prompt: str,
        system_prompt: str = None,
        history: List[Dict[str, str]] = None,
        max_retries: int = 2
    ) -> Optional[str]:
        """
        带重试的调用
        
        Args:
            user_prompt: 用户输入
            system_prompt: 系统提示词
            history: 对话历史
            max_retries: 最大重试次数
            
        Returns:
            AI 回复内容
        """
        for attempt in range(max_retries + 1):
            result = self.call_model(user_prompt, system_prompt, history)
            if result is not None:
                return result
            if attempt < max_retries:
                print(f"重试第 {attempt+1} 次...")
                time.sleep(2)
        return None
    
    def stream_chat(self, user_prompt: str, system_prompt: str) -> Iterator[str]:
        """
        流式聊天（仅阿里云支持）
        
        Args:
            user_prompt: 用户输入
            system_prompt: 系统提示词
            
        Yields:
            逐步生成的文本片段
        """
        if self.backend == "hf_space":
            print("⚠️ HF Space 不支持流式，降级为非流式调用")
            result = self.call_model(user_prompt, system_prompt)
            if result:
                yield result
        else:
            for chunk in RawAPICaller.call_aliyun_stream(user_prompt, system_prompt):
                yield chunk
    
    def get_full_response(self, user_prompt: str, system_prompt: str) -> str:
        """
        获取完整的流式响应字符串（用于后端解析状态）
        
        Args:
            user_prompt: 用户输入
            system_prompt: 系统提示词
            
        Returns:
            完整的 AI 回复文本
        """
        full_text = ""
        for chunk in self.stream_chat(user_prompt, system_prompt):
            full_text += chunk
        return full_text
    
    def parse_ai_response(self, response_text: str) -> Tuple[str, Dict[str, Any]]:
        """
        解析 AI 响应
        
        Args:
            response_text: AI 原始回复
            
        Returns:
            (剧情文本，状态变更字典)
        """
        return self.parser.parse(response_text)
    
    def call_with_memory(
        self,
        user_prompt: str,
        system_prompt: str = None,
        conversation_history: List[Dict[str, str]] = None,
        max_history_rounds: int = 10
    ) -> Optional[str]:
        """
        带上下文记忆的阿里云 API 调用
        
        Args:
            user_prompt: 用户输入
            system_prompt: 系统提示词
            conversation_history: 对话历史列表，格式为 [{"role": "user/assistant", "content": "..."}]
            max_history_rounds: 最大保留的历史轮数（默认10轮，避免超出token限制）
            
        Returns:
            AI 回复文本，失败返回 None
        """
        if self.backend != "aliyun":
            print("⚠️ 此方法仅支持阿里云后端")
            return None
        
        # 截取最近的历史记录（滑动窗口）
        truncated_history = None
        if conversation_history and len(conversation_history) > 0:
            # 只保留最近的 max_history_rounds * 2 条消息（user + assistant 算一轮）
            truncated_history = conversation_history[-(max_history_rounds * 2):]
        
        # 调用阿里云 API（传入截断后的历史）
        return RawAPICaller.call_aliyun_normal(user_prompt, system_prompt, truncated_history)


if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("测试 AIService")
    print("=" * 60)
    
    # 测试 1: HF Space 后端
    print("\n【测试 1】HF Space 后端")
    service_hf = AIService(backend="hf_space")
    response = service_hf.call_with_retry("你好", "你是一个友好的助手。")
    if response:
        print(f"回复: {response[:100]}...")
        drama, changes = service_hf.parse_ai_response(response)
        print(f"剧情长度: {len(drama)}, 状态变更: {changes}")
    else:
        print("调用失败")
    
    # 测试 2: 阿里云后端
    print("\n【测试 2】阿里云后端")
    service_ali = AIService(backend="aliyun")
    response = service_ali.call_with_retry("你好", "你是一个友好的助手。")
    if response:
        print(f"回复: {response[:100]}...")
    else:
        print("调用失败")
