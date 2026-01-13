let analysisData = null;

document.addEventListener('DOMContentLoaded', function() {
    initTabs();
    renderMessageDistribution();
    loadAnalysisIfExists();
});

function initTabs() {
    const tabs = document.querySelectorAll('.tab-btn');
    const panels = document.querySelectorAll('.tab-panel');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetTab = this.dataset.tab;
            
            tabs.forEach(t => t.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));
            
            this.classList.add('active');
            document.getElementById(targetTab)?.classList.add('active');
        });
    });
}

async function loadAnalysisIfExists() {
    const contactId = window.location.pathname.split('/').pop();
    
    try {
        const response = await fetch(`/api/contacts/${contactId}/analysis`);
        
        if (response.ok) {
            const data = await response.json();
            if (data.analysis) {
                analysisData = data.analysis;
                renderAnalysisResults(analysisData);
            }
        }
    } catch (error) {
        console.log('No analysis data yet');
    }
}

function renderAnalysisResults(analysis) {
    const parsed = analysis.get_parsed_data ? analysis.get_parsed_data() : parseAnalysis(analysis);
    
    if (parsed.summary) {
        document.querySelector('.summary-text').textContent = parsed.summary;
    }
    
    if (parsed.core_traits) {
        renderRadarChart(parsed.core_traits);
    }
    
    if (parsed.interests && Array.isArray(parsed.interests)) {
        renderWordCloud(parsed.interests);
    }
    
    renderMessageDistribution();
    renderQuickInsights(parsed);
    renderTraitDetails(parsed);
    renderInterests(parsed);
    renderGuide(parsed);
    renderTimeline();
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
    
    if (analysis.dos_and_donts) {
        try {
            result.dos_and_donts = typeof analysis.dos_and_donts === 'string'
                ? JSON.parse(analysis.dos_and_donts)
                : analysis.dos_and_donts;
        } catch {
            result.dos_and_donts = analysis.dos_and_donts;
        }
    }
    
    if (analysis.topic_suggestions) {
        try {
            result.topic_suggestions = typeof analysis.topic_suggestions === 'string'
                ? JSON.parse(analysis.topic_suggestions)
                : analysis.topic_suggestions;
        } catch {
            result.topic_suggestions = analysis.topic_suggestions;
        }
    }
    
    if (analysis.gift_suggestions) {
        try {
            result.gift_suggestions = typeof analysis.gift_suggestions === 'string'
                ? JSON.parse(analysis.gift_suggestions)
                : analysis.gift_suggestions;
        } catch {
            result.gift_suggestions = analysis.gift_suggestions;
        }
    }
    
    result.summary = analysis.summary || '';
    
    return result;
}

function renderRadarChart(traits) {
    const chartDom = document.getElementById('radarChart');
    if (!chartDom || typeof echarts === 'undefined') return;
    
    const chart = echarts.init(chartDom);
    
    const dimensions = [];
    const values = [];
    
    const traitMapping = {
        'rationality': '理性程度',
        'introversion': '内向程度',
        'planning': '计划性',
        'responsibility': '责任态度',
        'stress_resistance': '抗压能力',
        'decision_style': '决策风格',
        'initiative': '主动性',
        'expression_style': '表达风格',
        'empathy': '共情能力',
        'sharing_willingness': '分享欲',
        'knowledge_depth': '知识深度',
        'knowledge_breadth': '知识广度'
    };
    
    Object.entries(traits).forEach(([key, value]) => {
        if (traitMapping[key]) {
            dimensions.push(traitMapping[key]);
            const numValue = typeof value === 'number' ? value : 5;
            values.push(Math.min(10, Math.max(1, numValue)));
        }
    });
    
    if (dimensions.length === 0) return;
    
    const option = {
        tooltip: {
            trigger: 'item'
        },
        radar: {
            indicator: dimensions.map((dim, index) => ({
                name: dim,
                max: 10
            })),
            radius: '65%',
            center: ['50%', '50%'],
            axisName: {
                color: '#666',
                fontSize: 11
            },
            splitArea: {
                areaStyle: {
                    color: ['rgba(74, 108, 247, 0.05)', 'rgba(74, 108, 247, 0.1)']
                }
            }
        },
        series: [{
            type: 'radar',
            data: [{
                value: values,
                name: '性格维度',
                areaStyle: {
                    color: 'rgba(74, 108, 247, 0.3)'
                },
                lineStyle: {
                    color: '#4a6cf7',
                    width: 2
                },
                itemStyle: {
                    color: '#4a6cf7'
                }
            }]
        }]
    };
    
    chart.setOption(option);
    
    window.addEventListener('resize', () => chart.resize());
}

function renderMessageDistribution() {
    const chatItems = document.querySelectorAll('.chat-item');
    
    let myCount = 0;
    let otherCount = 0;
    
    chatItems.forEach(item => {
        if (item.classList.contains('me')) {
            myCount++;
        } else {
            otherCount++;
        }
    });
    
    const total = myCount + otherCount;
    
    if (total === 0) return;
    
    const myPercent = Math.round((myCount / total) * 100);
    const otherPercent = Math.round((otherCount / total) * 100);
    
    const myPercentEl = document.getElementById('mePercent');
    const otherPercentEl = document.getElementById('otherPercent');
    const myCountEl = document.getElementById('meCount');
    const otherCountEl = document.getElementById('otherCount');
    
    if (myPercentEl) myPercentEl.textContent = myPercent + '%';
    if (otherPercentEl) otherPercentEl.textContent = otherPercent + '%';
    if (myCountEl) myCountEl.textContent = myCount + ' 条';
    if (otherCountEl) otherCountEl.textContent = otherCount + ' 条';
    
    const chartDom = document.getElementById('messageChart');
    if (!chartDom || typeof echarts === 'undefined') return;
    
    const chart = echarts.init(chartDom);
    
    const option = {
        tooltip: {
            trigger: 'item',
            formatter: '{b}: {c} 条 ({d}%)'
        },
        series: [{
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['50%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
                borderRadius: 8,
                borderColor: '#fff',
                borderWidth: 2
            },
            label: {
                show: false,
                position: 'center'
            },
            emphasis: {
                label: {
                    show: true,
                    fontSize: 14,
                    fontWeight: 'bold'
                }
            },
            labelLine: {
                show: false
            },
            data: [
                {
                    value: otherCount,
                    name: '对方',
                    itemStyle: {
                        color: '#4a6cf7'
                    }
                },
                {
                    value: myCount,
                    name: '我',
                    itemStyle: {
                        color: '#a0aec0'
                    }
                }
            ]
        }]
    };
    
    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
}

