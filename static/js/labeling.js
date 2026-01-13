let parsedLines = [];
let currentStep = 1;
let activeIndex = -1;

document.addEventListener('DOMContentLoaded', function() {
    const dateInput = document.getElementById('chatDate');
    if (dateInput) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }
    
    initDragDrop();
    initKeyboardNav();
});

function initDragDrop() {
    const textarea = document.getElementById('chatTextarea');
    if (!textarea) return;
    
    const dropZone = textarea.parentElement;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    dropZone.addEventListener('dragenter', () => {
        dropZone.classList.add('drag-over');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });
    
    dropZone.addEventListener('drop', (e) => {
        dropZone.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (file.type.match('text.*') || file.name.endsWith('.txt')) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    textarea.value = event.target.result;
                    showToast('文件内容已加载', 'success');
                };
                reader.readAsText(file);
            } else {
                showToast('请上传文本文件', 'error');
            }
        }
    });
}

function initKeyboardNav() {
    document.addEventListener('keydown', (e) => {
        if (currentStep !== 2) return;
        
        const chatLines = document.querySelectorAll('.chat-line');
        if (chatLines.length === 0) return;
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                activeIndex = Math.min(activeIndex + 1, chatLines.length - 1);
                updateActiveLine(chatLines);
                break;
            case 'ArrowUp':
                e.preventDefault();
                activeIndex = Math.max(activeIndex - 1, 0);
                updateActiveLine(chatLines);
                break;
            case ' ':
            case 'Enter':
                e.preventDefault();
                if (activeIndex >= 0 && activeIndex < parsedLines.length) {
                    toggleSpeaker(activeIndex);
                    highlightChange(activeIndex);
                }
                break;
            case 'a':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    selectAll('对方');
                    highlightButton('btn-other');
                }
                break;
            case 'm':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    selectAll('我');
                    highlightButton('btn-me');
                }
                break;
            case 'i':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    invertSelect();
                }
                break;
        }
    });
}

