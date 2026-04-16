"""
升级面板组件
"""
import gradio as gr


def get_upgrade_cost(equipment_name):
    """
    获取装备升级消耗值（固定值）
    
    Args:
        equipment_name: 装备名称
        
    Returns:
        int: 升级消耗值
    """
    cost_map = {
        "氧气瓶": 100,
        "伸缩爪": 120,
        "探测器": 80,
        "居酒屋": 500
    }
    return cost_map.get(equipment_name, 0)


def create_upgrade_panel():
    """
    创建升级面板（与快捷指令面板大小相近）
    
    Returns:
        tuple: (upgrade_container, equipment_dict, izakaya_btn)
    """
    
    # 用一个容器包裹所有内容
    with gr.Column(scale=1, elem_classes=["upgrade-panel"]) as upgrade_container:
        
        # 标题
        gr.Markdown("### 🔧 升级", show_label=False)
        
        # 一排小按钮 - 所有装备横向排列
        with gr.Row():
            oxygen_tank_btn = gr.Button(
                f"🫧 氧气瓶\n升级 [{get_upgrade_cost('氧气瓶')}]",
                variant="secondary",
                size="sm"
            )
            
            claw_btn = gr.Button(
                f"🦾 伸缩爪\n升级 [{get_upgrade_cost('伸缩爪')}]",
                variant="secondary",
                size="sm"
            )
            
            detector_btn = gr.Button(
                f"📡 探测器\n升级 [{get_upgrade_cost('探测器')}]",
                variant="secondary",
                size="sm"
            )
            
            izakaya_btn = gr.Button(
                f"🏮 居酒屋\n升级 [{get_upgrade_cost('居酒屋')}]",
                variant="primary",
                size="sm"
            )
    
    # 简化的组件字典
    equipment_components = {
        "oxygen_tank": oxygen_tank_btn,
        "claw": claw_btn,
        "detector": detector_btn,
        "izakaya": izakaya_btn
    }
    
    return upgrade_container, equipment_components, izakaya_btn
