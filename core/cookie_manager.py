#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtNetwork import QNetworkCookie
from database.models import init_db
from urllib.parse import unquote

class CookieManager(QObject):
    cookies_updated = pyqtSignal(str)
    
    def __init__(self, web_view):
        super().__init__()
        self.web_view = web_view
        self.cookie_store = QWebEngineProfile.defaultProfile().cookieStore()
        self.cookie_store.cookieAdded.connect(self.on_cookie_added)
        self.cookies = {}
        self.is_logged_in = False
        self.conn = init_db()
        self.load_saved_cookies()
        self.web_view.urlChanged.connect(self.check_login_status)
    
    def check_login_status(self, url):
        # 检查是否存在pt_key和pt_pin这两个关键Cookie
        if 'pt_key' in self.cookies and 'pt_pin' in self.cookies:
            self.is_logged_in = True
        else:
            self.is_logged_in = False
    
    def clear_cookies(self):
        self.cookies = {}
        self.update_cookie_text()
        # 清除数据库中保存的Cookie
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM jd_cookie WHERE status = 'active'")
        self.conn.commit()
    
    def on_cookie_added(self, cookie):
        domain = cookie.domain()
        if '.jd.com' in domain:
            name = cookie.name().data().decode()
            value = cookie.value().data().decode()
            # 对Cookie值进行URL解码
            if name == 'pt_pin':
                value = unquote(value)
            self.cookies[name] = value
            self.update_cookie_text()
            self.check_login_status(None)
    
    def update_cookie_text(self):
        cookie_str = ''
        for name, value in self.cookies.items():
            cookie_str += f"{name}={value}; "
        self.cookies_updated.emit(cookie_str)
        
        # 如果已登录，保存Cookie到数据库
        if self.is_logged_in and 'pt_pin' in self.cookies:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO jd_cookie (user_pin, cookie, status) VALUES (?, ?, ?)",
                (self.cookies['pt_pin'], cookie_str, 'active')
            )
            self.conn.commit()
    
    def load_saved_cookies(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT cookie FROM jd_cookie WHERE status = 'active' LIMIT 1")
            result = cursor.fetchone()
            
            if result:
                cookie_str = result[0]
                for cookie_item in cookie_str.split('; '):
                    if '=' in cookie_item:
                        name, value = cookie_item.split('=', 1)
                        # 对pt_pin进行URL解码
                        if name == 'pt_pin':
                            value = unquote(value)
                        self.cookies[name] = value
                        # 将Cookie添加到WebView的CookieStore中
                        cookie = QNetworkCookie(name.encode(), value.encode())
                        cookie.setDomain('.jd.com')
                        cookie.setPath('/')
                        self.cookie_store.setCookie(cookie)
                self.update_cookie_text()
                self.check_login_status(None)
        except Exception as e:
            print(f"加载Cookie失败: {str(e)}")
            
    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
    
    def get_formatted_cookie(self):
        return '; '.join([f"{name}={value}" for name, value in self.cookies.items()])+';'
    
    def get_essential_cookies(self):
        """获取必要的Cookie（仅pt_key和pt_pin）"""
        return '; '.join([f"{name}={value}" for name, value in self.cookies.items() if name in ['pt_key', 'pt_pin']])+';'