"""
快捷指令面板组件
"""
import gradio as gr


def get_action_cost(action_name):
    """
    获取动作消耗值
    
    Args:
        action_name: 动作名称
        
    Returns:
        int: 消耗值
    """
    # TODO: 这里可以调用实际的函数来获取消耗值
    # 现在是示例数据
    cost_map = {
        "下潜": 10,
        "探测": 10,
        "捕获": 15,
        "撤离": 20
    }
    return cost_map.get(action_name, 0)


def create_quick_actions():
    """
    创建快捷指令面板
    
    Returns:
        tuple: (action_container, title, dive_btn, detect_btn, capture_btn, extract_btn)
    """
    
    with gr.Column(scale=1, elem_classes=["action-panel"]) as action_container:
        # 标题
        title = gr.Markdown(
            value="### ⚡ 快捷指令",
            show_label=False
        )
        
        # 一排按钮布局（1x4）
        with gr.Row():
            dive_btn = gr.Button(
                f"🌊 下潜\n消耗 [{get_action_cost('下潜')}]",
                variant="secondary",
                size="sm"
            )
            
            detect_btn = gr.Button(
                f"🔍 探测\n消耗 [{get_action_cost('探测')}]",
                variant="secondary",
                size="sm"
            )
            
            capture_btn = gr.Button(
                f"🎯 捕获\n消耗 [{get_action_cost('捕获')}]",
                variant="secondary",
                size="sm"
            )
            
            extract_btn = gr.Button(
                f"🚁 撤离\n消耗 [{get_action_cost('撤离')}]",
                variant="stop",
                size="sm"
            )
    
    return action_container, title, dive_btn, detect_btn, capture_btn, extract_btn
