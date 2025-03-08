#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from dataclasses import dataclass
from datetime import datetime
from database.models import init_db

class QinglongPanel:
    def __init__(self):
        self.conn = init_db()
        self.panel_url = None
        self.client_id = None
        self.client_secret = None
        self.token = None
        self.load_config()
    
    def load_config(self):
        """加载青龙面板配置"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT panel_url, client_id, client_secret, token FROM qinglong_config ORDER BY id DESC LIMIT 1"
            )
            result = cursor.fetchone()
            
            if result:
                self.panel_url = result[0]
                self.client_id = result[1]
                self.client_secret = result[2]
                self.token = result[3]
                
        except Exception as e:
            print(f"加载配置失败: {str(e)}")
    
    def save_config(self, panel_url: str, client_id: str, client_secret: str):
        """保存青龙面板配置"""
        try:
            # 获取token
            response = requests.get(
                f"{panel_url}/open/auth/token",
                headers={
                    'Content-Type': 'application/json'
                },
                params={
                    'client_id': client_id,
                    'client_secret': client_secret
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"获取token失败: {response.text}")
                
            data = response.json()
            if data.get('code') != 200:
                error_msg = data.get('message', '') or data.get('msg', '') or response.text
                raise Exception(f"获取token失败: {error_msg}")
                
            token = data['data']['token']
            # print(f"获取token成功: {token}")
            # 保存到数据库
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO qinglong_config (panel_url, client_id, client_secret, token) VALUES (?, ?, ?, ?)",
                (panel_url, client_id, client_secret, token)
            )
            self.conn.commit()
            
            # 更新实例变量
            self.panel_url = panel_url
            self.client_id = client_id
            self.client_secret = client_secret
            self.token = token
            
            return token
            
        except Exception as e:
            raise Exception(f'保存配置失败：{str(e)}')
    
    def get_envs(self):
        """获取环境变量列表"""
        if not all([self.panel_url, self.token]):
            raise Exception('请先配置青龙面板信息')
            
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{self.panel_url}/open/envs", headers=headers)
        if response.status_code != 200:
            raise Exception(f"获取环境变量失败: {response.text}")
            
        data = response.json()
        if data.get('code') != 200:
            error_msg = data.get('message', '') or data.get('msg', '') or response.text
            raise Exception(f"获取环境变量失败: {error_msg}")
            
        return data['data']
    
    def update_env(self, env_id: int, name: str, value: str, remarks: str = ''):
        """更新环境变量"""
        if not all([self.panel_url, self.token]):
            raise Exception('请先配置青龙面板信息')
            
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.put(
            f"{self.panel_url}/open/envs",
            headers=headers,
            json={
                'id': env_id,
                'name': name,
                'value': value,
                'remarks': remarks
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"更新环境变量失败: {response.text}")
            
        data = response.json()
        if data.get('code') != 200:
            error_msg = data.get('message', '') or data.get('msg', '') or response.text
            raise Exception(f"更新环境变量失败: {error_msg}")

    def create_env(self, name: str, value: str, remarks: str = ''):
        """创建新的环境变量"""
        if not all([self.panel_url, self.token]):
            raise Exception('请先配置青龙面板信息')
            
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{self.panel_url}/open/envs",
            headers=headers,
            json=[{
                'name': name,
                'value': value,
                'remarks': remarks,
                'status': 0  # 设置为启用状态
            }]
        )
        
        if response.status_code != 200:
            raise Exception(f"创建环境变量失败: {response.text}")
            
        data = response.json()
        if data.get('code') != 200:
            error_msg = data.get('message', '') or data.get('msg', '') or response.text
            raise Exception(f"创建环境变量失败: {error_msg}")
    
    def enable_env(self, env_ids: list):
        """启用环境变量"""
        if not all([self.panel_url, self.token]):
            raise Exception('请先配置青龙面板信息')
            
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.put(
            f"{self.panel_url}/open/envs/enable",
            headers=headers,
            json=env_ids
        )
        
        if response.status_code != 200:
            raise Exception(f"启用环境变量失败: {response.text}")
            
        data = response.json()
        if data.get('code') != 200:
            error_msg = data.get('message', '') or data.get('msg', '') or response.text
            raise Exception(f"启用环境变量失败: {error_msg}")

    def sync_cookie(self, cookie_str: str, remarks: str = ''):
        """同步Cookie到青龙面板"""
        try:
            # 验证cookie格式
            if not ('pt_key=' in cookie_str and 'pt_pin=' in cookie_str):
                raise Exception('Cookie格式无效，必须包含pt_key和pt_pin')
            
            # 获取环境变量列表
            envs = self.get_envs()
            
            # 检查是否存在JD_COOKIE环境变量
            jd_cookies = [env for env in envs if env['name'] == 'JD_COOKIE']
            jd_cookies_with_remarks = [env for env in jd_cookies if env['remarks'] == remarks]
            
            if jd_cookies_with_remarks:
                # 获取当前变量的状态
                current_env = jd_cookies_with_remarks[0]
                
                # 更新已存在的环境变量
                self.update_env(
                    env_id=current_env['id'],
                    name='JD_COOKIE',
                    value=cookie_str,
                    remarks=remarks
                )
                
                # 如果变量是禁用状态，则启用它
                if current_env.get('status') == 1:
                    self.enable_env([current_env['id']])
            else:
                # 创建新的环境变量
                self.create_env(
                    name='JD_COOKIE',
                    value=cookie_str,
                    remarks=remarks
                )
                
        except Exception as e:
            raise Exception(f'同步Cookie失败：{str(e)}')
    
    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
    
    def get_env_list(self):
        """获取环境变量列表，主要是JD_COOKIE相关的变量"""
        try:
            # 获取所有环境变量
            envs = self.get_envs()
            # 过滤出JD_COOKIE相关的变量
            jd_cookies = [env for env in envs if env['name'] == 'JD_COOKIE']
            return jd_cookies
        except Exception as e:
            raise Exception(f'获取环境变量列表失败：{str(e)}')