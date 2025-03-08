from dataclasses import dataclass
from datetime import datetime
import sqlite3
import json
import os

@dataclass
class QinglongConfig:
    id: int
    panel_url: str
    client_id: str
    client_secret: str
    token: str
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create_table(conn: sqlite3.Connection):
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS qinglong_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            panel_url TEXT NOT NULL,
            client_id TEXT NOT NULL,
            client_secret TEXT NOT NULL,
            token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()

@dataclass
class JdCookie:
    id: int
    user_pin: str
    cookie: str
    status: str  # 'active' or 'expired'
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create_table(conn: sqlite3.Connection):
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jd_cookie (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_pin TEXT NOT NULL,
            cookie TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()

def init_db():
    """初始化数据库连接和表结构"""
    # 获取用户文档目录路径
    docs_path = os.path.expanduser('~/Documents')
    # 创建jd_helper目录
    db_dir = os.path.join(docs_path, 'jd_helper')
    os.makedirs(db_dir, exist_ok=True)
    # 设置数据库文件路径
    db_path = os.path.join(db_dir, 'jd_helper.db')
    conn = sqlite3.connect(db_path)
    QinglongConfig.create_table(conn)
    JdCookie.create_table(conn)
    return conn