function renderQuickInsights(parsed) {
    const insightsList = document.getElementById('quickInsights');
    if (!insightsList) return;
    
    const insights = [];
    
    if (parsed.interests && Array.isArray(parsed.interests) && parsed.interests.length > 0) {
        const topInterests = parsed.interests.slice(0, 3);
        insights.push({
            icon: '🎯',
            text: `兴趣关键词: ${topInterests.join('、')}`
        });
    }
    
    if (parsed.dos_and_donts) {
        const dos = parsed.dos_and_donts.dos || [];
        if (dos.length > 0) {
            insights.push({
                icon: '✅',
                text: `适合: ${dos[0]}`
            });
        }
    }
    
    const chatItems = document.querySelectorAll('.chat-item');
    if (chatItems.length > 0) {
        const dates = new Set();
        chatItems.forEach(item => {
            const date = item.dataset.date;
            if (date) dates.add(date);
        });
        const activeDays = dates.size;
        insights.push({
            icon: '📅',
            text: `活跃天数: ${activeDays} 天`
        });
    }
    
    if (parsed.core_traits) {
        const traits = parsed.core_traits;
        if (traits.introversion) {
            const introText = traits.introversion.includes('外向') || traits.introversion.includes('开朗') ? '外向活跃' : '内向沉稳';
            insights.push({
                icon: '💬',
                text: `性格倾向: ${introText}`
            });
        }
    }
    
    insightsList.innerHTML = '';
    insights.forEach(insight => {
        const item = document.createElement('div');
        item.className = 'insight-item';
        item.innerHTML = `
            <span class="insight-icon">${insight.icon}</span>
            <span class="insight-text">${insight.text}</span>
        `;
        insightsList.appendChild(item);
    });
    
    if (insights.length === 0) {
        insightsList.innerHTML = `
            <div class="insight-item">
                <span class="insight-icon">📊</span>
                <span class="insight-text">开始分析后查看洞察</span>
            </div>
        `;
    }
}

function renderWordCloud(keywords) {
    const container = document.getElementById('wordCloud');
    if (!container) return;
    
    container.innerHTML = '';
    
    const colors = ['#4a6cf7', '#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe'];
    const sizes = [0.8, 1, 1.2, 1.4, 1.6];
    
    keywords.forEach((keyword, index) => {
        const tag = document.createElement('span');
        tag.className = 'keyword-tag';
        tag.textContent = keyword;
        tag.style.color = colors[index % colors.length];
        tag.style.fontSize = sizes[index % sizes.length] + 'rem';
        tag.style.animationDelay = (index * 0.1) + 's';
        container.appendChild(tag);
    });
}

function renderTraitDetails(parsed) {
    const mapping = {
        'coreTraitsList': parsed.core_traits || {},
        'behaviorList': parsed.behavior_preferences || {},
        'socialList': parsed.social_interaction || {},
        'cognitiveList': parsed.cognitive_thinking || {}
    };
    
    const labelMapping = {
        'rationality': '理性程度',
        'introversion': '内向程度',
        'planning': '计划性',
        'responsibility': '责任态度',
        'stress_resistance': '抗压能力',
        'decision_style': '决策风格',
        'high_frequency_topics': '高频话题',
        'interests': '兴趣领域',
        'hobbies': '爱好',
        'preferences': '明确偏好',
        'avoidances': '回避事项',
        'lifestyle': '生活方式',
        'initiative': '主动性',
        'expression_style': '表达风格',
        'response_pattern': '反馈效率',
        'empathy': '共情能力',
        'sharing_willingness': '分享欲',
        'boundary_awareness': '边界感',
        'collaboration_style': '协作风格',
        'knowledge_depth': '知识深度',
        'knowledge_breadth': '知识广度',
        'values': '价值观',
        'principles': '底线原则'
    };
    
    Object.entries(mapping).forEach(([containerId, data]) => {
        const container = document.getElementById(containerId);
        if (!container || !data) return;
        
        container.innerHTML = '';
        
        Object.entries(data).forEach(([key, value]) => {
            const label = labelMapping[key] || key;
            const item = document.createElement('div');
            item.className = 'trait-item';
            item.innerHTML = `
                <span class="trait-label">${label}</span>
                <span class="trait-value">${value}</span>
            `;
            container.appendChild(item);
        });
    });
}

function renderInterests(parsed) {
    const behavior = parsed.behavior_preferences || {};
    
    if (behavior.high_frequency_topics) {
        const container = document.getElementById('highFrequencyTopics');
        if (container) {
            container.innerHTML = '';
            (Array.isArray(behavior.high_frequency_topics) ? behavior.high_frequency_topics : [behavior.high_frequency_topics]).forEach(topic => {
                const tag = document.createElement('span');
                tag.className = 'tag';
                tag.textContent = topic;
                container.appendChild(tag);
            });
        }
    }
    
    if (behavior.interests) {
        const container = document.getElementById('interestsList');
        if (container) {
            container.innerHTML = '';
            (Array.isArray(behavior.interests) ? behavior.interests : [behavior.interests]).forEach(interest => {
                const tag = document.createElement('span');
                tag.className = 'tag';
                tag.textContent = interest;
                container.appendChild(tag);
            });
        }
    }
    
    if (behavior.lifestyle) {
        const el = document.getElementById('lifestyleContent');
        if (el) el.textContent = behavior.lifestyle;
    }
    
    const social = parsed.social_interaction || {};
    if (social.expression_style) {
        const el = document.getElementById('expressionContent');
        if (el) el.textContent = social.expression_style;
    }
}

