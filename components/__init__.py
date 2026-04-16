"""
UI 组件包
包含所有可复用的界面组件
"""

from components.header import create_header
from components.status_bar import create_status_bar
from components.chatbox import create_chatbox
from components.quick_actions import create_quick_actions
from components.upgrade_panel import create_upgrade_panel
from components.backpack import create_backpack

__all__ = [
    'create_header',
    'create_status_bar',
    'create_chatbox',
    'create_quick_actions',
    'create_upgrade_panel',
    'create_backpack',
]
