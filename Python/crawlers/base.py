#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫基类模块
定义所有爬虫通用的方法和属性
"""

import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional


class CrawlerBase:
    """爬虫基类"""
    
    def __init__(self):
        # 请求头，模拟浏览器访问
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        # 请求间隔时间（秒），防止请求过快
        self.request_interval = 1
        # 会话对象，保持连接
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def make_request(self, url: str, timeout: int = 30) -> Optional[requests.Response]:
        """
        发送HTTP请求
        :param url: 请求URL
        :param timeout: 超时时间
        :return: Response对象或None
        """
        try:
            # 请求前等待
            time.sleep(self.request_interval)
            
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()  # 检查请求是否成功
            return response
        except requests.RequestException as e:
            print(f"请求失败: {url}, 错误信息: {str(e)}")
            return None
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """
        解析HTML内容
        :param html_content: HTML字符串
        :return: BeautifulSoup对象
        """
        return BeautifulSoup(html_content, 'lxml')
    
    def crawl(self, url: str = None) -> List[Dict]:
        """
        爬取方法，子类必须实现
        :param url: 可选的自定义URL
        :return: 爬取的数据列表
        """
        raise NotImplementedError("子类必须实现crawl方法")
    
    def get_platform_name(self) -> str:
        """
        获取平台名称
        :return: 平台名称
        """
        raise NotImplementedError("子类必须实现get_platform_name方法")
    
    def get_default_url(self) -> str:
        """
        获取默认爬取URL
        :return: 默认URL
        """
        raise NotImplementedError("子类必须实现get_default_url方法")
    
    @staticmethod
    def format_number(num_str: str) -> int:
        """
        格式化数字字符串，去除逗号等分隔符
        :param num_str: 数字字符串，如 "123,456"
        :return: 整数
        """
        if not num_str:
            return 0
        # 移除所有非数字字符（除了负号）
        cleaned = ''.join(c for c in num_str.strip() if c.isdigit() or c == '-')
        try:
            return int(cleaned)
        except ValueError:
            return 0
    
    @staticmethod
    def get_current_time() -> str:
        """
        获取当前时间字符串
        :return: 格式化的时间字符串
        """
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