function updateActiveLine(chatLines) {
    chatLines.forEach((line, index) => {
        line.classList.toggle('active', index === activeIndex);
        if (index === activeIndex) {
            line.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    });
}

function highlightButton(btnId) {
    const btn = document.querySelector(`[onclick*="${btnId}"]`);
    if (btn) {
        btn.classList.add('highlight');
        setTimeout(() => btn.classList.remove('highlight'), 500);
    }
}

function highlightChange(index) {
    const lineEl = document.querySelector(`.chat-line[data-index="${index}"]`);
    if (lineEl) {
        lineEl.classList.add('changed');
        setTimeout(() => lineEl.classList.remove('changed'), 500);
    }
}

function clearText() {
    document.getElementById('chatTextarea').value = '';
}

function parseChatText() {
    const text = document.getElementById('chatTextarea').value.trim();
    
    if (!text) {
        showToast('请先粘贴聊天记录', 'error');
        return;
    }
    
    const lines = text.split('\n').filter(line => line.trim());
    
    if (lines.length === 0) {
        showToast('没有有效的内容', 'error');
        return;
    }
    
    parsedLines = lines.map((content, index) => ({
        index: index + 1,
        content: content.trim(),
        speaker: '对方'
    }));
    
    renderChatLines();
    updateCounts();
    updateProgress();
    
    document.getElementById('inputSection').style.display = 'none';
    document.getElementById('labelingSection').style.display = 'block';
    document.querySelector('[data-step="1"]').classList.remove('active');
    document.querySelector('[data-step="1"]').classList.add('completed');
    document.querySelector('[data-step="2"]').classList.add('active');
    
    currentStep = 2;
    activeIndex = 0;
    
    setTimeout(() => {
        const firstLine = document.querySelector('.chat-line');
        if (firstLine) {
            firstLine.focus();
        }
    }, 100);
}

function renderChatLines() {
    const container = document.getElementById('chatLines');
    if (!container) return;
    
    container.innerHTML = '';
    
    parsedLines.forEach((line, index) => {
        const lineEl = document.createElement('div');
        lineEl.className = `chat-line ${line.speaker === '我' ? 'me' : 'other'}`;
        lineEl.dataset.index = index;
        lineEl.tabIndex = 0;
        lineEl.onclick = () => {
            activeIndex = index;
            updateActiveLine(document.querySelectorAll('.chat-line'));
            toggleSpeaker(index);
            highlightChange(index);
        };
        
        lineEl.innerHTML = `
            <span class="line-number">${line.index}</span>
            <span class="line-content">${escapeHtml(line.content)}</span>
            <span class="speaker-indicator">${line.speaker}</span>
        `;
        
        container.appendChild(lineEl);
    });
}

function updateCounts() {
    const otherCount = parsedLines.filter(l => l.speaker === '对方').length;
    const myCount = parsedLines.filter(l => l.speaker === '我').length;
    
    const otherEl = document.getElementById('otherCount');
    const myEl = document.getElementById('myCount');
    
    if (otherEl) otherEl.textContent = otherCount;
    if (myEl) myEl.textContent = myCount;
}

function updateProgress() {
    const total = parsedLines.length;
    const myCount = parsedLines.filter(l => l.speaker === '我').length;
    const percentage = Math.round((myCount / total) * 100);
    
    const progressBar = document.getElementById('labelProgress');
    if (progressBar) {
        progressBar.style.width = `${percentage}%`;
    }
    
    const progressText = document.getElementById('progressText');
    if (progressText) {
        progressText.textContent = `${percentage}%`;
    }
}

function toggleSpeaker(index) {
    parsedLines[index].speaker = parsedLines[index].speaker === '我' ? '对方' : '我';
    
    const lineEl = document.querySelector(`.chat-line[data-index="${index}"]`);
    if (lineEl) {
        lineEl.className = `chat-line ${parsedLines[index].speaker === '我' ? 'me' : 'other'}`;
        lineEl.querySelector('.speaker-indicator').textContent = parsedLines[index].speaker;
    }
    
    updateCounts();
    updateProgress();
}

function selectAll(speaker) {
    parsedLines.forEach(line => {
        line.speaker = speaker;
    });
    renderChatLines();
    updateCounts();
    updateProgress();
}

function alternateSelect() {
    parsedLines.forEach((line, index) => {
        line.speaker = index % 2 === 0 ? '对方' : '我';
    });
    renderChatLines();
    updateCounts();
    updateProgress();
}

function invertSelect() {
    parsedLines.forEach(line => {
        line.speaker = line.speaker === '我' ? '对方' : '我';
    });
    renderChatLines();
    updateCounts();
    updateProgress();
}

function backToInput() {
    document.getElementById('labelingSection').style.display = 'none';
    document.getElementById('inputSection').style.display = 'block';
    document.querySelector('[data-step="2"]').classList.remove('active');
    document.querySelector('[data-step="1"]').classList.add('active');
    currentStep = 1;
}

function goToDateSelection() {
    if (parsedLines.length === 0) {
        showToast('没有聊天记录', 'error');
        return;
    }
    
    document.getElementById('labelingSection').style.display = 'none';
    document.getElementById('dateSection').style.display = 'block';
    document.querySelector('[data-step="2"]').classList.remove('active');
    document.querySelector('[data-step="2"]').classList.add('completed');
    document.querySelector('[data-step="3"]').classList.add('active');
    
    updatePreview();
    currentStep = 3;
}

function updatePreview() {
    const otherCount = parsedLines.filter(l => l.speaker === '对方').length;
    const myCount = parsedLines.filter(l => l.speaker === '我').length;
    
    document.getElementById('previewTotal').textContent = parsedLines.length;
    document.getElementById('previewOther').textContent = otherCount;
    document.getElementById('previewMe').textContent = myCount;
}

function backToLabeling() {
    document.getElementById('dateSection').style.display = 'none';
    document.getElementById('labelingSection').style.display = 'block';
    document.querySelector('[data-step="3"]').classList.remove('active');
    document.querySelector('[data-step="2"]').classList.add('active');
    currentStep = 2;
}

async function submitChatLogs() {
    const dateStr = document.getElementById('chatDate').value;
    
    if (!dateStr) {
        showToast('请选择聊天日期', 'error');
        return;
    }
    
    const contactId = window.location.pathname.split('/').pop();
    
    const data = {
        lines: parsedLines.map(line => ({
            speaker: line.speaker,
            content: line.content
        })),
        date: dateStr
    };
    
    try {
        showToast('保存中...', 'info');
        
        const response = await fetch(`/api/contacts/${contactId}/chat-logs`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showToast('保存成功！', 'success');
            setTimeout(() => {
                window.location.href = `/profile/${contactId}`;
            }, 1500);
        } else {
            const error = await response.json();
            showToast(error.message || '保存失败', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('保存失败，请重试', 'error');
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