function renderGuide(parsed) {
    const dosAndDonts = parsed.dos_and_donts || {};
    
    const dos = dosAndDonts.dos || [];
    const donts = dosAndDonts.donts || [];
    
    const dosList = document.getElementById('dosList');
    const dontsList = document.getElementById('dontsList');
    
    if (dosList) {
        dosList.innerHTML = '';
        dos.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            dosList.appendChild(li);
        });
    }
    
    if (dontsList) {
        dontsList.innerHTML = '';
        donts.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            dontsList.appendChild(li);
        });
    }
    
    const topicSuggestions = parsed.topic_suggestions || [];
    const topicList = document.getElementById('topicSuggestions');
    if (topicList) {
        topicList.innerHTML = '';
        topicSuggestions.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            topicList.appendChild(li);
        });
    }
    
    const giftSuggestions = parsed.gift_suggestions || [];
    const giftList = document.getElementById('giftSuggestions');
    if (giftList) {
        giftList.innerHTML = '';
        giftSuggestions.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            giftList.appendChild(li);
        });
    }
}

async function startAnalysis() {
    console.log('[Frontend] startAnalysis() called');
    const contactId = window.location.pathname.split('/').pop();
    console.log('[Frontend] contactId:', contactId);
    
    const modal = document.getElementById('analysisModal');
    const progressBar = document.getElementById('analysisProgress');
    const progressText = document.getElementById('progressText');
    const generatedTokensEl = document.getElementById('generatedTokens');
    const totalTokensEl = document.getElementById('totalTokens');
    const analysisStatus = document.getElementById('analysisStatus');
    const modalTitle = modal.querySelector('.modal-header h2');
    
    if (modal) modal.classList.add('show');
    if (modalTitle) modalTitle.textContent = 'AI分析中...';
    if (progressBar) progressBar.style.width = '5%';
    if (progressText) progressText.textContent = '5%';
    if (generatedTokensEl) generatedTokensEl.textContent = '0';
    if (totalTokensEl) totalTokensEl.textContent = '0';
    if (analysisStatus) analysisStatus.textContent = '正在连接AI服务...';
    
    updateStep(1);
    
    try {
        const apiKeyInput = document.getElementById('apiKey');
        const apiKey = apiKeyInput ? apiKeyInput.value : null;
        
        const response = await fetch(`/api/contacts/${contactId}/analyze/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ api_key: apiKey })
        });
        
        if (!response.ok) {
            throw new Error('请求失败');
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        if (analysisStatus) analysisStatus.textContent = '正在分析聊天记录...';
        updateStep(2);
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';
            
            for (const line of lines) {
                if (line.trim()) {
                    try {
                        const data = JSON.parse(line);
                        
                        if (data.type === 'content_update') {
                            const contentLength = data.content_length || 0;
                            const total = data.total_tokens || 0;
                            const completion = data.completion_tokens || 0;
                            
                            if (generatedTokensEl) generatedTokensEl.textContent = completion.toLocaleString();
                            if (totalTokensEl) totalTokensEl.textContent = total.toLocaleString();
                            
                            const progress = Math.min(95, 20 + (contentLength / 100) * 75);
                            if (progressBar) progressBar.style.width = progress + '%';
                            if (progressText) progressText.textContent = Math.round(progress) + '%';
                            
                            if (contentLength > 50) {
                                updateStep(3);
                            }
                        } else if (data.type === 'token_update') {
                            const total = data.total_tokens || 0;
                            const completion = data.completion_tokens || 0;
                            
                            if (generatedTokensEl) generatedTokensEl.textContent = completion.toLocaleString();
                            if (totalTokensEl) totalTokensEl.textContent = total.toLocaleString();
                            
                            const progress = Math.min(95, 20 + (completion / 2000) * 75);
                            if (progressBar) progressBar.style.width = progress + '%';
                            if (progressText) progressText.textContent = Math.round(progress) + '%';
                            
                            if (completion > 500) {
                                updateStep(3);
                            }
                        } else if (data.type === 'error') {
                            throw new Error(data.message);
                        } else if (data.type === 'complete') {
                            if (progressBar) progressBar.style.width = '100%';
                            if (progressText) progressText.textContent = '100%';
                            if (generatedTokensEl) generatedTokensEl.textContent = (data.completion_tokens || 0).toLocaleString();
                            if (totalTokensEl) totalTokensEl.textContent = (data.total_tokens || 0).toLocaleString();
                            if (analysisStatus) analysisStatus.textContent = '分析完成！';
                            
                            document.getElementById('analysisSpinner').style.display = 'none';
                            document.getElementById('analysisHint').style.display = 'none';
                            
                            const rawDataSection = document.getElementById('rawDataSection');
                            const rawDataContent = document.getElementById('rawDataContent');
                            const analysisActions = document.getElementById('analysisActions');
                            
                            if (rawDataContent) rawDataContent.textContent = JSON.stringify(data.analysis, null, 2);
                            if (rawDataSection) rawDataSection.style.display = 'block';
                            if (analysisActions) analysisActions.style.display = 'block';
                            
                            updateStep(3);
                            return;
                        }
                    } catch (e) {
                        continue;
                    }
                }
            }
        }
        
    } catch (error) {
        console.error('Analysis Error:', error);
        
        if (modal) modal.classList.remove('show');
        
        showToast(error.message || '分析失败，请重试', 'error');
    }
}

function toggleRawData() {
    const rawDataContent = document.getElementById('rawDataContent');
    if (rawDataContent.style.maxHeight === '300px') {
        rawDataContent.style.maxHeight = 'none';
    } else {
        rawDataContent.style.maxHeight = '300px';
    }
}

function finishAnalysis() {
    const modal = document.getElementById('analysisModal');
    if (modal) modal.classList.remove('show');
    showToast('分析完成！', 'success');
    setTimeout(() => {
        window.location.reload();
    }, 500);
}

function toggleChatViewMode() {
    const container = document.getElementById('chatsContainer');
    const viewModeIcon = document.getElementById('viewModeIcon');
    const viewModeText = document.getElementById('viewModeText');
    
    if (!container) return;
    
    const isCompact = container.classList.contains('compact-view');
    
    if (isCompact) {
        container.classList.remove('compact-view');
        container.classList.add('expanded-view');
        if (viewModeIcon) viewModeIcon.textContent = '📋';
        if (viewModeText) viewModeText.textContent = '紧凑视图';
        localStorage.setItem('chatViewMode', 'expanded');
    } else {
        container.classList.remove('expanded-view');
        container.classList.add('compact-view');
        if (viewModeIcon) viewModeIcon.textContent = '📝';
        if (viewModeText) viewModeText.textContent = '展开视图';
        localStorage.setItem('chatViewMode', 'compact');
    }
}

function filterChats() {
    const searchText = document.getElementById('chatSearch')?.value?.toLowerCase() || '';
    const dateFilter = document.getElementById('chatDateFilter')?.value || 'all';
    
    const chatItems = document.querySelectorAll('.chat-item');
    const dateGroups = document.querySelectorAll('.chat-date-group');
    
    let visibleDates = new Set();
    
    chatItems.forEach(item => {
        const content = item.querySelector('.chat-content')?.textContent?.toLowerCase() || '';
        const itemDate = item.dataset.date;
        let visible = true;
        
        if (searchText && !content.includes(searchText)) {
            visible = false;
        }
        
        if (dateFilter !== 'all' && itemDate !== dateFilter) {
            visible = false;
        }
        
        item.style.display = visible ? '' : 'none';
        
        if (visible && itemDate) {
            visibleDates.add(itemDate);
        }
    });
    
    dateGroups.forEach(group => {
        const groupDate = group.dataset.date;
        const hasVisibleItems = group.querySelectorAll('.chat-item[style=""]').length > 0 ||
                               group.querySelectorAll('.chat-item:not([style*="display: none"])').length > 0;
        group.style.display = hasVisibleItems ? '' : 'none';
    });
    
    updateDateFilterOptions();
}

function updateDateFilterOptions() {
    const dateFilter = document.getElementById('chatDateFilter');
    if (!dateFilter) return;
    
    const availableDates = new Set();
    document.querySelectorAll('.chat-item').forEach(item => {
        const date = item.dataset.date;
        if (date && item.style.display !== 'none') {
            availableDates.add(date);
        }
    });
    
    const currentValue = dateFilter.value;
    const options = dateFilter.querySelectorAll('option');
    options.forEach((option, index) => {
        if (index > 0) {
            option.style.display = availableDates.has(option.value) ? '' : 'none';
        }
    });
    
    if (currentValue !== 'all' && !availableDates.has(currentValue)) {
        dateFilter.value = 'all';
    }
}

function showQuickActionsToolbar() {
    let toolbar = document.getElementById('quickActionsToolbar');
    
    if (!toolbar) {
        toolbar = document.createElement('div');
        toolbar.id = 'quickActionsToolbar';
        toolbar.className = 'quick-actions-toolbar';
        toolbar.innerHTML = `
            <div class="toolbar-content">
                <div class="toolbar-info">
                    <span class="toolbar-count" id="quickSelectedCount">0</span>
                    <span class="toolbar-label">条已选择</span>
                </div>
                <div class="toolbar-buttons">
                    <button class="quick-action-btn" onclick="analyzeSelectedMessages()" title="分析选中">
                        <span class="btn-icon">🤖</span>
                        <span class="btn-text">分析</span>
                    </button>
                    <button class="quick-action-btn" onclick="exportSelectedMessages()" title="导出选中">
                        <span class="btn-icon">📤</span>
                        <span class="btn-text">导出</span>
                    </button>
                    <button class="quick-action-btn" onclick="copySelectedMessages()" title="复制内容">
                        <span class="btn-icon">📋</span>
                        <span class="btn-text">复制</span>
                    </button>
                    <div class="toolbar-divider"></div>
                    <button class="quick-action-btn secondary" onclick="clearSelection()" title="取消选择">
                        <span class="btn-icon">✕</span>
                        <span class="btn-text">取消</span>
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(toolbar);
    }
    
    const selectedCount = document.querySelectorAll('.chat-select-checkbox:checked').length;
    const countEl = document.getElementById('quickSelectedCount');
    if (countEl) {
        countEl.textContent = selectedCount;
    }
    
    toolbar.classList.toggle('visible', selectedCount > 0);
}

function hideQuickActionsToolbar() {
    const toolbar = document.getElementById('quickActionsToolbar');
    if (toolbar) {
        toolbar.classList.remove('visible');
    }
}

function exportSelectedMessages() {
    const checkboxes = document.querySelectorAll('.chat-select-checkbox:checked');
    const selectedIds = Array.from(checkboxes).map(cb => parseInt(cb.value));
    
    if (selectedIds.length === 0) {
        showToast('请先选择要导出的聊天记录', 'warning');
        return;
    }
    
    const chatItems = document.querySelectorAll('.chat-item');
    let exportContent = '';
    
    chatItems.forEach(item => {
        const checkbox = item.querySelector('.chat-select-checkbox');
        if (checkbox && checkbox.checked) {
            const speaker = item.classList.contains('me') ? '我' : '对方';
            const time = item.dataset.time || '';
            const content = item.querySelector('.chat-content')?.textContent || '';
            exportContent += `[${time}] ${speaker}: ${content}\n`;
        }
    });
    
    const blob = new Blob([exportContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'selected_chats.txt';
    a.click();
    URL.revokeObjectURL(url);
    
    showToast(`已导出 ${selectedIds.length} 条聊天记录`, 'success');
}

function copySelectedMessages() {
    const checkboxes = document.querySelectorAll('.chat-select-checkbox:checked');
    const selectedIds = Array.from(checkboxes).map(cb => parseInt(cb.value));
    
    if (selectedIds.length === 0) {
        showToast('请先选择要复制的聊天记录', 'warning');
        return;
    }
    
    const chatItems = document.querySelectorAll('.chat-item');
    let copyText = '';
    
    chatItems.forEach(item => {
        const checkbox = item.querySelector('.chat-select-checkbox');
        if (checkbox && checkbox.checked) {
            const speaker = item.classList.contains('me') ? '我' : '对方';
            const time = item.dataset.time || '';
            const content = item.querySelector('.chat-content')?.textContent || '';
            copyText += `[${time}] ${speaker}: ${content}\n`;
        }
    });
    
    navigator.clipboard.writeText(copyText).then(() => {
        showToast(`已复制 ${selectedIds.length} 条聊天记录`, 'success');
    }).catch(err => {
        showToast('复制失败，请手动复制', 'error');
    });
}

function clearSelection() {
    const checkboxes = document.querySelectorAll('.chat-select-checkbox:checked');
    checkboxes.forEach(cb => cb.checked = false);
    
    const selectAllCheckbox = document.getElementById('selectAllChats');
    if (selectAllCheckbox) selectAllCheckbox.checked = false;
    
    updateSelectedCount();
    showQuickActionsToolbar();
}

function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey || e.metaKey) {
            if (e.key === 'a') {
                e.preventDefault();
                const selectAllCheckbox = document.getElementById('selectAllChats');
                if (selectAllCheckbox) {
                    selectAllCheckbox.checked = !selectAllCheckbox.checked;
                    toggleSelectAllChats();
                }
            } else if (e.key === 'c') {
                if (document.activeElement?.tagName !== 'INPUT' && document.activeElement?.tagName !== 'TEXTAREA') {
                    e.preventDefault();
                    copySelectedMessages();
                }
            }
        } else if (e.key === 'Escape') {
            clearSelection();
        }
    });
}

