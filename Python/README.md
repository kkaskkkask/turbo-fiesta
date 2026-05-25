# 🎮 游戏排行榜爬虫 Web 应用

一个基于 Flask 的完整 Web 应用，用于爬取并可视化展示 Steam Charts 和 TapTap 等平台的游戏排行榜数据。

## ✨ 功能特性

### 🖥️ Web 界面功能
- 🏠 简洁美观的响应式主页
- 📝 平台选择和自定义 URL 输入
- ⏳ 爬取进度和加载动画提示
- 📊 数据表格展示（支持排序、搜索、分页）
- 📈 数据可视化图表（Chart.js 实现）
- 💾 数据导出（CSV / JSON 格式）
- 📜 爬取历史记录展示

### 🎯 支持的平台
- 🔥 **Steam Charts** - 游戏在线人数排行榜
- 📱 **TapTap** - 热门游戏下载排行榜
- 🔍 **自动识别** - 根据 URL 自动识别对应平台

### 📋 爬取数据字段
- 游戏排名
- 游戏名称
- 当前在线人数 / 下载量
- 峰值玩家数
- 游戏详情链接
- 平台标识
- 爬取时间

## 🛠️ 技术栈

| 模块 | 技术栈 |
|------|--------|
| **后端** | Flask 3.0 (Python Web 框架) |
| **前端** | HTML5 + CSS3 + 原生 JavaScript |
| **图表** | Chart.js |
| **爬虫** | requests + BeautifulSoup4 |
| **数据处理** | pandas |
| **HTML 解析** | lxml |

## 📁 项目结构

```
game_crawler_app/
├── app.py                 # Flask 主应用程序
├── crawlers/              # 爬虫模块目录
│   ├── __init__.py
│   ├── base.py            # 爬虫基类
│   ├── steam_charts.py    # Steam Charts 爬虫
│   └── taptap.py          # TapTap 爬虫
├── templates/             # HTML 模板目录
│   └── index.html         # 主页
├── static/                # 静态资源目录
│   ├── css/
│   │   └── style.css      # 样式文件
│   └── js/
│       └── app.js         # 前端脚本
├── data/                  # 数据存储目录
│   └── history.json       # 爬取历史记录
├── requirements.txt       # Python 依赖清单
└── README.md              # 使用说明文档
```

## 🚀 快速开始

### 1️⃣ 环境要求
- Python 3.8+
- pip 包管理器

### 2️⃣ 安装依赖

```bash
cd game_crawler_app
pip install -r requirements.txt
```

### 3️⃣ 启动应用

```bash
python app.py
```

### 4️⃣ 访问应用

打开浏览器访问: **http://localhost:5000**

## 📡 API 接口说明

### 1. 主页
```
GET /
```
返回 Web 应用主页。

### 2. 开始爬取
```
POST /api/crawl
Content-Type: application/json

{
    "platform": "steam",    // steam / taptap / auto
    "url": ""               // 可选，自定义 URL
}
```

**响应示例:**
```json
{
    "success": true,
    "message": "成功爬取 100 条数据",
    "platform": "steam",
    "platform_name": "Steam Charts",
    "url": "https://steamcharts.com/top",
    "crawl_time": "2024-01-15 12:00:00",
    "data": [...]
}
```

### 3. 获取爬取历史
```
GET /api/history
```

### 4. 导出数据
```
GET /api/export/csv    // 导出 CSV 格式
GET /api/export/json   // 导出 JSON 格式
```

## 🎮 使用说明

### Steam Charts 爬取
1. 在平台选择中选择 **"Steam Charts"**
2. 点击 **"开始爬取"**
3. 等待数据加载完成

### TapTap 爬取
1. 在平台选择中选择 **"TapTap"**
2. 点击 **"开始爬取"**

### 自定义 URL
1. 在平台选择中选择 **"自动识别"**
2. 在 URL 输入框中输入完整的目标网站 URL
3. 点击 **"开始爬取"**

### 数据操作
- **搜索**: 在搜索框输入游戏名称进行筛选
- **排序**: 点击表头进行排序切换
- **分页**: 点击分页按钮翻页查看
- **导出**: 点击导出按钮下载数据文件

## 🎨 界面预览

### 主页设计
- 响应式设计，支持电脑和手机端完美展示
- 现代渐变配色风格
- 流畅的动画和交互效果

### 数据展示
- TOP 10 游戏热度横向柱状图
- 排名前三名特殊颜色标识（金/银/铜）
- 表格支持分页，每页 20 条记录

## ⚙️ 配置说明

### 请求频率限制
在 `crawlers/base.py` 中修改:
```python
self.request_interval = 1  # 单位：秒
```

### 分页数量
在 `static/js/app.js` 中修改:
```javascript
const itemsPerPage = 20;  // 每页显示数量
```

### 历史记录数量
在 `app.py` 中修改:
```python
history = history[:50]  # 保留最近 50 条记录
```

## 🔧 开发说明

### 添加新平台爬虫
1. 在 `crawlers/` 目录下创建新文件，如 `new_platform.py`
2. 继承 `CrawlerBase` 类
3. 实现 `crawl()`, `get_platform_name()`, `get_default_url()` 方法
4. 在 `crawlers/__init__.py` 中导出新爬虫
5. 在 `app.py` 的 `crawlers` 字典中添加映射
6. 在前端 `templates/index.html` 中添加选项

### 注意事项
- 请遵守目标网站的 `robots.txt` 规则
- 合理设置请求间隔，避免对目标服务器造成压力
- 数据仅供学习参考使用

## 🐛 常见问题

**Q: Steam Charts 爬取失败怎么办？**
> A: 可能是网站结构变更，请检查网络连接或更新爬虫解析规则。

**Q: TapTap 数据为空？**
> A: TapTap 有反爬机制，可能需要更新请求头或使用代理。

**Q: 导出的 CSV 乱码？**
> A: 已使用 `utf-8-sig` 编码，Excel 打开时请选择 UTF-8 编码。

## 📝 更新日志

### v1.0.0 (2024-01-15)
- ✅ 基础 Flask Web 应用框架
- ✅ Steam Charts 爬虫实现
- ✅ TapTap 爬虫实现
- ✅ 响应式前端界面
- ✅ 数据表格和图表展示
- ✅ 数据导出功能
- ✅ 爬取历史记录

## 📄 许可证

本项目仅供学习交流使用。

---

**🎯 Enjoy your game data crawling!**
