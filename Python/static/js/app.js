// 全局变量
let currentData = [];
let filteredData = [];
let currentPage = 1;
const itemsPerPage = 20;
let chartInstance = null;
let sortColumn = null;
let sortDirection = 1; // 1: 升序, -1: 降序

// DOM元素
const elements = {
    platform: document.getElementById('platform'),
    url: document.getElementById('url'),
    crawlBtn: document.getElementById('crawlBtn'),
    btnText: document.querySelector('.btn-text'),
    btnLoading: document.querySelector('.btn-loading'),
    progress: document.getElementById('progress'),
    error: document.getElementById('error'),
    results: document.getElementById('results'),
    platformName: document.getElementById('platformName'),
    crawlTime: document.getElementById('crawlTime'),
    recordCount: document.getElementById('recordCount'),
    searchInput: document.getElementById('searchInput'),
    tableBody: document.getElementById('tableBody'),
    pagination: document.getElementById('pagination'),
    exportCsv: document.getElementById('exportCsv'),
    exportJson: document.getElementById('exportJson'),
    historyList: document.getElementById('historyList')
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
    bindEvents();
});

// 绑定事件
function bindEvents() {
    elements.crawlBtn.addEventListener('click', startCrawl);
    elements.searchInput.addEventListener('input', handleSearch);
    elements.exportCsv.addEventListener('click', () => exportData('csv'));
    elements.exportJson.addEventListener('click', () => exportData('json'));

    // 表头排序事件
    document.querySelectorAll('.data-table th[data-sort]').forEach(th => {
        th.addEventListener('click', () => handleSort(th.dataset.sort));
    });
}

// 开始爬取
async function startCrawl() {
    const platform = elements.platform.value;
    const url = elements.url.value.trim();

    // 验证
    if (platform === 'auto' && !url) {
        showError('选择"自动识别"时请输入URL');
        return;
    }

    // 显示加载状态
    setLoading(true);
    hideError();
    elements.results.style.display = 'none';

    try {
        const response = await fetch('/api/crawl', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ platform, url })
        });

        const result = await response.json();

        if (result.success) {
            currentData = result.data;
            filteredData = [...currentData];
            displayResults(result);
            renderTable();
            renderChart();
            loadHistory(); // 刷新历史
        } else {
            showError(result.message || '爬取失败');
        }
    } catch (error) {
        showError('网络错误，请重试: ' + error.message);
    } finally {
        setLoading(false);
    }
}

// 设置加载状态
function setLoading(isLoading) {
    elements.crawlBtn.disabled = isLoading;
    elements.btnText.style.display = isLoading ? 'none' : 'inline';
    elements.btnLoading.style.display = isLoading ? 'inline-flex' : 'none';
    elements.progress.style.display = isLoading ? 'block' : 'none';
}

// 显示错误
function showError(message) {
    elements.error.textContent = message;
    elements.error.style.display = 'block';
}

// 隐藏错误
function hideError() {
    elements.error.style.display = 'none';
}

// 显示结果
function displayResults(result) {
    elements.results.style.display = 'block';
    elements.platformName.textContent = `平台: ${result.platform_name}`;
    elements.crawlTime.textContent = `时间: ${result.crawl_time}`;
    elements.recordCount.textContent = `记录数: ${result.data.length}条`;
}

// 搜索过滤
function handleSearch() {
    const keyword = elements.searchInput.value.toLowerCase().trim();
    
    if (!keyword) {
        filteredData = [...currentData];
    } else {
        filteredData = currentData.filter(item => 
            item.game_name.toLowerCase().includes(keyword)
        );
    }
    
    currentPage = 1;
    renderTable();
}

// 排序处理
function handleSort(column) {
    if (sortColumn === column) {
        sortDirection *= -1;
    } else {
        sortColumn = column;
        sortDirection = 1;
    }

    filteredData.sort((a, b) => {
        let valA = a[column];
        let valB = b[column];

        // 数字排序
        if (typeof valA === 'number' && typeof valB === 'number') {
            return (valA - valB) * sortDirection;
        }
        
        // 排名排序（处理带#号的情况）
        if (column === 'rank') {
            valA = parseInt(valA) || 0;
            valB = parseInt(valB) || 0;
            return (valA - valB) * sortDirection;
        }

        // 字符串排序
        return String(valA).localeCompare(String(valB)) * sortDirection;
    });

    renderTable();
}

