document.addEventListener('DOMContentLoaded', function() {
    initExportPage();
    loadAnalysisData();
});

let analysisData = null;

function initExportPage() {
    initToast();
    initExportCards();
}

function initToast() {
    const toast = document.getElementById('toast');
    if (!toast) {
        const toastDiv = document.createElement('div');
        toastDiv.id = 'toast';
        toastDiv.className = 'toast';
        document.body.appendChild(toastDiv);
    }
}

function initExportCards() {
    document.querySelectorAll('.export-card').forEach(card => {
        const statusEl = card.querySelector('.export-status');
        if (statusEl) {
            statusEl.classList.add('idle');
        }
    });
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function updateCardStatus(cardId, status) {
    const card = document.querySelector(`[data-export="${cardId}"]`);
    if (!card) return;
    
    const statusEl = card.querySelector('.export-status');
    if (!statusEl) return;
    
    statusEl.className = 'export-status';
    statusEl.classList.add(status);
}

function updateProgress(progressId, percent, text) {
    const progress = document.getElementById(progressId);
    if (!progress) return;
    
    progress.style.display = 'block';
    const fill = progress.querySelector('.progress-fill');
    const textEl = progress.querySelector('.progress-text');
    
    if (fill) {
        fill.style.width = `${percent}%`;
    }
    if (textEl) {
        textEl.textContent = text || `${percent}%`;
    }
}

function toggleDateRange() {
    const checkbox = document.getElementById('dateRange');
    const inputs = document.getElementById('dateRangeInputs');
    if (checkbox && inputs) {
        inputs.style.display = checkbox.checked ? 'flex' : 'none';
    }
}

function toggleQRInput() {
    const checkbox = document.getElementById('posterQR');
    const input = document.getElementById('qrInput');
    if (checkbox && input) {
        input.style.display = checkbox.checked ? 'block' : 'none';
    }
}

function getSelectedFormats(name) {
    const checkboxes = document.querySelectorAll(`input[name="${name}"]:checked`);
    return Array.from(checkboxes).map(cb => cb.value);
}

async function loadAnalysisData() {
    const contactId = window.location.pathname.split('/').pop();
    
    try {
        const response = await fetch(`/api/contacts/${contactId}/analysis`);
        
        if (response.ok) {
            const data = await response.json();
            if (data.analysis) {
                analysisData = data.analysis;
                updatePosterPreview();
            }
        }
    } catch (error) {
        console.log('No analysis data');
    }
}

async function exportChatLogs() {
    const contactId = window.location.pathname.split('/').pop();
    const card = document.querySelector('[data-export="chat-logs"]');
    const btn = document.getElementById('chatLogsBtn');
    
    const formats = getSelectedFormats('chatFormat');
    if (formats.length === 0) {
        showToast('请选择至少一种导出格式', 'error');
        return;
    }
    
    if (card) card.classList.add('exporting');
    updateCardStatus('chat-logs', 'exporting');
    if (btn) {
        btn.disabled = true;
        btn.textContent = '导出中...';
    }
    
    updateProgress('chatLogsProgress', 10, '准备数据...');
    
    try {
        showToast('正在导出聊天记录...', 'info');
        
        const includeAnalysis = document.getElementById('includeAnalysis')?.checked || false;
        const useDateRange = document.getElementById('dateRange')?.checked || false;
        const startDate = document.getElementById('startDate')?.value;
        const endDate = document.getElementById('endDate')?.value;
        
        const params = new URLSearchParams({
            formats: formats.join(','),
            include_analysis: includeAnalysis
        });
        
        if (useDateRange && startDate) {
            params.append('start_date', startDate);
        }
        if (useDateRange && endDate) {
            params.append('end_date', endDate);
        }
        
        updateProgress('chatLogsProgress', 30, '处理数据...');
        
        const response = await fetch(`/api/contacts/${contactId}/export/chat-logs?${params}`);
        
        if (response.ok) {
            updateProgress('chatLogsProgress', 70, '生成文件...');
            
            const blob = await response.blob();
            updateProgress('chatLogsProgress', 90, '下载中...');
            
            const contentType = blob.type || 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
            const extension = contentType.includes('spreadsheet') || contentType.includes('excel') ? 'xlsx' : 'csv';
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `聊天记录_${Date.now()}.${extension}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            updateProgress('chatLogsProgress', 100, '完成！');
            if (card) card.classList.remove('exporting');
            if (card) card.classList.add('success');
            updateCardStatus('chat-logs', 'success');
            
            showToast(`导出成功！格式：${formats.join(', ')}`, 'success');
        } else {
            const error = await response.json();
            throw new Error(error.error || '导出失败');
        }
    } catch (error) {
        console.error('Export Error:', error);
        if (card) card.classList.remove('exporting');
        if (card) card.classList.add('error');
        updateCardStatus('chat-logs', 'error');
        showToast(error.message || '导出失败', 'error');
        
        const progress = document.getElementById('chatLogsProgress');
        if (progress) progress.style.display = 'none';
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.textContent = '导出聊天记录';
        }
    }
}

async function exportAnalysis() {
    const contactId = window.location.pathname.split('/').pop();
    const card = document.querySelector('[data-export="analysis"]');
    const btn = document.getElementById('analysisBtn');
    
    const formats = getSelectedFormats('analysisFormat');
    if (formats.length === 0) {
        showToast('请选择至少一种导出格式', 'error');
        return;
    }
    
    if (card) card.classList.add('exporting');
    updateCardStatus('analysis', 'exporting');
    if (btn) {
        btn.disabled = true;
        btn.textContent = '导出中...';
    }
    
    updateProgress('analysisProgress', 10, '准备数据...');
    
    try {
        showToast('正在导出分析报告...', 'info');
        
        const includePersonality = document.getElementById('includePersonality')?.checked || true;
        const includeInterests = document.getElementById('includeInterests')?.checked || true;
        const includeGuide = document.getElementById('includeGuide')?.checked || true;
        
        updateProgress('analysisProgress', 30, '生成报告...');
        
        const params = new URLSearchParams({
            formats: formats.join(','),
            include_personality: includePersonality,
            include_interests: includeInterests,
            include_guide: includeGuide
        });
        
        const response = await fetch(`/api/contacts/${contactId}/export/analysis?${params}`);
        
        if (response.ok) {
            updateProgress('analysisProgress', 60, '处理文件...');
            
            const blob = await response.blob();
            updateProgress('analysisProgress', 80, '下载中...');
            
            let filename = '分析报告';
            if (formats.length === 1) {
                const format = formats[0];
                if (format === 'xlsx') filename += '.xlsx';
                else if (format === 'json') filename += '.json';
                else if (format === 'pdf') filename += '.pdf';
            } else {
                filename += '.zip';
            }
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${filename}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            updateProgress('analysisProgress', 100, '完成！');
            if (card) card.classList.remove('exporting');
            if (card) card.classList.add('success');
            updateCardStatus('analysis', 'success');
            
            showToast(`分析报告导出成功！`, 'success');
        } else {
            const error = await response.json();
            throw new Error(error.error || '导出失败');
        }
    } catch (error) {
        console.error('Export Error:', error);
        if (card) card.classList.remove('exporting');
        if (card) card.classList.add('error');
        updateCardStatus('analysis', 'error');
        showToast(error.message || '导出失败', 'error');
        
        const progress = document.getElementById('analysisProgress');
        if (progress) progress.style.display = 'none';
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.textContent = '导出分析报告';
        }
    }
}

async function generatePoster() {
    if (!analysisData) {
        showToast('请先进行AI分析', 'error');
        return;
    }
    
    const card = document.querySelector('[data-export="poster"]');
    const btn = document.getElementById('posterBtn');
    
    if (card) card.classList.add('exporting');
    updateCardStatus('poster', 'exporting');
    if (btn) {
        btn.disabled = true;
        btn.textContent = '生成中...';
    }
    
    updateProgress('posterProgress', 20, '渲染图表...');
    
    try {
        showToast('正在生成海报...', 'info');
        
        const modal = document.getElementById('posterModal');
        if (modal) modal.classList.add('show');
        
        setTimeout(() => {
            renderPosterChart();
            updateProgress('posterProgress', 50, '生成预览...');
            
            setTimeout(() => {
                updateProgress('posterProgress', 100, '完成！');
                if (card) card.classList.remove('exporting');
                if (card) card.classList.add('success');
                updateCardStatus('poster', 'success');
                
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = '重新生成';
                }
            }, 500);
        }, 100);
    } catch (error) {
        console.error('Generate poster error:', error);
        if (card) card.classList.remove('exporting');
        if (card) card.classList.add('error');
        updateCardStatus('poster', 'error');
        showToast('生成海报失败', 'error');
        
        const progress = document.getElementById('posterProgress');
        if (progress) progress.style.display = 'none';
        
        if (btn) {
            btn.disabled = false;
            btn.textContent = '生成海报';
        }
    }
}

function renderPosterChart() {
    const chartDom = document.getElementById('posterRadar');
    if (!chartDom || typeof echarts === 'undefined' || !analysisData) return;
    
    const chart = echarts.init(chartDom);
    
    const parsed = parseAnalysis(analysisData);
    const traits = parsed.core_traits || {};
    
    const dimensions = [];
    const values = [];
    
    const traitMapping = {
        'rationality': '理性',
        'introversion': '内向',
        'planning': '计划性',
        'responsibility': '责任感',
        'stress_resistance': '抗压能力',
        'decision_style': '决断力'
    };
    
    Object.entries(traits).forEach(([key, value]) => {
        if (traitMapping[key]) {
            dimensions.push(traitMapping[key]);
            const numValue = typeof value === 'number' ? value : 5;
            values.push(Math.min(10, Math.max(1, numValue)));
        }
    });
    
    if (dimensions.length === 0) {
        dimensions.push('综合');
        values.push(5);
    }
    
    const showRadar = document.getElementById('posterRadar')?.checked !== false;
    if (!showRadar) {
        chartDom.style.display = 'none';
        return;
    }
    
    chartDom.style.display = 'block';
    
    const option = {
        tooltip: {
            trigger: 'item'
        },
        radar: {
            indicator: dimensions.map((dim, index) => ({
                name: dim,
                max: 10
            })),
            radius: '60%',
            center: ['50%', '50%'],
            axisName: {
                color: '#fff',
                fontSize: 10
            },
            splitArea: {
                areaStyle: {
                    color: ['rgba(255,255,255,0.1)', 'rgba(255,255,255,0.2)']
                }
            },
            axisLine: {
                lineStyle: {
                    color: 'rgba(255,255,255,0.3)'
                }
            },
            splitLine: {
                lineStyle: {
                    color: 'rgba(255,255,255,0.3)'
                }
            }
        },
        series: [{
            type: 'radar',
            data: [{
                value: values,
                name: '性格维度',
                areaStyle: {
                    color: 'rgba(255,255,255,0.4)'
                },
                lineStyle: {
                    color: '#fff',
                    width: 2
                },
                itemStyle: {
                    color: '#fff'
                }
            }]
        }]
    };
    
    chart.setOption(option);
    
    window.addEventListener('resize', () => chart.resize());
    
    updatePosterKeywords();
    updatePosterSummary();
}

function updatePosterKeywords() {
    const container = document.getElementById('posterKeywords');
    const showKeywords = document.getElementById('posterKeywords')?.checked !== false;
    
    if (!container) return;
    
    if (!showKeywords) {
        container.style.display = 'none';
        return;
    }
    
    container.style.display = 'flex';
    const parsed = parseAnalysis(analysisData);
    const keywords = parsed.interests || [];
    
    container.innerHTML = '';
    
    keywords.slice(0, 6).forEach(keyword => {
        const tag = document.createElement('span');
        tag.className = 'keyword-tag';
        tag.textContent = keyword;
        container.appendChild(tag);
    });
}

function updatePosterSummary() {
    const el = document.getElementById('posterSummary');
    if (!el || !analysisData) return;
    
    const parsed = parseAnalysis(analysisData);
    el.textContent = parsed.summary || '等待分析...';
}

function parseAnalysis(analysis) {
    const result = {};
    
    ['core_traits', 'behavior_preferences', 'social_interaction', 'cognitive_thinking'].forEach(field => {
        if (analysis[field]) {
            try {
                result[field] = typeof analysis[field] === 'string' 
                    ? JSON.parse(analysis[field]) 
                    : analysis[field];
            } catch {
                result[field] = analysis[field];
            }
        }
    });
    
    if (analysis.interests) {
        try {
            result.interests = typeof analysis.interests === 'string'
                ? JSON.parse(analysis.interests)
                : analysis.interests;
        } catch {
            result.interests = analysis.interests;
        }
    }
    
    result.summary = analysis.summary || '';
    
    return result;
}

async function downloadPoster() {
    const posterEl = document.getElementById('posterContent');
    if (!posterEl) return;
    
    const card = document.querySelector('[data-export="poster"]');
    const btn = document.getElementById('posterBtn');
    
    if (card) card.classList.add('exporting');
    updateCardStatus('poster', 'exporting');
    if (btn) {
        btn.disabled = true;
        btn.textContent = '下载中...';
    }
    
    try {
        showToast('正在生成海报...', 'info');
        
        if (typeof html2canvas !== 'undefined') {
            const canvas = await html2canvas(posterEl, {
                scale: 2,
                backgroundColor: null,
                logging: false
            });
            
            const format = document.querySelector('input[name="posterFormat"]:checked')?.value || 'png';
            const extension = format === 'jpg' ? 'jpg' : 'png';
            const mimeType = format === 'jpg' ? 'image/jpeg' : 'image/png';
            
            const link = document.createElement('a');
            link.download = `SoulProfile_${Date.now()}.${extension}`;
            link.href = canvas.toDataURL(mimeType, 0.95);
            link.click();
            
            if (card) card.classList.remove('exporting');
            if (card) card.classList.add('success');
            updateCardStatus('poster', 'success');
            showToast('海报下载成功！', 'success');
        } else {
            showToast('html2canvas库未加载', 'error');
        }
    } catch (error) {
        console.error('Generate poster error:', error);
        if (card) card.classList.remove('exporting');
        if (card) card.classList.add('error');
        updateCardStatus('poster', 'error');
        showToast('生成海报失败', 'error');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.textContent = '下载海报';
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
    }
}

function updatePosterPreview() {
    if (analysisData) {
        updatePosterKeywords();
        updatePosterSummary();
    }
}
