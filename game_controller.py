# game_controller.py
# 游戏控制器模块 - 负责协调游戏逻辑和 AI 交互（JSON 格式版本）

import re
from game_engine import ShibaGame
from ai_service import AIService
import config


class GameController:
    """游戏控制器类 - JSON 格式交互"""
    
    def __init__(self):
        self.game = ShibaGame()
        self.ai_service = AIService(backend="hf")
        
        # 加载 system_prompt
        self.system_prompt = self._load_system_prompt()

        # 初始引导语（纯文本，用于显示）
        self.initial_narrative = """
🌊 **《柴犬潜水员：深海珍味》** 🌊

夕阳把海面染成了金枪鱼刺身的颜色。阿柴系好绿方巾，戴上沉重的透明头盔，咔哒一声，防水密封完成。
它看着空荡荡的推车，对着大海汪汪叫了两声壮胆，然后摆动起像螺旋桨一样的尾巴，一头扎进了凉爽的蔚蓝之中。

**第一场深海猎场，开启！**
"""
        self.reset_game_state()
    
    def _load_system_prompt(self) -> str:
        """加载系统提示词"""
        try:
            with open(config.SYSTEM_PROMPT_FILE, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print("警告：未找到 system_prompt.txt")
            return "你是游戏 AI。"
        
    def _load_prompt(self, filename: str) -> str:
        """加载单个 prompt 文件"""
        try:
            with open(f"prompts/{filename}", 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
        
    def build_system_prompt(self, action: str) -> str:
        """
        根据动作类型构建 system prompt
        背景信息 + 输出格式 + 对应动作指令
        """
        background = self._load_prompt("prompt_background.txt")
        format_rules = self._load_prompt("prompt_format.txt")
            
        # 根据动作类型加载对应指令
        action_prompts = {
            "下潜": "prompt_dive.txt",
            "探测": "prompt_detect.txt",
            "捕获": "prompt_catch.txt",
            "撤离": "prompt_return.txt",
        }
            
        action_file = action_prompts.get(action, "")
        action_prompt = self._load_prompt(action_file) if action_file else ""
            
        # 组合 prompt
        parts = [background, format_rules]
        if action_prompt:
            parts.append(action_prompt)
            
        return "\n\n".join(parts)
    
    def reset_game_state(self):
        """重置游戏状态"""
        self.game.reset_game()
    
    def generate_first_scene(self):
        """生成第一场景"""
        state_json = self.game.get_state_json()
        system_prompt = self.build_system_prompt("开始游戏")
        user_prompt = f"""当前状态：
{state_json}

玩家操作：开始游戏

请按照规定的格式输出。"""
        response = self.ai_service.call_with_retry(user_prompt, system_prompt)
        
        if not response:
            return self.get_fallback_response()
        
        drama, changes = self.ai_service.parse_ai_response(response)
        self.game.apply_state_changes(changes)
        
        return drama
    
    def process_player_action(self, action: str) -> str:
        """
        处理玩家行动（JSON 格式）
        
        Args:
            action: 玩家操作（下潜/探测/捕获/撤离/升级 XX/全部卖出）
        Returns:
            剧情文本
        """
        # 获取当前状态 JSON
        state_json = self.game.get_state_json()
        
        # 构建动态 system prompt（根据动作类型）
        system_prompt = self.build_system_prompt(action)
        
        # 构建符合 system_prompt 要求的用户输入
        user_prompt = f"""当前状态：
{state_json}

玩家操作：{action}

请按照规定的格式输出。"""
        
        # 调用 AI
        response = self.ai_service.call_with_retry(user_prompt, system_prompt)
        
        if not response:
            return "AI 调用失败，请检查网络连接。"
        
        # 解析 AI 响应
        drama, changes = self.ai_service.parse_ai_response(response)
        
        # 应用状态变更
        self.game.apply_state_changes(changes)
        
        # 【关键】检查氧气是否耗尽
        if self.game.energy <= 0:
            # 触发氧气耗尽剧情
            fail_drama = (
                "这次海底探险让阿柴玩的很开心，完全没注意到氧气表的指针不断下跌。"
                "当警报声在耳边炸响的时候，氧气已经彻底耗尽，它眼前一黑朝着海底坠去。"
                "就在意识即将消散的时候，一阵温暖的浮力托住了它，阿柴迷迷糊糊睁开眼，"
                "看见一条蓝鲸正用尾巴轻柔地将自己托着，朝着海面缓缓上升..."
                "不过在岸边醒来阿柴才发现自己的捕到的鱼弄丢了。"
            )
            # 执行重置逻辑：深度归零、氧气补满、清空背包（鱼）、金币不变
            self.game.state["depth"] = 0
            self.game.state["oxygen"] = self.game.state["oxygen_max"]
            self.game.state["fish"] = 0
            # 确保不因为 AI 之前的返回而意外增加金币，这里强制同步一次状态
            
            return fail_drama
        
        return drama

    def stream_player_action(self, action: str):
        """
        流式处理玩家行动（打字机效果）
        
        Yields:
            str: 逐步生成的剧情文本
        """
        state_json = self.game.get_state_json()
        system_prompt = self.build_system_prompt(action)
        user_prompt = f"当前状态：\n{state_json}\n\n玩家操作：{action}\n\n请按照规定的格式输出。"
        
        full_response = ""
        # 逐字获取 AI 回复并 yield 出去
        for chunk in self.ai_service.stream_chat(user_prompt, system_prompt):
            full_response += chunk
            yield full_response
        
        # 结束后解析状态并存档
        if full_response:
            drama, changes = self.ai_service.parse_ai_response(full_response)
            self.game.apply_state_changes(changes)
            yield drama  # 确保最后返回的是纯净的剧情
        else:
            yield "AI 调用失败，请检查网络连接。"

    def get_fallback_response(self):
        """获取备用回复（当 AI 调用失败时）"""
        return f"""
【状态栏：深度 -{self.game.depth}m 氧气 {self.game.energy}% 金币 {self.game.gold} | 居酒屋 L{self.game.hall_level}】

[环境描述]
周围是幽蓝的海水，几缕阳光透过水面洒下。一群小鱼游过，远处有珊瑚礁的影子。

[阿柴的状态]
阿柴疑惑地甩了甩尾巴，面罩上起了一层薄雾。它用爪子拍了拍头盔，汪汪叫了两声。

[行动指令]
A.[探索] 向更深处前进
B.[捕获] 尝试用爪子抓鱼
C.[特殊] 使用探测器寻找美味
D.[撤离] 回到海面
"""

    def local_action(self, action: str) -> str:
        """
        本地程序响应动作（升级、卖鱼等不连接 AI）
        返回剧情文本
        """
        # 全部卖出
        if action == "全部卖出":
            result = self.game.sell_all_fish()
            if result == -1:
                return "⚠ 必须返回海面（深度 0）才能卖鱼！"
            if result == 0:
                return "🎒 背包里没有鱼可以卖。"
            return f"""💰 **卖出成功！**

卖出所有鱼类，获得 **{result}** 金币！
当前金币：{self.game.gold}
背包已清空。"""
            
        # 升级逻辑
        for equip_name in ["氧气瓶", "伸缩爪", "探测器", "居酒屋"]:
            if f"升级{equip_name}" in action or action == f"升级{equip_name}":
                success, cost, desc = self.game.upgrade(equip_name)
                if success:
                    return f"🔧 {desc}"
                else:
                    return f"⚠ 升级失败：{desc}"
                    
        return f"未知操作：{action}"
