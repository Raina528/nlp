"""
对话框组件 - 带滚动条的聊天界面
"""
import gradio as gr


def create_chatbox():
    """
    创建对话框组件

    Returns:
        tuple: (chat_container, chatbot, input_box, send_btn)
    """

    # 外层容器添加类，与主界面 CSS 中的 .chat-column 对应
    with gr.Column(scale=3) as chat_container:  # ← scale=3，占 3 份宽度
        # 聊天机器人：移除固定高度，添加类让 CSS 控制高度
        chatbot = gr.Chatbot(
            height="61vh",
            label="冒险事件",
            show_label=True,
            elem_classes=["chatbot"]  # 主界面 CSS 会设置 height:100%
        )

        # 输入区域
        with gr.Row():
            input_box = gr.Textbox(
                placeholder="请输入...",
                lines=1,
                max_lines=1,  # 固定 2 行高度，超出自动滚动
                show_label=False,
                scale=4  # ← 占 4 份宽度
            )

            send_btn = gr.Button(
                "🐾 对话",
                variant="primary",
                size="lg",
                scale=1,
                elem_classes=["big-send-btn"]  # ← 自定义 CSS 类
            )

    return chat_container, chatbot, input_box, send_btn