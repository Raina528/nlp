"""

"""
import gradio as gr
from components import create_header, create_status_bar, create_chatbox, create_upgrade_panel, create_backpack, create_quick_actions
from game_controller_memory import GameControllerMemory


def main():
    """创建主界面"""
    
    # 初始化游戏控制器（使用带记忆版本）
    controller = GameControllerMemory()
    
    # 自定义 CSS：禁用滚动条，限制页面高度
    custom_css = """
    body {
        overflow: hidden;
    }
    .gradio-container {
        overflow: hidden !important;
        max-height: 100vh !important;
    }
    .text-center {
        text-align: center !important;
        width: 100% !important;
    }
    
    /* 发送按钮 - 加高并增大字号 */
    .big-send-btn {
        height: 40px !important;
        margin-top: 10px !important;
    }
    
    /* 右侧功能区域高度控制 - 比例 2:2:3 */
    .action-panel {
        max-height: calc(100vh / 7 * 2) !important;
    }
    .upgrade-panel {
        max-height: calc(100vh / 7 * 2) !important;
    }
    .backpack-panel {
        max-height: calc(100vh / 7 * 3) !important;
    }
    
    /* 全部卖出按钮 - 长但窄的横向按钮 */
    .long-sell-btn {
        width: 100% !important;
        height: 32px !important;
        font-size: 13px !important;
        white-space: nowrap !important;
    }
    
    /* 通知提示（8秒后消失） */
    .notification-toast {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
        color: white !important;
        padding: 8px 16px !important;
        border-radius: 6px !important;
        margin: 5px 10px !important;
        text-align: center !important;
        font-weight: bold !important;
        font-size: 14px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
        animation: fadeOut 0.5s ease 7.5s forwards !important; /* 7.5秒后开始淡出，持续0.5秒 */
    }
    .notification-toast.warning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
    }
    
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; visibility: hidden; }
    }
    """
    
    # 定义回调函数
    def respond(message, history, action_type=None):
        """处理用户输入（仅剧情流式输出）"""
        if not message or message.strip() == "":
            return history, "", update_status(), update_backpack()
        
        # 将 action_type 转换为 AI 能理解的操作
        action_map = {
            "dive": "下潜",
            "detect": "探测",
            "catch": "捕获",
            "return": "撤离"
        }
        
        if action_type and action_type in action_map:
            action = action_map[action_type]
        else:
            action = message.strip()
        
        # 1. 先显示用户消息和“思考中”占位符
        history.append({"role": "user", "content": message})
        ai_response_placeholder = {"role": "assistant", "content": "✨ 阿柴正在努力组织中..."}
        history.append(ai_response_placeholder)
        yield history, "", update_status(), update_backpack()
        
        # 2. 开始流式获取剧情（此时只更新聊天框，不刷新状态栏以保持界面稳定）
        for partial_response in controller.stream_player_action(action):
            ai_response_placeholder["content"] = partial_response
            # 【关键】这里只 yield 聊天框的实时变化，状态栏和背包保持原样
            yield history, "", gr.update(), gr.update()
        
        # 3. 剧情全部蹦完后，再统一更新状态栏和背包
        
        # --- 前端强制检查：氧气是否耗尽 ---
        if controller.game.energy <= 0:
            fail_drama = (
                "这次海底探险让阿柴玩的很开心，完全没注意到氧气表的指针不断下跌。"
                "当警报声在耳边炸响的时候，氧气已经彻底耗尽，它眼前一黑朝着海底坠去。"
                "就在意识即将消散的时候，一阵温暖的浮力托住了它，阿柴迷迷糊糊睁开眼，"
                "看见一条蓝鲸正用尾巴轻柔地将自己托着，朝着海面缓缓上升..."
                "不过在岸边醒来阿柴才发现自己的捕到的鱼弄丢了。"
            )
            # 执行重置逻辑：深度归零、氧气补满、清空背包（鱼）、金币不变
            controller.game.state["depth"] = 0
            controller.game.state["oxygen"] = controller.game.state["oxygen_max"]
            controller.game.state["fish"] = 0
            
            # 将剧情追加到聊天框
            history.append({"role": "assistant", "content": fail_drama})
            yield history, "", update_status(), update_backpack()
            return

        yield history, "", update_status(), update_backpack()

    def reset_game():
        """重置游戏"""
        print("重置游戏...")
        controller.reset_game_state()
        first_scene = controller.generate_first_scene()
        history = [
            {"role": "assistant", "content": controller.initial_narrative},
            {"role": "assistant", "content": first_scene}
        ]
        return history, "", update_status(), update_backpack()
    
    def update_status():
        """更新状态栏"""
        game = controller.game
        hall_names = ["路边摊", "小木屋", "温馨小店", "人气食堂", "名店", "柴 - 极味"]
        
        full_html = f'''
        <div style="background:linear-gradient(135deg, #2d3748 0%, #1a202c 100%); padding:12px 20px; border-radius:8px; margin:5px 10px; color:white; white-space:nowrap; width:calc(100% - 20px); display:flex; justify-content:space-between; align-items:center">
            <div style="display:flex; gap:8px">
                <span style="color:#fbbf24;font-weight:bold">📊 状态</span>
                <span style="color:#94a3b8">深度:</span><span style="color:#fff;font-weight:bold">{game.depth}m</span>
                <span style="color:#94a3b8">氧气:</span><span style="color:{'#ef4444' if game.energy < 20 else '#fff'};font-weight:bold">{game.energy}%</span>
                <span style="color:#94a3b8">金币:</span><span style="color:#fff;font-weight:bold">{game.gold}</span>
                <span style="color:#94a3b8">居酒屋:</span><span style="color:#fff;font-weight:bold">Lv.{game.hall_level}</span>
            </div>

            <div style="display:flex; gap:8px">
                <span style="color:#fbbf24;font-weight:bold">🎒 装备</span>
                <span style="color:#94a3b8">氧气瓶:</span><span style="color:#fff;font-weight:bold">Lv.{game.equipment['energy_bottle']}</span>
                <span style="color:#94a3b8">伸缩爪:</span><span style="color:#fff;font-weight:bold">Lv.{game.equipment['catcher']}</span>
                <span style="color:#94a3b8">探测器:</span><span style="color:#fff;font-weight:bold">Lv.{game.equipment['detector']}</span>
            </div>
        </div>
        '''
        return full_html
    
    def update_backpack():
        """更新背包显示（固定网格）"""
        game = controller.game
        rows = 5  # 固定行数
        cols = 6  # 固定列数
        cell_size = 34
        grid_height = cell_size * rows + 4
        
        # 生成物品字典
        items = {}
        for idx, fish in enumerate(game.inventory):
            row = idx // cols
            col = idx % cols
            if row < rows:
                items[(row, col)] = fish
        
        grid_html = f'<div id="backpack-grid" style="display:grid;grid-template-columns:repeat({cols},{cell_size}px);gap:2px">'
        
        for row in range(rows):
            for col in range(cols):
                item_key = (row, col)
                
                if item_key in items:
                    item = items[item_key]
                    icon = item.get('icon', '❓')
                    grid_html += f'''
                    <div style="width:{cell_size}px;height:{cell_size}px;background:#2d3748;border:2px solid #4a5568;border-radius:4px;position:relative;display:flex;align-items:center;justify-content:center;font-size:1.5em">
                        {icon}
                    </div>
                    '''
                else:
                    grid_html += f'''
                    <div style="width:{cell_size}px;height:{cell_size}px;background:#2d3748;border:1px solid #4a5568;border-radius:4px"></div>
                    '''
        
        grid_html += '</div>'
        
        scroll_container_html = f'''
        <div style="overflow-y:auto; max-height:{grid_height}px; background:#1a202c; border-radius:6px;">
            {grid_html}
        </div>
        '''
        
        return scroll_container_html
    
    def sell_all_fish(history):
        """卖出所有鱼类（本地响应，不加入聊天）"""
        msg = controller.local_action("全部卖出")
        return history, update_status(), update_backpack(), msg

    def upgrade_equipment(equip_name, history):
        """升级装备（本地响应，不加入聊天）"""
        msg = controller.local_action(f"升级{equip_name}")
        return history, update_status(), update_backpack(), msg
    
    def show_notification(msg):
        """显示通知（8秒后自动消失）"""
        css_class = "notification-toast" if "成功" in msg else "notification-toast warning"
        html = f'<div class="{css_class}">{msg}</div>'
        # 使用 gr.update 的 timer 属性实现延时隐藏
        return html, gr.update(visible=True)

    def action_a():
        return "A"
    def action_b():
        return "B"
    def action_c():
        return "C"
    def action_d():
        return "D"
    
    # 创建 Blocks 布局
    with gr.Blocks() as demo:
        
        # ============ 顶部标题栏 ============
        header, title = create_header()
        
        # ============ 状态栏 ============
        status_row, status_display = create_status_bar()
        
        # ============ 中间内容区域 ============
        with gr.Row():
            # 左侧：对话框
            chat_container, chatbot, input_box, send_btn = create_chatbox()
            
            # 右侧：功能区域
            with gr.Column(scale=2):

                # 右上侧：快捷指令面板（约 25% 宽）
                action_container, action_title, dive_btn, detect_btn, capture_btn, extract_btn = create_quick_actions()
                    
                # 右上侧：升级面板
                upgrade_container, equipment_components, izakaya_btn = create_upgrade_panel()
                
                # 通知提示（用于显示升级/卖鱼结果）
                notification = gr.Markdown(visible=False)
                
                # 右下部分：背包
                backpack_container, backpack_display, sell_all_btn = create_backpack()
        
        # ============ 绑定事件 ============
        # 文本输入框绑定（支持流式）
        send_btn.click(respond, [input_box, chatbot], [chatbot, input_box, status_display, backpack_display])
        input_box.submit(respond, [input_box, chatbot], [chatbot, input_box, status_display, backpack_display])
        
        # 快捷指令按钮绑定（直接调用流式 respond 函数，避免 .then() 导致的生成器识别错误）
        dive_btn.click(
            lambda: ("下潜", "dive"), 
            None, 
            [input_box, gr.State(value="dive")]
        ).then(
            respond, 
            [input_box, chatbot, gr.State(value="dive")], 
            [chatbot, input_box, status_display, backpack_display]
        )
        detect_btn.click(
            lambda: ("探测", "detect"), 
            None, 
            [input_box, gr.State(value="detect")]
        ).then(
            respond, 
            [input_box, chatbot, gr.State(value="detect")], 
            [chatbot, input_box, status_display, backpack_display]
        )
        capture_btn.click(
            lambda: ("捕获", "catch"), 
            None, 
            [input_box, gr.State(value="catch")]
        ).then(
            respond, 
            [input_box, chatbot, gr.State(value="catch")], 
            [chatbot, input_box, status_display, backpack_display]
        )
        extract_btn.click(
            lambda: ("撤离", "return"), 
            None, 
            [input_box, gr.State(value="return")]
        ).then(
            respond, 
            [input_box, chatbot, gr.State(value="return")], 
            [chatbot, input_box, status_display, backpack_display]
        )
        
        # 卖鱼按钮绑定（本地响应，显示通知）
        sell_all_btn.click(
            sell_all_fish,
            [chatbot],
            [chatbot, status_display, backpack_display, notification]
        ).then(
            show_notification,
            [notification],
            [notification, notification]
        )
        
        # 升级按钮绑定（本地响应，显示通知）
        oxygen_tank_btn = equipment_components["oxygen_tank"]
        claw_btn = equipment_components["claw"]
        detector_btn = equipment_components["detector"]
        izakaya_btn_main = equipment_components["izakaya"]
        
        def upgrade_and_notify(name, hist):
            msg = controller.local_action(f"升级{name}")
            return hist, update_status(), update_backpack(), msg
            
        for btn, name in [
            (oxygen_tank_btn, "氧气瓶"),
            (claw_btn, "伸缩爪"),
            (detector_btn, "探测器"),
            (izakaya_btn_main, "居酒屋")
        ]:
            btn.click(
                lambda h, n=name: upgrade_and_notify(n, h),
                [chatbot],
                [chatbot, status_display, backpack_display, notification]
            ).then(
                show_notification,
                [notification],
                [notification, notification]
            )
        
        # 页面加载时启动游戏
        demo.load(reset_game, None, [chatbot, input_box, status_display, backpack_display])
    
    # 启动服务
    demo.launch(
        server_name="0.0.0.0",
        server_port=7869,
        inbrowser=True,
        css=custom_css
    )


if __name__ == "__main__":
    main()