// 渲染表格
function renderTable() {
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageData = filteredData.slice(start, end);

    let html = '';
    pageData.forEach((item, index) => {
        const rankNum = parseInt(item.rank) || (start + index + 1);
        const rankClass = rankNum <= 3 ? `rank-${rankNum}` : '';
        
        html += `
            <tr>
                <td class="${rankClass}">#${item.rank || rankNum}</td>
                <td>${escapeHtml(item.game_name)}</td>
                <td>${formatNumber(item.current_players || item.hotness || 0)}</td>
                <td>${formatNumber(item.peak_players || 0)}</td>
                <td>
                    ${item.detail_link ? `<a href="${item.detail_link}" target="_blank" class="game-link">查看详情 →</a>` : '-'}
                </td>
            </tr>
        `;
    });

    if (!pageData.length) {
        html = '<tr><td colspan="5" style="text-align: center; padding: 40px; color: #999;">暂无数据</td></tr>';
    }

    elements.tableBody.innerHTML = html;
    renderPagination();
}

// 渲染分页
function renderPagination() {
    const totalPages = Math.ceil(filteredData.length / itemsPerPage);
    
    if (totalPages <= 1) {
        elements.pagination.innerHTML = '';
        return;
    }

    let html = '';

    // 上一页
    html += `<button class="page-btn" ${currentPage === 1 ? 'disabled' : ''} onclick="changePage(${currentPage - 1})">上一页</button>`;

    // 页码
    const maxVisible = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    
    if (endPage - startPage < maxVisible - 1) {
        startPage = Math.max(1, endPage - maxVisible + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
        html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="changePage(${i})">${i}</button>`;
    }

    // 下一页
    html += `<button class="page-btn" ${currentPage === totalPages ? 'disabled' : ''} onclick="changePage(${currentPage + 1})">下一页</button>`;

    elements.pagination.innerHTML = html;
}

// 切换页面
function changePage(page) {
    const totalPages = Math.ceil(filteredData.length / itemsPerPage);
    if (page < 1 || page > totalPages) return;
    
    currentPage = page;
    renderTable();
    
    // 滚动到表格顶部
    document.querySelector('.table-container').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// 渲染图表
function renderChart() {
    const ctx = document.getElementById('rankingChart').getContext('2d');
    
    // 获取TOP 10数据
    const top10 = filteredData.slice(0, 10);
    const labels = top10.map(item => item.game_name.length > 15 
        ? item.game_name.substring(0, 15) + '...' 
        : item.game_name);
    const data = top10.map(item => item.current_players || item.hotness || 0);

    // 销毁旧图表
    if (chartInstance) {
        chartInstance.destroy();
    }

    // 创建渐变颜色
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(102, 126, 234, 0.8)');
    gradient.addColorStop(1, 'rgba(118, 75, 162, 0.8)');

    chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '热度/在线人数',
                data: data,
                backgroundColor: gradient,
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return '热度: ' + formatNumber(context.raw);
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        callback: function(value) {
                            return formatNumber(value);
                        }
                    }
                },
                y: {
                    grid: {
                        display: false
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    });
}

// 导出数据
function exportData(format) {
    window.location.href = `/api/export/${format}`;
}

// 加载历史记录
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const result = await response.json();

        if (result.success && result.data.length > 0) {
            let html = '';
            result.data.forEach(item => {
                const platformEmoji = item.platform === 'steam' ? '🔥' : '📱';
                html += `
                    <div class="history-item">
                        <div class="history-info">
                            <span class="history-platform">${platformEmoji} ${item.platform.toUpperCase()}</span>
                            <span class="history-time">${item.time}</span>
                        </div>
                        <span class="history-count">${item.count} 条</span>
                    </div>
                `;
            });
            elements.historyList.innerHTML = html;
        } else {
            elements.historyList.innerHTML = '<p class="empty-history">暂无历史记录</p>';
        }
    } catch (error) {
        console.error('加载历史记录失败:', error);
    }
}

// 工具函数：格式化数字
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// 工具函数：HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