function initClickSelection() {
    const chatItems = document.querySelectorAll('.chat-item');
    
    chatItems.forEach(item => {
        item.addEventListener('click', function(e) {
            if (e.target.type === 'checkbox' || e.target.closest('.chat-checkbox')) {
                return;
            }
            
            if (e.ctrlKey || e.metaKey) {
                const checkbox = this.querySelector('.chat-select-checkbox');
                if (checkbox) {
                    checkbox.checked = !checkbox.checked;
                    updateSelectedCount();
                    showQuickActionsToolbar();
                }
            } else if (e.shiftKey) {
                selectRange(this);
            }
        });
        
        item.addEventListener('dblclick', function() {
            expandChatItem(this);
        });
    });
}

let isDragging = false;
let dragStartItem = null;
let dragEndItem = null;
let dragSelectionMode = 'add';

function initDragSelection() {
    const container = document.getElementById('chatsContainer');
    if (!container) return;
    
    let startX, startY;
    
    container.addEventListener('mousedown', function(e) {
        if (e.button !== 0) return;
        if (e.target.type === 'checkbox' || e.target.closest('.chat-checkbox')) return;
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        
        isDragging = true;
        dragStartItem = e.target.closest('.chat-item');
        
        if (dragStartItem) {
            const checkbox = dragStartItem.querySelector('.chat-select-checkbox');
            dragSelectionMode = checkbox && checkbox.checked ? 'remove' : 'add';
        }
        
        startX = e.clientX;
        startY = e.clientY;
        
        document.body.style.userSelect = 'none';
        document.body.style.cursor = 'crosshair';
    });
    
    document.addEventListener('mousemove', function(e) {
        if (!isDragging || !dragStartItem) return;
        
        const currentItem = e.target.closest('.chat-item');
        if (currentItem && currentItem !== dragEndItem) {
            dragEndItem = currentItem;
            updateDragSelection();
        }
    });
    
    document.addEventListener('mouseup', function(e) {
        if (!isDragging) return;
        
        isDragging = false;
        dragStartItem = null;
        dragEndItem = null;
        
        document.body.style.userSelect = '';
        document.body.style.cursor = '';
        
        updateSelectedCount();
        showQuickActionsToolbar();
    });
}

