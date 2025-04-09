// 初始化Socket.IO连接
const socket = io();

// DOM元素
const settingsForm = document.getElementById('settingsForm');
const hardMode = document.getElementById('hardMode');
const sendEmail = document.getElementById('sendEmail');
const emailContainer = document.getElementById('emailContainer');
const outputEl = document.getElementById('output');
const statusDisplay = document.getElementById('statusDisplay');
const progressBar = document.getElementById('progressBar');
const clearOutputBtn = document.getElementById('clearOutput');
const runButton = document.getElementById('runButton');
const addEmailBtn = document.getElementById('addEmailBtn');

// 邮箱输入相关变量
let visibleEmailCount = 1;
const MAX_EMAILS = 3;

// 系统状态
let isRunning = false;
let taskProgress = 0;

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 绑定添加邮箱按钮事件
    addEmailBtn.addEventListener('click', addEmailField);
    
    // 绑定删除邮箱按钮事件（使用事件委托）
    emailContainer.addEventListener('click', handleRemoveEmail);
    
    // 绑定表单提交事件
    settingsForm.addEventListener('submit', handleFormSubmit);
    
    // 绑定清空按钮事件
    clearOutputBtn.addEventListener('click', clearOutput);
    
    // 初始化状态查询
    checkStatus();
    
    // 定期查询状态
    setInterval(checkStatus, 5000);
});

// 添加邮箱输入框
function addEmailField() {
    // 最多显示3个邮箱输入框
    if (visibleEmailCount >= MAX_EMAILS) return;
    
    // 显示下一个邮箱输入框
    visibleEmailCount++;
    const nextEmailRow = document.getElementById(`email-row-${visibleEmailCount}`);
    nextEmailRow.classList.remove('d-none');
    
    // 如果只有一个输入框，显示它的删除按钮
    if (visibleEmailCount === 2) {
        const firstRowBtn = document.querySelector('#email-row-1 .remove-email');
        firstRowBtn.classList.remove('d-none');
    }
    
    // 当达到最大输入框数量时，禁用添加按钮
    if (visibleEmailCount >= MAX_EMAILS) {
        addEmailBtn.disabled = true;
    }
    
    // 将焦点设置到新显示的输入框
    const newInput = nextEmailRow.querySelector('.email-input');
    setTimeout(() => newInput.focus(), 100);
}

// 处理删除邮箱操作
function handleRemoveEmail(e) {
    // 检查是否点击了删除按钮
    if (!e.target.closest('.remove-email')) return;
    
    const button = e.target.closest('.remove-email');
    const rowId = button.getAttribute('data-row');
    const rowElement = document.getElementById(`email-row-${rowId}`);
    
    // 如果是最后一个可见的行，直接隐藏它
    if (rowId == visibleEmailCount) {
        rowElement.querySelector('.email-input').value = '';
        rowElement.classList.add('d-none');
        visibleEmailCount--;
    } 
    // 如果不是最后一个，需要移动下面的行到当前位置
    else {
        // 将后面的每一行的值移到前一行
        for (let i = parseInt(rowId); i < visibleEmailCount; i++) {
            const currentRow = document.getElementById(`email-row-${i}`);
            const nextRow = document.getElementById(`email-row-${i+1}`);
            
            currentRow.querySelector('.email-input').value = 
                nextRow.querySelector('.email-input').value;
        }
        
        // 隐藏最后一行
        const lastRow = document.getElementById(`email-row-${visibleEmailCount}`);
        lastRow.querySelector('.email-input').value = '';
        lastRow.classList.add('d-none');
        visibleEmailCount--;
    }
    
    // 如果只剩一个输入框，隐藏其删除按钮
    if (visibleEmailCount === 1) {
        document.querySelector('#email-row-1 .remove-email').classList.add('d-none');
    }
    
    // 重新启用添加按钮
    addEmailBtn.disabled = false;
}

// 获取所有有效的邮箱地址
function getEmails() {
    const emails = [];
    
    // 只处理可见的邮箱输入框
    for (let i = 1; i <= visibleEmailCount; i++) {
        const row = document.getElementById(`email-row-${i}`);
        const input = row.querySelector('.email-input');
        const value = input.value.trim();
        
        if (value && isValidEmail(value)) {
            emails.push(value);
        }
    }
    
    return emails;
}

// 验证邮箱格式
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// 表单提交处理
function handleFormSubmit(e) {
    e.preventDefault();
    
    if (isRunning) {
        addOutput('[系统] 任务正在运行中，请等待完成...');
        return;
    }
    
    const emails = getEmails();
    
    // 准备参数
    const params = {
        hard: hardMode.checked,
        send: sendEmail.checked,
        emails: emails
    };
    
    // 禁用表单
    setRunningState(true);
    
    // 清空输出
    clearOutput();
    
    // 添加启动信息
    addOutput('[系统] 正在启动任务...');
    addOutput(`[系统] 参数：硬编码模式=${params.hard}, 发送邮件=${params.send}, 收件人=${emails.join(', ') || '使用.env配置'}`);
    
    // 发送请求
    fetch('/api/run', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            addOutput(`[系统] 启动失败: ${data.message}`, 'error');
            setRunningState(false);
        } else {
            addOutput('[系统] 任务已成功启动', 'success');
        }
    })
    .catch(error => {
        addOutput(`[系统] 启动出错: ${error}`, 'error');
        setRunningState(false);
    });
}

// 设置运行状态
function setRunningState(running) {
    isRunning = running;
    
    if (running) {
        runButton.disabled = true;
        statusDisplay.textContent = '运行中';
        statusDisplay.className = 'running';
        updateProgress(10); // 初始进度
    } else {
        runButton.disabled = false;
        statusDisplay.textContent = '就绪';
        statusDisplay.className = 'idle';
        updateProgress(0);
    }
}

// 更新进度条
function updateProgress(value) {
    taskProgress = value;
    progressBar.style.width = `${value}%`;
    progressBar.textContent = `${value}%`;
}

// 检查任务状态
function checkStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'running') {
                setRunningState(true);
                // 模拟进度
                if (taskProgress < 90) {
                    updateProgress(taskProgress + 5);
                }
            } else if (data.status === 'completed') {
                setRunningState(false);
                statusDisplay.textContent = '完成';
                statusDisplay.className = 'completed';
                updateProgress(100);
            } else {
                setRunningState(false);
            }
        })
        .catch(() => {
            // 忽略错误
        });
}

// 添加输出内容
function addOutput(text, type = '') {
    const now = new Date();
    const timestamp = now.toTimeString().split(' ')[0];
    
    // 如果不是系统消息，添加时间戳
    if (!text.startsWith('[系统]')) {
        text = text.replace(/^\[(\d{2}:\d{2}:\d{2})\]/, ''); // 移除可能已有的时间戳
        text = `[${timestamp}]${text}`;
    }
    
    const div = document.createElement('div');
    div.className = type ? `output ${type}` : 'output';
    div.textContent = text;
    
    outputEl.appendChild(div);
    
    // 滚动到底部
    const terminal = document.getElementById('terminal');
    terminal.scrollTop = terminal.scrollHeight;
}

// 清空输出
function clearOutput() {
    outputEl.innerHTML = '';
    addOutput('[系统] 输出已清空');
}

// Socket.IO消息处理
socket.on('output', function(data) {
    addOutput(data.data);
    
    // 如果包含完成标记，设置状态为完成
    if (data.data.includes('新闻聚合流程完成') || data.data.includes('处理完成: 发送邮件')) {
        setRunningState(false);
        statusDisplay.textContent = '完成';
        statusDisplay.className = 'completed';
        updateProgress(100);
    }
});
    