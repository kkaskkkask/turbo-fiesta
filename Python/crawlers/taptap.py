#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TapTap爬虫模块
用于爬取 taptap.cn 的热门游戏排行榜
"""

from typing import List, Dict
from .base import CrawlerBase
import json
import re


class TapTapCrawler(CrawlerBase):
    """TapTap爬虫"""
    
    def __init__(self):
        super().__init__()
        self.platform = 'taptap'
        # 修改请求头以适应TapTap
        self.headers.update({
            'Referer': 'https://www.taptap.cn/',
        })
        self.session.headers.update(self.headers)
    
    def get_platform_name(self) -> str:
        """获取平台名称"""
        return 'TapTap'
    
    def get_default_url(self) -> str:
        """获取默认爬取URL"""
        return 'https://www.taptap.cn/top/download'
    
    def crawl(self, url: str = None) -> List[Dict]:
        """
        爬取TapTap排行榜数据
        :param url: 自定义URL，默认为下载榜
        :return: 游戏数据列表
        """
        target_url = url if url else self.get_default_url()
        results = []
        
        # 发送请求
        response = self.make_request(target_url)
        if not response:
            return results
        
        # 尝试从页面中提取JSON数据
        results = self._extract_from_page(response.text)
        
        if not results:
            # 如果提取失败，尝试使用备用方法
            results = self._parse_html_directly(response.text)
        
        return results
    
    def _extract_from_page(self, html_content: str) -> List[Dict]:
        """
        从HTML中提取NEXT_DATA JSON数据
        :param html_content: HTML内容
        :return: 游戏数据列表
        """
        results = []
        crawl_time = self.get_current_time()
        
        try:
            # 查找包含数据的script标签
            pattern = r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>'
            match = re.search(pattern, html_content, re.DOTALL)
            
            if match:
                json_data = json.loads(match.group(1))
                results = self._parse_next_data(json_data, crawl_time)
        except Exception as e:
            print(f"提取TapTap NEXT_DATA出错: {str(e)}")
        
        return results
    
    def _parse_next_data(self, json_data: Dict, crawl_time: str) -> List[Dict]:
        """
        解析NEXT_DATA中的游戏数据
        :param json_data: JSON数据
        :param crawl_time: 爬取时间
        :return: 游戏数据列表
        """
        results = []
        
        try:
            # 定位到游戏列表
            props = json_data.get('props', {})
            page_props = props.get('pageProps', {})
            
            # 尝试多种可能的数据路径
            games_list = None
            
            if 'list' in page_props:
                games_list = page_props.get('list', [])
            elif 'data' in page_props:
                data = page_props.get('data', {})
                games_list = data.get('list', [])
            
            if not games_list:
                # 深度搜索游戏数据
                games_list = self._find_games_deep(page_props)
            
            for idx, game in enumerate(games_list, 1):
                game_data = self._parse_game_item(game, idx, crawl_time)
                if game_data:
                    results.append(game_data)
        except Exception as e:
            print(f"解析TapTap JSON数据出错: {str(e)}")
        
        return results
    
    def _find_games_deep(self, data: Dict) -> List:
        """
        深度搜索游戏列表
        :param data: 字典数据
        :return: 游戏列表
        """
        if isinstance(data, list):
            # 检查是否是游戏列表
            if len(data) > 0 and isinstance(data[0], dict):
                if 'title' in data[0] or 'game_name' in data[0]:
                    return data
            # 递归搜索
            for item in data:
                result = self._find_games_deep(item)
                if result:
                    return result
        elif isinstance(data, dict):
            for key, value in data.items():
                if key in ['list', 'items', 'games', 'data']:
                    if isinstance(value, list) and len(value) > 0:
                        return value
                result = self._find_games_deep(value)
                if result:
                    return result
        return []
    
    def _parse_game_item(self, game: Dict, rank: int, crawl_time: str) -> Dict:
        """
        解析单个游戏数据
        :param game: 游戏字典
        :param rank: 排名
        :param crawl_time: 爬取时间
        :return: 标准化的游戏数据
        """
        try:
            # 游戏名称
            game_name = game.get('title', '') or game.get('game_name', '') or game.get('name', '')
            
            # 游戏ID和链接
            game_id = game.get('id', '') or game.get('app_id', '')
            detail_link = f'https://www.taptap.cn/app/{game_id}' if game_id else ''
            
            # 热度/下载量
            stats = game.get('stat', {}) or game.get('stats', {})
            downloads = stats.get('downloads', 0) or game.get('hits', 0) or game.get('play_count', 0)
            
            # 评分
            rating = game.get('rating', {}).get('score', 0) if isinstance(game.get('rating'), dict) else game.get('rating', 0)
            
            return {
                'rank': str(rank),
                'game_name': game_name,
                'current_players': downloads,
                'peak_players': downloads,  # TapTap没有峰值数据，用下载量代替
                'detail_link': detail_link,
                'platform': self.platform,
                'crawl_time': crawl_time,
                'hotness': downloads,
                'rating': float(rating) if rating else 0
            }
        except Exception as e:
            print(f"解析TapTap游戏数据出错: {str(e)}")
            return {}
    
    def _parse_html_directly(self, html_content: str) -> List[Dict]:
        """
        直接解析HTML获取游戏数据（备用方法）
        :param html_content: HTML内容
        :return: 游戏数据列表
        """
        results = []
        crawl_time = self.get_current_time()
        
        try:
            soup = self.parse_html(html_content)
            
            # 查找游戏卡片
            game_cards = soup.find_all('a', {'class': lambda x: x and 'game-card' in x})
            
            for idx, card in enumerate(game_cards, 1):
                try:
                    href = card.get('href', '')
                    game_name = card.find('h3')
                    game_name = game_name.text.strip() if game_name else ''
                    
                    results.append({
                        'rank': str(idx),
                        'game_name': game_name,
                        'current_players': 0,
                        'peak_players': 0,
                        'detail_link': f'https://www.taptap.cn{href}' if href else '',
                        'platform': self.platform,
                        'crawl_time': crawl_time,
                        'hotness': 0
                    })
                except:
                    continue
        except Exception as e:
            print(f"直接解析TapTap HTML出错: {str(e)}")
        
        return results
