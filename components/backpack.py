""" 
背包组件 - 游戏风格的物品栏
"""
import gradio as gr


def create_backpack():
    """
    创建背包界面（网格状物品栏）
    
    Returns:
        tuple: (backpack_container, grid_html)
    """
    
    # 背包配置
    rows = 10  # 10 行
    cols = 12  # 12 列
    cell_size = 34  # 每格大小 34px
    
    # 初始为空背包
    items = {}
    
    # 生成背包网格 HTML（初始空）
    grid_height = cell_size * 2 + 4  # 最多显示 2 行的高度
    
    grid_html = f'<div id="backpack-grid" style="display:grid;grid-template-columns:repeat({cols},{cell_size}px);gap:2px">'
    
    for row in range(rows):
        for col in range(cols):
            # 空格子
            grid_html += f'''
            <div style="width:{cell_size}px;height:{cell_size}px;background:#2d3748;border:1px solid #4a5568;border-radius:4px"></div>
            '''
    
    grid_html += '</div>'
    
    # 创建带滚动条的容器包裹网格（初始空）
    scroll_container_html = f'''
    <div style="overflow-y:auto; max-height:{grid_height}px; background:#1a202c; border-radius:6px;">
        {grid_html}
    </div>
    '''
    
    # 创建背包容器
    with gr.Column(scale=1, elem_classes=["backpack-panel"]) as backpack_container:
        gr.Markdown("### 🎒 背包", show_label=False)
        
        # 上侧：滚动物品框
        backpack_display = gr.HTML(
            value=scroll_container_html,
            show_label=False
        )
        
        # 下侧：全部卖出按钮（长但窄）
        sell_all_btn = gr.Button(
            "💰 全部卖出",
            variant="stop",
            size="sm",
            elem_classes=["long-sell-btn"]
        )
    
    return backpack_container, backpack_display, sell_all_btn
