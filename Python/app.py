#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask主应用文件
游戏排行榜爬虫Web应用
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, make_response
import pandas as pd

# 导入爬虫模块
from crawlers import SteamChartsCrawler, TapTapCrawler

# 初始化Flask应用
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 支持中文显示

# 数据存储路径
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
HISTORY_FILE = os.path.join(DATA_DIR, 'history.json')

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# 初始化爬虫实例
crawlers = {
    'steam': SteamChartsCrawler(),
    'taptap': TapTapCrawler()
}

# 缓存机制，缓存最近一次爬取的数据
last_crawled_data = []
last_crawl_time = None
last_crawl_platform = None


def load_history() -> list:
    """
    加载爬取历史记录
    :return: 历史记录列表
    """
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def save_history(history_data: list):
    """
    保存爬取历史记录
    :param history_data: 历史记录列表
    """
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存历史记录失败: {str(e)}")


def add_to_history(platform: str, url: str, record_count: int):
    """
    添加一条历史记录
    :param platform: 平台名称
    :param url: 爬取的URL
    :param record_count: 记录数量
    """
    history = load_history()
    history.insert(0, {
        'platform': platform,
        'url': url,
        'count': record_count,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    # 只保留最近50条记录
    history = history[:50]
    save_history(history)


def detect_platform(url: str) -> str:
    """
    根据URL自动识别平台
    :param url: 用户输入的URL
    :return: 平台标识
    """
    if not url:
        return 'unknown'
    
    url_lower = url.lower()
    if 'steamcharts.com' in url_lower:
        return 'steam'
    elif 'taptap.cn' in url_lower:
        return 'taptap'
    return 'unknown'


@app.route('/')
def index():
    """主页路由"""
    return render_template('index.html')


@app.route('/api/crawl', methods=['POST'])
def crawl():
    """
    爬取API接口
    POST参数:
        - platform: steam/taptap/auto
        - url: 可选的自定义URL
    """
    global last_crawled_data, last_crawl_time, last_crawl_platform
    
    try:
        data = request.get_json() or request.form
        platform = data.get('platform', 'auto')
        custom_url = data.get('url', '').strip()
        
        # 自动识别平台
        if platform == 'auto' and custom_url:
            platform = detect_platform(custom_url)
        
        # 检查平台是否支持
        if platform not in crawlers:
            return jsonify({
                'success': False,
                'message': f'不支持的平台: {platform}，请选择Steam或TapTap，或输入正确的URL'
            }), 400
        
        # 获取对应爬虫
        crawler = crawlers[platform]
        
        # 使用自定义URL或默认URL
        target_url = custom_url if custom_url else crawler.get_default_url()
        
        # 执行爬取
        crawled_data = crawler.crawl(target_url)
        
        if not crawled_data:
            return jsonify({
                'success': False,
                'message': '未能获取到数据，请检查URL是否正确或稍后再试'
            }), 500
        
        # 更新缓存
        last_crawled_data = crawled_data
        last_crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        last_crawl_platform = platform
        
        # 添加到历史记录
        add_to_history(platform, target_url, len(crawled_data))
        
        return jsonify({
            'success': True,
            'message': f'成功爬取 {len(crawled_data)} 条数据',
            'platform': platform,
            'platform_name': crawler.get_platform_name(),
            'url': target_url,
            'crawl_time': last_crawl_time,
            'data': crawled_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'爬取过程中发生错误: {str(e)}'
        }), 500


@app.route('/api/history')
def get_history():
    """获取爬取历史记录API"""
    history = load_history()
    return jsonify({
        'success': True,
        'data': history
    })


@app.route('/api/export/<format_type>')
def export_data(format_type):
    """
    数据导出API
    :param format_type: csv或json
    """
    global last_crawled_data
    
    if not last_crawled_data:
        return jsonify({
            'success': False,
            'message': '没有可导出的数据，请先进行爬取'
        }), 400
    
    try:
        df = pd.DataFrame(last_crawled_data)
        
        if format_type.lower() == 'csv':
            csv_data = df.to_csv(index=False, encoding='utf-8-sig')
            response = make_response(csv_data)
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename="game_ranking_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            return response
        
        elif format_type.lower() == 'json':
            json_data = df.to_json(orient='records', force_ascii=False)
            response = make_response(json_data)
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename="game_ranking_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
            return response
        
        else:
            return jsonify({
                'success': False,
                'message': f'不支持的导出格式: {format_type}'
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'导出失败: {str(e)}'
        }), 500


@app.errorhandler(404)
def page_not_found(e):
    """404错误处理"""
    return jsonify({
        'success': False,
        'message': '页面不存在'
    }), 404


@app.errorhandler(500)
def internal_server_error(e):
    """500错误处理"""
    return jsonify({
        'success': False,
        'message': '服务器内部错误'
    }), 500


if __name__ == '__main__':
    print('=' * 60)
    print('游戏排行榜爬虫Web应用启动中...')
    print('访问地址: http://localhost:5000')
    print('支持平台: Steam Charts, TapTap')
    print('=' * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
