#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""JD Cookie 助手

一个用于获取京东Cookie并同步到青龙面板的图形化工具

version: v1.0
author: Payne
date: 2025-03-07
"""

import sys
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QLineEdit, QMessageBox, QDialog
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QIcon
from database.models import init_db

from core.cookie_manager import CookieManager
from core.qinglong_panel import QinglongPanel
from core.web_view_manager import WebViewManager

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('关于')
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # 读取关于信息
        try:
            # 获取应用程序的基础路径
            import os
            import sys
            
            if getattr(sys, 'frozen', False):
                # 如果是打包后的应用
                base_path = sys._MEIPASS
            else:
                # 如果是开发环境
                base_path = os.path.abspath(".")
            
            about_file_path = os.path.join(base_path, 'about', 'about.txt')
            with open(about_file_path, 'r', encoding='utf-8') as f:
                about_text = f.read()
        except Exception as e:
            about_text = f'无法读取关于信息: {str(e)}'
        
        # 显示关于信息
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setText(about_text)
        layout.addWidget(text_edit)
        
        # 确定按钮
        ok_button = QPushButton('确定')
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)
        
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 设置应用图标
        icon = QIcon('assets/app_icon.png')
        self.setWindowIcon(icon)
        
        # 初始化各个管理器
        self.web_view_manager = WebViewManager()
        self.cookie_manager = CookieManager(self.web_view_manager.get_web_view())
        self.qinglong_panel = QinglongPanel()
        
        # 初始化数据库连接
        self.conn = init_db()
        
        self.init_ui()
        # 加载保存的配置
        self.load_config()

    def init_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle('JD Cookie-- 青龙助手')
        self.setMinimumSize(1000, 800)

        # 创建中心部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # 创建左侧WebView区域
        web_layout = QVBoxLayout()
        web_view = self.web_view_manager.get_web_view()
        web_layout.addWidget(web_view)
        
        # 添加刷新按钮
        refresh_button = QPushButton('刷新页面')
        refresh_button.clicked.connect(self.web_view_manager.reload_page)
        web_layout.addWidget(refresh_button)
        
        # 连接Cookie更新信号
        self.cookie_manager.cookies_updated.connect(self.update_cookie_display)

        # 创建右侧控制面板
        control_layout = QVBoxLayout()
        
        # Cookie显示区域
        cookie_group = QWidget()
        cookie_layout = QVBoxLayout(cookie_group)
        cookie_layout.addWidget(QLabel('Cookie信息：'))
        self.cookie_text = QTextEdit()
        self.cookie_text.setReadOnly(True)
        cookie_layout.addWidget(self.cookie_text)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        self.copy_button = QPushButton('复制Cookie')
        self.sync_button = QPushButton('同步到青龙面板')
        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.sync_button)
        cookie_layout.addLayout(button_layout)
        
        # 青龙面板配置区域
        config_group = QWidget()
        config_layout = QVBoxLayout(config_group)
        config_layout.addWidget(QLabel('青龙面板配置：'))
        
        # 添加配置输入框
        self.panel_url = QLineEdit()
        self.panel_url.setPlaceholderText('青龙面板地址 (例如: http://localhost:5700)')
        config_layout.addWidget(self.panel_url)
        
        client_id_layout = QHBoxLayout()
        client_id_layout.addWidget(QLabel('Client ID:'))
        self.client_id = QLineEdit()
        client_id_layout.addWidget(self.client_id)
        config_layout.addLayout(client_id_layout)
        
        client_secret_layout = QHBoxLayout()
        client_secret_layout.addWidget(QLabel('Client Secret:'))
        self.client_secret = QLineEdit()
        client_secret_layout.addWidget(self.client_secret)
        config_layout.addLayout(client_secret_layout)
        
        self.panel_token = QLineEdit()
        self.panel_token.setPlaceholderText('青龙面板Token (自动获取)')
        self.panel_token.setReadOnly(True)
        config_layout.addWidget(self.panel_token)
        
        # 保存配置按钮
        self.save_config = QPushButton('保存配置')
        config_layout.addWidget(self.save_config)

        # 添加环境变量列表区域
        env_group = QWidget()
        env_layout = QVBoxLayout(env_group)
        env_header_layout = QHBoxLayout()
        env_layout.addWidget(QLabel('JD_COOKIE环境变量列表：'))
        self.refresh_env_button = QPushButton('刷新列表')
        env_header_layout.addStretch()
        env_header_layout.addWidget(self.refresh_env_button)
        env_layout.addLayout(env_header_layout)
        
        self.env_text = QTextEdit()
        self.env_text.setReadOnly(True)
        env_layout.addWidget(self.env_text)

        # 将各个区域添加到控制面板
        control_layout.addWidget(cookie_group)
        control_layout.addWidget(config_group)
        control_layout.addWidget(env_group)

        # 添加关于按钮
        about_button = QPushButton('关于')
        about_button.clicked.connect(self.show_about_dialog)
        control_layout.addWidget(about_button)

        # 设置布局比例
        main_layout.addLayout(web_layout, 7)
        main_layout.addLayout(control_layout, 3)

        # 连接信号槽
        self.setup_connections()

    def setup_connections(self):
        # 这里先只连接基本的信号槽，具体实现后续添加
        self.copy_button.clicked.connect(self.copy_cookie)
        self.sync_button.clicked.connect(self.sync_to_panel)
        self.save_config.clicked.connect(self.save_panel_config)
        # 连接刷新环境变量列表按钮的信号
        self.refresh_env_button.clicked.connect(self.refresh_env_list)

    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def update_cookie_display(self, cookie_str):
        self.cookie_text.setText(cookie_str)
    
    def copy_cookie(self):
        cookie_str = self.cookie_manager.get_formatted_cookie()
        if cookie_str:
            clipboard = QApplication.clipboard()
            clipboard.setText(cookie_str)
            QMessageBox.information(self, '成功', 'Cookie已复制到剪贴板')
        else:
            QMessageBox.warning(self, '警告', '没有可用的Cookie')

    def sync_to_panel(self):
        try:
            # 获取必要的Cookie（仅pt_key和pt_pin）
            cookie_str = self.cookie_manager.get_essential_cookies()
            if not cookie_str:
                raise Exception('请先获取有效的Cookie')
            
            # 从cookie中提取pt_pin作为备注
            current_pin = self.cookie_manager.cookies.get('pt_pin', '')
            
            # 同步到青龙面板
            self.qinglong_panel.sync_cookie(
                cookie_str=cookie_str,
                remarks=current_pin
            )
            
            QMessageBox.information(self, '成功', 'Cookie已成功同步到青龙面板')
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'同步失败：{str(e)}')

    def save_panel_config(self):
        try:
            panel_url = self.panel_url.text().strip()
            client_id = self.client_id.text().strip()
            client_secret = self.client_secret.text().strip()
            
            if not all([panel_url, client_id, client_secret]):
                raise Exception('请填写完整的青龙面板配置信息')
            
            # 保存配置并获取token
            token = self.qinglong_panel.save_config(panel_url, client_id, client_secret)
            
            # 更新token显示
            self.panel_token.setText(token)
            
            QMessageBox.information(self, '成功', '青龙面板配置已保存')
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存配置失败：{str(e)}')
    
    def load_config(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT panel_url, client_id, client_secret, token FROM qinglong_config LIMIT 1"
            )
            result = cursor.fetchone()
            
            if result:
                self.panel_url.setText(result[0])
                self.client_id.setText(result[1])
                self.client_secret.setText(result[2])
                self.panel_token.setText(result[3])
                
        except Exception as e:
            print(f"加载配置失败: {str(e)}")
    
    def closeEvent(self, event):
        if self.conn:
            self.conn.close()
        event.accept()

    def refresh_env_list(self):
        """刷新环境变量列表"""
        try:
            env_vars = self.qinglong_panel.get_env_list()
            if env_vars:
                # 格式化环境变量信息
                env_text = ''
                for env in env_vars:
                    # 转换时间戳为可读格式
                    update_time = env.get('updatedAt')
                    dt = datetime.fromisoformat(update_time.replace('Z', '+00:00'))
                    update_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                    env_text += f"名称: {env['name']}\n"
                    env_text += f"备注: {env.get('remarks', '无')}\n"
                    env_text += f"状态: {'已启用' if env['status'] == 0 else '已禁用'}\n"
                    env_text += f"更新时间: {update_time}\n"
                    env_text += '-' * 50 + '\n'
                
                self.env_text.setText(env_text)
            else:
                self.env_text.setText('暂无环境变量')
                
        except Exception as e:
            self.env_text.setText(f'获取环境变量失败: {str(e)}')

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()