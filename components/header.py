"""
顶部标题栏组件
"""
import gradio as gr


def create_header():
    """
    创建居中的游戏标题

    Returns:
        tuple: (header_row, title_html)
    """

    # 简单的居中标题
    with gr.Row() as header:
        title = gr.Markdown(
            value="# 柴犬潜水员：深海珍味",
            elem_classes=["text-center"]
        )

    return header, title