function updateDragSelection() {
    if (!dragStartItem || !dragEndItem) return;
    
    const allItems = Array.from(document.querySelectorAll('.chat-item'));
    const startIndex = allItems.indexOf(dragStartItem);
    const endIndex = allItems.indexOf(dragEndItem);
    
    const start = Math.min(startIndex, endIndex);
    const end = Math.max(startIndex, endIndex);
    
    for (let i = start; i <= end; i++) {
        const checkbox = allItems[i].querySelector('.chat-select-checkbox');
        if (checkbox) {
            checkbox.checked = dragSelectionMode === 'add';
        }
    }
}

function clearDragSelection() {
    const allItems = document.querySelectorAll('.chat-item');
    allItems.forEach(item => {
        item.classList.remove('selection-range');
    });
}

let lastSelectedItem = null;

function selectRange(currentItem) {
    if (!lastSelectedItem) {
        const checkbox = currentItem.querySelector('.chat-select-checkbox');
        if (checkbox) {
            checkbox.checked = true;
            lastSelectedItem = currentItem;
            updateSelectedCount();
            showQuickActionsToolbar();
        }
        return;
    }
    
    const allItems = Array.from(document.querySelectorAll('.chat-item'));
    const currentIndex = allItems.indexOf(currentItem);
    const lastIndex = allItems.indexOf(lastSelectedItem);
    
    const start = Math.min(currentIndex, lastIndex);
    const end = Math.max(currentIndex, lastIndex);
    
    for (let i = start; i <= end; i++) {
        const checkbox = allItems[i].querySelector('.chat-select-checkbox');
        if (checkbox) {
            checkbox.checked = true;
        }
    }
    
    lastSelectedItem = currentItem;
    updateSelectedCount();
    showQuickActionsToolbar();
}

