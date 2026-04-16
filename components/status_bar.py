"""
状态栏组件 - 极简版本
"""
import gradio as gr


def create_status_bar():
    """
    创建长条形状态栏（初始显示，后续通过 gr.HTML 更新）

    Returns:
        tuple: (status_row, status_display)
    """

    # 初始数据
    initial_status = {
        "depth": 0,
        "oxygen": 100,
        "gold": 0,
        "izakaya_level": 0
    }

    initial_equipment = {
        "oxygen_tank": 0,
        "claw": 0,
        "detector": 0
    }

    # 构建完整的状态栏 HTML（一行显示所有内容）
    full_html = f'''
    <div style="background:linear-gradient(135deg, #2d3748 0%, #1a202c 100%); padding:12px 20px; border-radius:8px; margin:5px 10px; color:white; white-space:nowrap; width:calc(100% - 20px); display:flex; justify-content:space-between; align-items:center">
        <div style="display:flex; gap:8px">
            <span style="color:#fbbf24;font-weight:bold">📊 状态</span>
            <span style="color:#94a3b8">深度:</span><span style="color:#fff;font-weight:bold">{initial_status["depth"]}m</span>
            <span style="color:#94a3b8">氧气:</span><span style="color:#fff;font-weight:bold">{initial_status["oxygen"]}%</span>
            <span style="color:#94a3b8">金币:</span><span style="color:#fff;font-weight:bold">{initial_status["gold"]}</span>
            <span style="color:#94a3b8">居酒屋:</span><span style="color:#fff;font-weight:bold">Lv.{initial_status["izakaya_level"]}</span>
        </div>

        <div style="display:flex; gap:8px">
            <span style="color:#fbbf24;font-weight:bold">🎒 装备</span>
            <span style="color:#94a3b8">氧气瓶:</span><span style="color:#fff;font-weight:bold">Lv.{initial_equipment["oxygen_tank"]}</span>
            <span style="color:#94a3b8">伸缩爪:</span><span style="color:#fff;font-weight:bold">Lv.{initial_equipment["claw"]}</span>
            <span style="color:#94a3b8">探测器:</span><span style="color:#fff;font-weight:bold">Lv.{initial_equipment["detector"]}</span>
        </div>
    </div>
    '''

    # 创建一个 Row 容器来放置状态栏
    with gr.Row() as status_row:
        status_display = gr.HTML(
            value=full_html,
            show_label=False
        )

    return status_row, status_display