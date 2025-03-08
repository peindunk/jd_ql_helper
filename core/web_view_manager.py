#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

class WebViewManager:
    def __init__(self):
        self.web_view = QWebEngineView()
        self.init_web_view()
    
    def init_web_view(self):
        """初始化WebView"""
        self.web_view.setUrl(QUrl('https://m.jd.com'))
    
    def get_web_view(self) -> QWebEngineView:
        """获取WebView实例"""
        return self.web_view
    
    def reload_page(self):
        """刷新当前页面"""
        self.web_view.reload()
    
    def load_url(self, url: str):
        """加载指定URL"""
        self.web_view.setUrl(QUrl(url))
    
    def go_back(self):
        """返回上一页"""
        self.web_view.back()
    
    def go_forward(self):
        """前进到下一页"""
        self.web_view.forward()
    
    def stop_loading(self):
        """停止加载"""
        self.web_view.stop()