function expandChatItem(item) {
    item.classList.toggle('expanded');
    const content = item.querySelector('.chat-content');
    if (content) {
        content.classList.toggle('expanded');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initTabs();
    renderMessageDistribution();
    loadAnalysisIfExists();
    initKeyboardShortcuts();
    initClickSelection();
    initDragSelection();
    
    const savedMode = localStorage.getItem('chatViewMode');
    if (savedMode === 'compact') {
        const container = document.getElementById('chatsContainer');
        const viewModeIcon = document.getElementById('viewModeIcon');
        const viewModeText = document.getElementById('viewModeText');
        if (container) container.classList.add('compact-view');
        if (viewModeIcon) viewModeIcon.textContent = '📝';
        if (viewModeText) viewModeText.textContent = '展开视图';
    }
    
    populateDateFilter();
});

function populateDateFilter() {
    const dateFilter = document.getElementById('chatDateFilter');
    if (!dateFilter) return;
    
    const dates = new Set();
    document.querySelectorAll('.chat-item').forEach(item => {
        const date = item.dataset.date;
        if (date) dates.add(date);
    });
    
    const sortedDates = Array.from(dates).sort();
    
    sortedDates.forEach(date => {
        const option = document.createElement('option');
        option.value = date;
        
        const dateObj = new Date(date);
        const month = dateObj.getMonth() + 1;
        const day = dateObj.getDate();
        const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
        const weekday = weekdays[dateObj.getDay()];
        
        option.textContent = `${month}月${day}日 ${weekday}`;
        dateFilter.appendChild(option);
    });
}

function renderTimeline() {
    const chatItems = document.querySelectorAll('.chat-item');
    
    if (chatItems.length === 0) {
        renderEmptyTimeline();
        return;
    }
    
    const activityData = {};
    chatItems.forEach(item => {
        const date = item.dataset.date;
        if (date) {
            activityData[date] = (activityData[date] || 0) + 1;
        }
    });
    
    renderHeatmap(activityData);
    renderTimelineSummary(activityData);
    renderActivitySummary(activityData);
    renderRecentActivity(activityData);
}

function renderEmptyTimeline() {
    const container = document.getElementById('timelineVisual');
    if (!container) return;
    
    container.innerHTML = `
        <div class="heatmap-container">
            <p class="timeline-placeholder">导入聊天记录后查看互动时间线</p>
        </div>
    `;
    
    const summaryContainer = document.getElementById('activitySummary');
    const recentContainer = document.getElementById('recentActivity');
    if (summaryContainer) {
        summaryContainer.innerHTML = '<p class="empty-state">暂无数据</p>';
    }
    if (recentContainer) {
        recentContainer.innerHTML = '<p class="empty-state">暂无数据</p>';
    }
}

function renderHeatmap(activityData) {
    const container = document.getElementById('timelineHeatmap');
    if (!container) return;
    
    const dates = Object.keys(activityData).sort();
    
    if (dates.length === 0) {
        container.innerHTML = '<p class="timeline-placeholder">暂无互动数据</p>';
        return;
    }
    
    const today = new Date();
    const sixMonthsAgo = new Date(today);
    sixMonthsAgo.setMonth(today.getMonth() - 6);
    
    const weeks = [];
    let currentDate = new Date(sixMonthsAgo);
    currentDate.setDate(currentDate.getDate() - currentDate.getDay());
    
    while (currentDate <= today) {
        const weekData = [];
        for (let i = 0; i < 7; i++) {
            const dateStr = currentDate.toISOString().split('T')[0];
            const count = activityData[dateStr] || 0;
            weekData.push({
                date: dateStr,
                count: count,
                level: getActivityLevel(count)
            });
            currentDate.setDate(currentDate.getDate() + 1);
        }
        weeks.push(weekData);
    }
    
    let html = '';
    
    const months = ['1月', '2月', '3月', '4月', '5月', '6月'];
    const currentMonth = today.getMonth();
    
    html += `<div class="timeline-months">`;
    for (let i = 0; i < 6; i++) {
        const monthIndex = (currentMonth - 5 + i + 12) % 12;
        html += `<span class="month-label" style="flex: ${i === 5 ? 1 : 4}">${months[monthIndex]}</span>`;
    }
    html += `</div>`;
    
    const dayLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    
    html += `<div class="timeline-heatmap">`;
    for (let day = 0; day < 7; day++) {
        html += `
            <div class="heatmap-row">
                <span class="heatmap-label">${dayLabels[day]}</span>
                <div class="heatmap-grid">
        `;
        
        for (let week = 0; week < weeks.length; week++) {
            const cell = weeks[week][day];
            const tooltip = cell.count > 0 ? `${cell.date}: ${cell.count} 条消息` : cell.date;
            html += `<div class="heatmap-cell ${cell.level}" data-tooltip="${tooltip}"></div>`;
        }
        
        html += `
                </div>
            </div>
        `;
    }
    html += `</div>`;
    
    container.innerHTML = html;
}

function getActivityLevel(count) {
    if (count === 0) return 'empty';
    if (count <= 2) return 'low';
    if (count <= 5) return 'medium';
    if (count <= 10) return 'high';
    return 'highest';
}

