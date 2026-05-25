#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Steam Charts爬虫模块
用于爬取 steamcharts.com 的游戏在线人数排行榜
"""

from typing import List, Dict
from .base import CrawlerBase


class SteamChartsCrawler(CrawlerBase):
    """Steam Charts爬虫"""
    
    def __init__(self):
        super().__init__()
        self.platform = 'steam'
    
    def get_platform_name(self) -> str:
        """获取平台名称"""
        return 'Steam Charts'
    
    def get_default_url(self) -> str:
        """获取默认爬取URL"""
        return 'https://steamcharts.com/top'
    
    def crawl(self, url: str = None) -> List[Dict]:
        """
        爬取Steam Charts排行榜数据
        :param url: 自定义URL，默认为TOP游戏榜
        :return: 游戏数据列表
        """
        target_url = url if url else self.get_default_url()
        results = []
        
        # 发送请求
        response = self.make_request(target_url)
        if not response:
            return results
        
        # 解析HTML
        soup = self.parse_html(response.text)
        
        # 查找游戏表格
        game_table = soup.find('table', {'id': 'top-games'})
        if not game_table:
            return results
        
        # 解析表格行
        tbody = game_table.find('tbody')
        if not tbody:
            return results
        
        rows = tbody.find_all('tr')
        crawl_time = self.get_current_time()
        
        for row in rows:
            try:
                game_data = self._parse_row(row)
                if game_data:
                    game_data['platform'] = self.platform
                    game_data['crawl_time'] = crawl_time
                    results.append(game_data)
            except Exception as e:
                print(f"解析Steam行数据出错: {str(e)}")
                continue
        
        return results
    
    def _parse_row(self, row) -> Dict:
        """
        解析单行游戏数据
        :param row: tr标签对象
        :return: 游戏数据字典
        """
        cols = row.find_all('td')
        if len(cols) < 5:
            return {}
        
        # 排名
        rank = cols[0].text.strip() if cols[0] else ''
        
        # 游戏名称和链接
        game_name_col = cols[1].find('a') if cols[1] else None
        game_name = game_name_col.text.strip() if game_name_col else ''
        detail_link = 'https://steamcharts.com' + game_name_col.get('href', '') if game_name_col else ''
        
        # 当前在线人数
        current_players = self.format_number(cols[2].text.strip()) if cols[2] else 0
        
        # 峰值人数
        peak_players = self.format_number(cols[4].text.strip()) if len(cols) > 4 else 0
        
        return {
            'rank': rank,
            'game_name': game_name,
            'current_players': current_players,
            'peak_players': peak_players,
            'detail_link': detail_link,
            'hotness': current_players  # Steam用当前在线人数表示热度
        }
