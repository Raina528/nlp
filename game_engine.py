# game_engine.py
# 游戏引擎模块 - 负责管理游戏状态和逻辑（JSON 格式与 system_prompt 匹配）

import json
from typing import Dict, Any


class ShibaGame:
    """柴犬潜水员游戏类（JSON 状态版本）"""
    
    def __init__(self):
        """初始化游戏状态"""
        self.reset_game()
    
    def reset_game(self):
        """重置游戏到初始状态（使用 system_prompt 定义的字段）"""
        self.state = {
            "oxygen": 100,
            "oxygen_max": 100,
            "depth": 0,
            "max_depth": 100,  # 固定最大深度
            "gold": 10000,
            "fish": 0,
            "lvl_oxy": 0,
            "lvl_retractable_claw": 0,
            "lvl_scan": 0,
            "lvl_inn": 0
        }
    
    def get_state_json(self) -> str:
        """获取当前状态的 JSON 字符串"""
        return json.dumps(self.state, ensure_ascii=False)
    
    def apply_state_changes(self, changes: Dict[str, Any]):
        """应用 AI 返回的状态变更"""
        for key, value in changes.items():
            if key in self.state:
                self.state[key] = value
    
    # 以下为兼容旧 UI 的属性方法
    @property
    def depth(self):
        return self.state["depth"]
    
    @property
    def energy(self):
        return self.state["oxygen"]
    
    @property
    def gold(self):
        return self.state["gold"]
    
    @property
    def hall_level(self):
        return self.state["lvl_inn"]
    
    @property
    def inventory(self):
        # 为了兼容旧 UI，返回鱼的列表
        return [{"name": f"鱼{i+1}", "icon": "🐟", "weight": 1, "value": 10} for i in range(self.state["fish"])]
    
    @property
    def current_weight(self):
        return self.state["fish"]
    
    @property
    def max_weight(self):
        return 10  # 简化处理
    
    @property
    def equipment(self):
        return {
            "energy_bottle": self.state["lvl_oxy"],
            "catcher": self.state["lvl_retractable_claw"],
            "detector": self.state["lvl_scan"]
        }
    
    def to_dict(self) -> Dict:
        """导出状态为字典"""
        return self.state.copy()
    
    def from_dict(self, data: Dict):
        """从字典恢复状态"""
        self.state = data.copy()
    
    def sell_all_fish(self) -> int:
        """卖出所有鱼类（本地逻辑）"""
        fish_count = self.state["fish"]
        if fish_count == 0:
            return 0
        
        if self.state["depth"] != 0:
            return -1  # 错误码：只能在水面卖出
            
        base_price = 30
        bonus = self.state["lvl_inn"] * 0.2
        total = int(fish_count * base_price * (1 + bonus))
        self.state["gold"] += total
        self.state["fish"] = 0
        return total
    
    def upgrade(self, equip_type: str) -> tuple:
        """
        本地升级逻辑
        equip_type: 氧气瓶/伸缩爪/探测器/居酒屋
        返回：(是否成功, 消耗金币, 剧情描述)
        """
        costs = {
            "氧气瓶": 100,
            "伸缩爪": 120,
            "探测器": 80,
            "居酒屋": 500
        }
        
        keys = {
            "氧气瓶": "lvl_oxy",
            "伸缩爪": "lvl_retractable_claw",
            "探测器": "lvl_scan",
            "居酒屋": "lvl_inn"
        }
        
        if equip_type not in keys:
            return False, 0, "未知装备"
            
        lvl_key = keys[equip_type]
        current_lvl = self.state[lvl_key]
        
        if current_lvl >= 5:
            return False, 0, f"{equip_type}已达最高等级"
            
        cost = costs[equip_type]
        if self.state["gold"] < cost:
            return False, 0, f"金币不足（需 {cost} 金币）"
            
        # 执行升级
        self.state["gold"] -= cost
        self.state[lvl_key] += 1
        
        # 特殊效果更新
        if equip_type == "氧气瓶":
            self.state["oxygen_max"] = int(100 * (1 + 0.2 * self.state["lvl_oxy"]))
            self.state["oxygen"] = self.state["oxygen_max"]  # 升级补满氧气
            desc = f"🔧 **升级成功！** 氧气瓶升至 Lv.{self.state['lvl_oxy']}，消耗 {cost} 金币。氧气上限显著增加！"
        elif equip_type == "伸缩爪":
            desc = f"🔧 **升级成功！** 伸缩爪升至 Lv.{self.state['lvl_retractable_claw']}，消耗 {cost} 金币。捕获成功的概率增加了！"
        elif equip_type == "探测器":
            desc = f"🔧 **升级成功！** 探测器升至 Lv.{self.state['lvl_scan']}，消耗 {cost} 金币。探测到稀有奖励的概率变高了！"
        elif equip_type == "居酒屋":
            desc = f"🔧 **升级成功！** 居酒屋升至 Lv.{self.state['lvl_inn']}，消耗 {cost} 金币。以后卖鱼能赚更多钱了！"
        else:
            desc = f"🔧 **升级成功！** {equip_type}升至 Lv.{self.state[lvl_key]}，消耗 {cost} 金币。"
            
        return True, cost, desc