function renderTimelineSummary(activityData) {
    const dates = Object.keys(activityData);
    const totalDays = dates.length;
    const totalMessages = Object.values(activityData).reduce((sum, count) => sum + count, 0);
    
    let longestStreak = 0;
    let currentStreak = 0;
    const sortedDates = dates.sort();
    
    for (let i = 0; i < sortedDates.length; i++) {
        if (i === 0) {
            currentStreak = 1;
        } else {
            const prevDate = new Date(sortedDates[i - 1]);
            const currDate = new Date(sortedDates[i]);
            const diffDays = (currDate - prevDate) / (1000 * 60 * 60 * 24);
            
            if (diffDays === 1) {
                currentStreak++;
            } else {
                longestStreak = Math.max(longestStreak, currentStreak);
                currentStreak = 1;
            }
        }
    }
    longestStreak = Math.max(longestStreak, currentStreak);
    
    const avgMessagesPerDay = totalDays > 0 ? (totalMessages / totalDays).toFixed(1) : 0;
    
    let peakDate = '';
    let peakCount = 0;
    Object.entries(activityData).forEach(([date, count]) => {
        if (count > peakCount) {
            peakCount = count;
            peakDate = date;
        }
    });
    
    const container = document.getElementById('timelineVisual');
    if (!container) return;
    
    container.innerHTML = `
        <div class="heatmap-container">
            <div class="heatmap-header">
                <span class="heatmap-title">活跃度热力图</span>
                <div class="timeline-legend">
                    <span class="legend-item"><span class="legend-color" style="background: #e8f5e9"></span> 无</span>
                    <span class="legend-item"><span class="legend-color low"></span> 1-2</span>
                    <span class="legend-item"><span class="legend-color medium"></span> 3-5</span>
                    <span class="legend-item"><span class="legend-color high"></span> 6-10</span>
                    <span class="legend-item"><span class="legend-color highest"></span> 10+</span>
                </div>
            </div>
            <div class="timeline-heatmap" id="timelineHeatmap">
                <p class="timeline-placeholder">加载中...</p>
            </div>
        </div>
    `;
    
    const heatmapContainer = document.getElementById('timelineHeatmap');
    if (heatmapContainer) {
        const heatmapHTML = generateHeatmapHTML(activityData);
        heatmapContainer.innerHTML = heatmapHTML;
    }
}

function generateHeatmapHTML(activityData) {
    const today = new Date();
    const sixMonthsAgo = new Date(today);
    sixMonthsAgo.setMonth(today.getMonth() - 6);
    
    const weeks = [];
    let currentDate = new Date(sixMonthsAgo);
    currentDate.setDate(currentDate.getDate() - currentDate.getDay());
    
    while (currentDate <= today) {
        const weekData = [];
        for (let i = 0; i < 7; i++) {
            const dateStr = currentDate.toISOString().split('T')[0];
            const count = activityData[dateStr] || 0;
            weekData.push({
                date: dateStr,
                count: count,
                level: getActivityLevel(count)
            });
            currentDate.setDate(currentDate.getDate() + 1);
        }
        weeks.push(weekData);
    }
    
    let html = '';
    
    const months = ['1月', '2月', '3月', '4月', '5月', '6月'];
    const currentMonth = today.getMonth();
    
    html += `<div class="timeline-months">`;
    for (let i = 0; i < 6; i++) {
        const monthIndex = (currentMonth - 5 + i + 12) % 12;
        html += `<span class="month-label" style="flex: ${i === 5 ? 1 : 4}">${months[monthIndex]}</span>`;
    }
    html += `</div>`;
    
    const dayLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    
    html += `<div class="timeline-heatmap">`;
    for (let day = 0; day < 7; day++) {
        html += `<div class="heatmap-row"><span class="heatmap-label">${dayLabels[day]}</span><div class="heatmap-grid">`;
        for (let week = 0; week < weeks.length; week++) {
            const cell = weeks[week][day];
            const tooltip = cell.count > 0 ? `${cell.date}: ${cell.count} 条消息` : cell.date;
            html += `<div class="heatmap-cell ${cell.level}" data-tooltip="${tooltip}"></div>`;
        }
        html += `</div></div>`;
    }
    html += `</div>`;
    
    return html;
}

function renderActivitySummary(activityData) {
    const dates = Object.keys(activityData).sort();
    const totalDays = dates.length;
    const totalMessages = Object.values(activityData).reduce((sum, count) => sum + count, 0);
    
    let peakDate = '';
    let peakCount = 0;
    Object.entries(activityData).forEach(([date, count]) => {
        if (count > peakCount) {
            peakCount = count;
            peakDate = date;
        }
    });
    
    const peakDayEl = document.getElementById('peakDay');
    const avgDailyEl = document.getElementById('avgDaily');
    const activeWeeksEl = document.getElementById('activeWeeks');
    
    if (peakDayEl) {
        peakDayEl.textContent = peakDate ? formatDate(peakDate) : '-';
    }
    if (avgDailyEl) {
        avgDailyEl.textContent = totalDays > 0 ? (totalMessages / totalDays).toFixed(1) : '-';
    }
    if (activeWeeksEl) {
        activeWeeksEl.textContent = totalDays > 0 ? Math.ceil(totalDays / 7) : '-';
    }
    
    const peakHourEl = document.getElementById('peakHour');
    if (peakHourEl) {
        const chatItems = document.querySelectorAll('.chat-item');
        const hourCounts = {};
        chatItems.forEach(item => {
            const time = item.dataset.time;
            if (time) {
                const hour = time.split(':')[0];
                hourCounts[hour] = (hourCounts[hour] || 0) + 1;
            }
        });
        
        let peakHour = '';
        let maxHourCount = 0;
        Object.entries(hourCounts).forEach(([hour, count]) => {
            if (count > maxHourCount) {
                maxHourCount = count;
                peakHour = hour;
            }
        });
        
        if (peakHour) {
            const hourInt = parseInt(peakHour);
            const period = hourInt < 12 ? '上午' : (hourInt < 18 ? '下午' : '晚上');
            peakHourEl.textContent = `${period} ${hourInt}:00`;
        } else {
            peakHourEl.textContent = '-';
        }
    }
}

function renderRecentActivity(activityData) {
    const container = document.getElementById('recentActivity');
    if (!container) return;
    
    const sortedDates = Object.entries(activityData)
        .sort((a, b) => new Date(b[0]) - new Date(a[0]))
        .slice(0, 5);
    
    if (sortedDates.length === 0) {
        container.innerHTML = '<p class="empty-state">暂无数据</p>';
        return;
    }
    
    let html = '<div class="activity-list-inner">';
    sortedDates.forEach(([date, count]) => {
        html += `
            <div class="activity-item">
                <span class="activity-date">${formatDate(date)}</span>
                <span class="activity-count">${count} 条</span>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    return `${month}月${day}日`;
}

function toggleSelectAllChats() {
    const selectAllCheckbox = document.getElementById('selectAllChats');
    const checkboxes = document.querySelectorAll('.chat-select-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
    });
    updateSelectedCount();
}

function updateSelectedCount() {
    const checkboxes = document.querySelectorAll('.chat-select-checkbox:checked');
    const count = checkboxes.length;
    
    const selectedCountEl = document.getElementById('selectedCount');
    if (selectedCountEl) {
        selectedCountEl.textContent = `已选择 ${count} 条`;
    }
    
    const analyzeBtn = document.getElementById('analyzeSelectedBtn');
    if (analyzeBtn) {
        analyzeBtn.disabled = count === 0;
    }
    updateSelectAllState();
}

function updateSelectAllState() {
    const checkboxes = document.querySelectorAll('.chat-select-checkbox');
    const selectAllCheckbox = document.getElementById('selectAllChats');
    if (selectAllCheckbox && checkboxes.length > 0) {
        const checkedCount = document.querySelectorAll('.chat-select-checkbox:checked').length;
        selectAllCheckbox.checked = checkedCount === checkboxes.length;
        selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < checkboxes.length;
    }
}

let analysisCancelled = false;

function simulateProgress(progressBar, progressText) {
    analysisCancelled = false;
    let progress = 0;
    
    const animate = () => {
        if (analysisCancelled) return;
        
        progress += Math.random() * 15;
        if (progress > 95) progress = 95;
        
        progressBar.style.width = progress + '%';
        progressText.textContent = Math.round(progress) + '%';
        
        if (progress < 95) {
            setTimeout(animate, 300 + Math.random() * 500);
        }
    };
    
    animate();
}

function cancelAnalysis() {
    analysisCancelled = true;
    const modal = document.getElementById('analysisModal');
    if (modal) modal.classList.remove('show');
    showToast('已取消分析', 'info');
}

function updateStep(step) {
    const steps = document.querySelectorAll('.step-item');
    steps.forEach((s, index) => {
        s.classList.toggle('active', index < step);
        const check = s.querySelector('.step-check');
        if (check) {
            check.textContent = index < step ? '✓' : '○';
        }
    });
}

async function analyzeSelectedMessages() {
    console.log('[Frontend] analyzeSelectedMessages() called');
    const contactId = window.location.pathname.split('/').pop();
    console.log('[Frontend] contactId:', contactId);
    const checkboxes = document.querySelectorAll('.chat-select-checkbox:checked');
    const selectedIds = Array.from(checkboxes).map(cb => parseInt(cb.value));
    
    if (selectedIds.length === 0) {
        showToast('请先选择要分析的聊天记录', 'warning');
        return;
    }
    
    const modal = document.getElementById('analysisModal');
    const progressBar = document.getElementById('analysisProgress');
    const progressText = document.getElementById('progressText');
    const modalTitle = modal.querySelector('.modal-header h2');
    const generatedTokensEl = document.getElementById('generatedTokens');
    const totalTokensEl = document.getElementById('totalTokens');
    const analysisStatus = document.getElementById('analysisStatus');
    
    modal.classList.add('show');
    modalTitle.textContent = 'AI分析中...';
    progressBar.style.width = '5%';
    progressText.textContent = '5%';
    generatedTokensEl.textContent = '0';
    totalTokensEl.textContent = '0';
    analysisStatus.textContent = '正在连接AI服务...';
    
    updateStep(1);
    
    try {
        const apiKeyInput = document.getElementById('apiKey');
        const apiKey = apiKeyInput ? apiKeyInput.value : null;
        
        const response = await fetch(`/api/contacts/${contactId}/analyze-selected/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message_ids: selectedIds,
                api_key: apiKey
            })
        });
        
        if (!response.ok) {
            throw new Error('请求失败');
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        analysisStatus.textContent = '正在分析聊天记录...';
        updateStep(2);
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';
            
            for (const line of lines) {
                if (line.trim()) {
                    try {
                        const data = JSON.parse(line);
                        
                        if (data.type === 'content_update') {
                            const contentLength = data.content_length || 0;
                            
                            if (generatedTokensEl) generatedTokensEl.textContent = contentLength.toLocaleString();
                            if (totalTokensEl) totalTokensEl.textContent = contentLength.toLocaleString();
                            
                            const progress = Math.min(95, 20 + (contentLength / 100) * 75);
                            if (progressBar) progressBar.style.width = progress + '%';
                            if (progressText) progressText.textContent = Math.round(progress) + '%';
                            
                            if (contentLength > 50) {
                                updateStep(3);
                            }
                        } else if (data.type === 'token_update') {
                            const total = data.total_tokens || 0;
                            const completion = data.completion_tokens || 0;
                            
                            generatedTokensEl.textContent = completion.toLocaleString();
                            totalTokensEl.textContent = total.toLocaleString();
                            
                            const progress = Math.min(95, 20 + (completion / 2000) * 75);
                            progressBar.style.width = progress + '%';
                            progressText.textContent = Math.round(progress) + '%';
                            
                            if (completion > 500) {
                                updateStep(3);
                            }
                        } else if (data.type === 'error') {
                            throw new Error(data.message);
                        } else if (data.type === 'complete') {
                            progressBar.style.width = '100%';
                            progressText.textContent = '100%';
                            
                            analysisStatus.textContent = '分析完成！';
                            
                            document.getElementById('analysisSpinner').style.display = 'none';
                            document.getElementById('analysisHint').style.display = 'none';
                            
                            const rawDataSection = document.getElementById('rawDataSection');
                            const rawDataContent = document.getElementById('rawDataContent');
                            const analysisActions = document.getElementById('analysisActions');
                            
                            rawDataContent.textContent = JSON.stringify(data.analysis, null, 2);
                            rawDataSection.style.display = 'block';
                            analysisActions.style.display = 'block';
                            
                            updateStep(3);
                            return;
                        }
                    } catch (e) {
                        continue;
                    }
                }
            }
        }
        
    } catch (error) {
        console.error('Analysis Error:', error);
        
        if (modal) modal.classList.remove('show');
        
        showToast(error.message || '分析失败，请重试', 'error');
    }
}
