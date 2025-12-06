// ========================================
// JOGO DE DAMA PROFISSIONAL - JAVASCRIPT
// ========================================

// VARIÁVEIS GLOBAIS
let gameState = null;
let selectedCell = null;
let validMoves = [];
let currentMode = 'pvp';
let selectedTheme = 'classic';
let timerInterval = null;
let timeLeft = 60;
let moveStartTime = null;
let isPlayerTurn = true;

const EMPTY = 0, P1 = 1, P2 = 2, P1_KING = 3, P2_KING = 4;

// ========================================
// FUNÇÕES DE NAVEGAÇÃO
// ========================================

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');
}

function showConfig(mode) {
    currentMode = mode;
    const player2Group = document.getElementById('player2Group');
    const player2Input = document.getElementById('player2Name');
    
    if (mode === 'pvc') {
        player2Input.value = 'Romano';
        player2Input.disabled = true;
        player2Group.querySelector('label').textContent = 'Adversário (CPU):';
    } else {
        player2Input.value = '';
        player2Input.disabled = false;
        player2Group.querySelector('label').textContent = 'Nome do Jogador 2 (Preto):';
    }
    
    showScreen('configScreen');
}

function selectTheme(theme) {
    selectedTheme = theme;
    document.querySelectorAll('.theme-option').forEach(opt => {
        opt.classList.remove('selected');
    });
    document.querySelector(`[data-theme="${theme}"]`).classList.add('selected');
}

async function startGame() {
    const p1Name = document.getElementById('player1Name').value.trim();
    const p2Name = document.getElementById('player2Name').value.trim();
    
    if (!p1Name || p1Name.length < 2) {
        alert('Por favor, digite um nome válido para o Jogador 1 (mínimo 2 caracteres)');
        return;
    }
    
    if (currentMode === 'pvp' && (!p2Name || p2Name.length < 2)) {
        alert('Por favor, digite um nome válido para o Jogador 2 (mínimo 2 caracteres)');
        return;
    }
    
    try {
        const response = await fetch('/configure', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player1_name: p1Name,
                player2_name: p2Name || 'Romano',
                mode: currentMode
            })
        });
        
        if (response.ok) {
            await fetchGameState();
            document.getElementById('board').className = `board theme-${selectedTheme}`;
            showScreen('gameScreen');
            startTimer();
        }
    } catch (error) {
        alert('Erro ao iniciar jogo: ' + error.message);
    }
}

// ========================================
// REGRAS
// ========================================

function showRules() {
    document.getElementById('rulesModal').classList.add('active');
}

function closeRules(understood) {
    if (!understood) {
        alert('Releia as regras com atenção! 📖');
        return;
    }
    document.getElementById('rulesModal').classList.remove('active');
}

// ========================================
// JOGO
// ========================================

async function fetchGameState() {
    try {
        const response = await fetch('/game-state');
        gameState = await response.json();
        renderBoard();
        updateScoreboard();
        checkAITurn();
        
        if (gameState.winner) {
            showWinner();
        }
    } catch (error) {
        showMessage('Erro ao carregar jogo: ' + error.message, 'error');
    }
}

function renderBoard() {
    const board = document.getElementById('board');
    board.innerHTML = '';
    
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const cell = document.createElement('div');
            cell.className = 'cell ' + ((row + col) % 2 === 0 ? 'light' : 'dark');
            cell.dataset.row = row;
            cell.dataset.col = col;
            cell.onclick = () => handleCellClick(row, col);
            
            const piece = gameState.board[row][col];
            if (piece !== EMPTY) {
                const pieceDiv = document.createElement('div');
                pieceDiv.className = 'piece';
                pieceDiv.draggable = true;
                
                if (piece === P1 || piece === P1_KING) {
                    pieceDiv.classList.add('p1');
                } else {
                    pieceDiv.classList.add('p2');
                }
                
                if (piece === P1_KING || piece === P2_KING) {
                    pieceDiv.classList.add('king');
                }
                
                // Drag and drop com eventos aprimorados
                pieceDiv.ondragstart = (e) => handleDragStart(e, row, col);
                pieceDiv.ondragend = (e) => handleDragEnd(e);
                cell.ondragover = (e) => e.preventDefault();
                cell.ondragenter = (e) => handleDragEnter(e, row, col);
                cell.ondragleave = (e) => handleDragLeave(e);
                cell.ondrop = (e) => handleDrop(e, row, col);
                
                cell.appendChild(pieceDiv);
            }
            
            board.appendChild(cell);
        }
    }
}

// ========================================
// DRAG & DROP
// ========================================

function handleDragStart(e, row, col) {
    if (!isPlayerTurn && currentMode === 'pvc') return;
    
    const piece = gameState.board[row][col];
    if (isPieceOfCurrentPlayer(piece)) {
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', `${row},${col}`);
        
        const pieceElement = e.target;
        pieceElement.classList.add('dragging');
        
        selectPiece(row, col);
    } else {
        e.preventDefault();
    }
}

function handleDragEnd(e) {
    e.target.classList.remove('dragging');
    document.querySelectorAll('.cell').forEach(cell => {
        cell.classList.remove('drag-over');
    });
}

function handleDragEnter(e, row, col) {
    e.preventDefault();
    if (isValidMove(row, col)) {
        e.currentTarget.classList.add('drag-over');
    }
}

function handleDragLeave(e) {
    e.currentTarget.classList.remove('drag-over');
}

function handleDrop(e, endRow, endCol) {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    
    const data = e.dataTransfer.getData('text/plain');
    const [startRow, startCol] = data.split(',').map(Number);
    
    if (isValidMove(endRow, endCol)) {
        animateMove(startRow, startCol, endRow, endCol, () => {
            makeMove(startRow, startCol, endRow, endCol);
        });
    } else {
        clearSelection();
    }
}

function animateMove(startRow, startCol, endRow, endCol, callback) {
    const startIndex = startRow * 8 + startCol;
    const endIndex = endRow * 8 + endCol;
    const cells = document.querySelectorAll('.cell');
    const piece = cells[startIndex].querySelector('.piece');
    
    if (piece) {
        const clone = piece.cloneNode(true);
        clone.style.position = 'fixed';
        clone.style.zIndex = '1000';
        clone.style.pointerEvents = 'none';
        
        const startRect = cells[startIndex].getBoundingClientRect();
        const endRect = cells[endIndex].getBoundingClientRect();
        
        clone.style.left = startRect.left + startRect.width * 0.075 + 'px';
        clone.style.top = startRect.top + startRect.height * 0.075 + 'px';
        clone.style.width = startRect.width * 0.85 + 'px';
        clone.style.height = startRect.height * 0.85 + 'px';
        
        document.body.appendChild(clone);
        
        setTimeout(() => {
            clone.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
            clone.style.left = endRect.left + endRect.width * 0.075 + 'px';
            clone.style.top = endRect.top + endRect.height * 0.075 + 'px';
            clone.style.transform = 'scale(1.1) rotate(360deg)';
            
            setTimeout(() => {
                clone.remove();
                callback();
            }, 400);
        }, 10);
    } else {
        callback();
    }
}

// ========================================
// CLIQUES
// ========================================

function handleCellClick(row, col) {
    if (!isPlayerTurn && currentMode === 'pvc') return;
    if (gameState.winner) return;
    
    const piece = gameState.board[row][col];
    
    if (isPieceOfCurrentPlayer(piece)) {
        selectPiece(row, col);
    } else if (selectedCell && isValidMove(row, col)) {
        makeMove(selectedCell.row, selectedCell.col, row, col);
    } else {
        clearSelection();
    }
}

function isPieceOfCurrentPlayer(piece) {
    if (gameState.turn === P1) {
        return piece === P1 || piece === P1_KING;
    } else {
        return piece === P2 || piece === P2_KING;
    }
}

function selectPiece(row, col) {
    clearSelection();
    selectedCell = { row, col };
    
    const cells = document.querySelectorAll('.cell');
    const index = row * 8 + col;
    cells[index].classList.add('selected');
    
    calculateValidMoves(row, col);
    
    validMoves.forEach(move => {
        const moveIndex = move.row * 8 + move.col;
        if (move.isCapture) {
            cells[moveIndex].classList.add('capture-move');
        } else {
            cells[moveIndex].classList.add('valid-move');
        }
    });
}

function calculateValidMoves(row, col) {
    validMoves = [];
    const piece = gameState.board[row][col];
    
    let directions = [];
    if (piece === P1) {
        directions = [[-1, -1], [-1, 1], [-2, -2], [-2, 2]];
    } else if (piece === P2) {
        directions = [[1, -1], [1, 1], [2, -2], [2, 2]];
    } else {
        directions = [[-1, -1], [-1, 1], [1, -1], [1, 1], 
                     [-2, -2], [-2, 2], [2, -2], [2, 2]];
    }
    
    let hasCaptures = false;
    let tempMoves = [];
    
    directions.forEach(([dr, dc]) => {
        const newRow = row + dr;
        const newCol = col + dc;
        
        if (newRow >= 0 && newRow < 8 && newCol >= 0 && newCol < 8) {
            if (gameState.board[newRow][newCol] === EMPTY) {
                if (Math.abs(dr) === 1) {
                    tempMoves.push({ row: newRow, col: newCol, isCapture: false });
                } else {
                    const midRow = row + dr / 2;
                    const midCol = col + dc / 2;
                    const midPiece = gameState.board[midRow][midCol];
                    if (midPiece !== EMPTY && !isPieceOfCurrentPlayer(midPiece)) {
                        tempMoves.push({ row: newRow, col: newCol, isCapture: true });
                        hasCaptures = true;
                    }
                }
            }
        }
    });
    
    if (hasCaptures) {
        validMoves = tempMoves.filter(m => m.isCapture);
        showMessage('⚠️ CAPTURA OBRIGATÓRIA! Clique no RAIO VERMELHO!', 'warning');
    } else {
        validMoves = tempMoves;
    }
}

function isValidMove(row, col) {
    return validMoves.some(move => move.row === row && move.col === col);
}

function clearSelection() {
    selectedCell = null;
    validMoves = [];
    document.querySelectorAll('.cell').forEach(cell => {
        cell.classList.remove('selected', 'valid-move', 'capture-move');
    });
}

// ========================================
// EFEITOS ESPECIAIS
// ========================================

function createCaptureEffect(row, col) {
    const cellIndex = row * 8 + col;
    const cells = document.querySelectorAll('.cell');
    const cell = cells[cellIndex];
    const rect = cell.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    for (let i = 0; i < 12; i++) {
        const particle = document.createElement('div');
        particle.className = 'capture-particle';
        
        const angle = (Math.PI * 2 * i) / 12;
        const velocity = 50 + Math.random() * 50;
        const tx = Math.cos(angle) * velocity;
        const ty = Math.sin(angle) * velocity;
        
        particle.style.left = centerX + 'px';
        particle.style.top = centerY + 'px';
        particle.style.background = i % 2 === 0 ? '#ff6b6b' : '#ffd700';
        particle.style.setProperty('--tx', tx + 'px');
        particle.style.setProperty('--ty', ty + 'px');
        
        document.body.appendChild(particle);
        setTimeout(() => particle.remove(), 800);
    }
}

function createPromoteEffect(row, col) {
    const cellIndex = row * 8 + col;
    const cells = document.querySelectorAll('.cell');
    const cell = cells[cellIndex];
    const rect = cell.getBoundingClientRect();
    
    const flash = document.createElement('div');
    flash.className = 'promote-flash';
    flash.style.left = (rect.left + rect.width / 2 - 50) + 'px';
    flash.style.top = (rect.top + rect.height / 2 - 50) + 'px';
    
    document.body.appendChild(flash);
    setTimeout(() => flash.remove(), 600);
}

// ========================================
// MOVIMENTOS
// ========================================

async function makeMove(startRow, startCol, endRow, endCol) {
    const moveTime = moveStartTime ? (60 - timeLeft) : 0;
    
    const isCapture = Math.abs(endRow - startRow) === 2;
    if (isCapture) {
        const midRow = (startRow + endRow) / 2;
        const midCol = (startCol + endCol) / 2;
        createCaptureEffect(midRow, midCol);
    }
    
    try {
        const response = await fetch('/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start_row: startRow,
                start_col: startCol,
                end_row: endRow,
                end_col: endCol,
                move_time: moveTime
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            const piece = gameState.board[startRow][startCol];
            const willPromote = (piece === P1 && endRow === 0) || (piece === P2 && endRow === 7);
            
            gameState = data.game_state;
            clearSelection();
            renderBoard();
            updateScoreboard();
            showMessage(data.message, 'success');
            
            if (willPromote) {
                setTimeout(() => createPromoteEffect(endRow, endCol), 100);
            }
            
            if (data.time_analysis && data.time_analysis.message) {
                setTimeout(() => {
                    showMessage(data.time_analysis.message, 'warning');
                }, 1000);
            }
            
            resetTimer();
            checkAITurn();
            
            if (gameState.winner) {
                showWinner();
            }
        } else {
            showMessage(data.message, 'error');
        }
    } catch (error) {
        showMessage('Erro ao fazer movimento: ' + error.message, 'error');
    }
}

// ========================================
// TIMER
// ========================================

function startTimer() {
    moveStartTime = Date.now();
    timeLeft = 60;
    updateTimerDisplay();
    
    if (timerInterval) clearInterval(timerInterval);
    
    timerInterval = setInterval(() => {
        timeLeft--;
        updateTimerDisplay();
        
        if (timeLeft <= 0) {
            handleTimeout();
        }
    }, 1000);
}

function resetTimer() {
    startTimer();
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

function updateTimerDisplay() {
    const timer1 = document.getElementById('timer1');
    const timer2 = document.getElementById('timer2');
    
    if (gameState.turn === P1) {
        timer1.textContent = formatTime(timeLeft);
        timer1.className = 'timer ' + getTimerClass(timeLeft);
        timer2.textContent = '--';
        timer2.className = 'timer time-ok';
    } else {
        timer2.textContent = formatTime(timeLeft);
        timer2.className = 'timer ' + getTimerClass(timeLeft);
        timer1.textContent = '--';
        timer1.className = 'timer time-ok';
    }
}

function formatTime(seconds) {
    return `${Math.floor(seconds / 60)}:${(seconds % 60).toString().padStart(2, '0')}`;
}

function getTimerClass(seconds) {
    if (seconds > 30) return 'time-ok';
    if (seconds > 10) return 'time-warning';
    return 'time-danger';
}

async function handleTimeout() {
    stopTimer();
    showMessage('⏰ Você demorou muito!! Esteja focado!!!!', 'error');
    
    try {
        const response = await fetch('/timeout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        gameState = data.game_state;
        renderBoard();
        updateScoreboard();
        resetTimer();
        checkAITurn();
    } catch (error) {
        console.error('Erro ao processar timeout:', error);
    }
}

// ========================================
// SCOREBOARD
// ========================================

function updateScoreboard() {
    document.getElementById('p1Name').textContent = gameState.player1_name;
    document.getElementById('p2Name').textContent = gameState.player2_name;
    document.getElementById('p1Pieces').textContent = gameState.p1_pieces;
    document.getElementById('p2Pieces').textContent = gameState.p2_pieces;
    document.getElementById('p1AvgTime').textContent = gameState.p1_avg_time + 's';
    document.getElementById('p2AvgTime').textContent = gameState.p2_avg_time + 's';
    
    const p1Card = document.getElementById('player1Card');
    const p2Card = document.getElementById('player2Card');
    
    if (gameState.turn === P1) {
        p1Card.classList.add('active');
        p2Card.classList.remove('active');
    } else {
        p2Card.classList.add('active');
        p1Card.classList.remove('active');
    }
}

// ========================================
// IA
// ========================================

async function checkAITurn() {
    if (currentMode === 'pvc' && gameState.turn === P2 && !gameState.winner) {
        isPlayerTurn = false;
        showMessage('🤖 Romano está pensando...', 'info');
        
        setTimeout(async () => {
            try {
                const response = await fetch('/ai-move', { method: 'POST' });
                const data = await response.json();
                
                if (data.status === 'success') {
                    gameState = data.game_state;
                    renderBoard();
                    updateScoreboard();
                    showMessage('🤖 Romano fez sua jogada!', 'success');
                    resetTimer();
                    isPlayerTurn = true;
                    
                    if (gameState.winner) {
                        showWinner();
                    }
                }
            } catch (error) {
                showMessage('Erro na jogada da IA: ' + error.message, 'error');
                isPlayerTurn = true;
            }
        }, 1500);
    } else {
        isPlayerTurn = true;
    }
}

// ========================================
// MENSAGENS
// ========================================

function showMessage(text, type = 'info') {
    const msgBox = document.getElementById('messageBox');
    msgBox.textContent = text;
    msgBox.className = `message-box msg-${type}`;
    
    if (type === 'success' || type === 'error') {
        setTimeout(() => {
            msgBox.className = 'message-box msg-info';
            msgBox.textContent = `Vez de ${gameState.turn_name}`;
        }, 3000);
    }
}

// ========================================
// CONTROLES
// ========================================

async function confirmSurrender() {
    if (!confirm('Tem certeza que deseja desistir? 🏳️')) return;
    
    stopTimer();
    
    try {
        const response = await fetch('/surrender', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        const loser = gameState.turn_name;
        showMessage(`💔 ${loser}: Você é um jogador fraco... Treine e volte novamente para resolver esta fatura!`, 'error');
        
        setTimeout(() => {
            gameState = data.game_state;
            showWinner();
        }, 2000);
    } catch (error) {
        console.error('Erro ao desistir:', error);
    }
}

function confirmReset() {
    if (!confirm('Reiniciar o jogo? 🔄')) return;
    playAgain();
}

function backToMenu() {
    stopTimer();
    document.getElementById('winnerModal').classList.remove('active');
    document.getElementById('rulesModal').classList.remove('active');
    fetch('/reset', { method: 'POST' })
        .then(() => {
            showScreen('menuScreen');
        })
        .catch(err => console.error('Erro ao voltar ao menu:', err));
}

async function playAgain() {
    try {
        const response = await fetch('/reset', { method: 'POST' });
        const data = await response.json();
        gameState = data.game_state;
        document.getElementById('winnerModal').classList.remove('active');
        renderBoard();
        updateScoreboard();
        resetTimer();
        showMessage('Novo jogo iniciado! Boa sorte! 🍀', 'success');
    } catch (error) {
        console.error('Erro ao reiniciar:', error);
    }
}

function showWinner() {
    stopTimer();
    const modal = document.getElementById('winnerModal');
    const winnerText = document.getElementById('winnerText');
    const winnerStats = document.getElementById('winnerStats');
    
    winnerText.textContent = `${gameState.winner} VENCEU!`;
    winnerStats.innerHTML = `
        <p>🏆 Parabéns pela vitória!</p>
        <p>📊 ${gameState.player1_name}: ${gameState.p1_pieces} peças | Tempo médio: ${gameState.p1_avg_time}s</p>
        <p>📊 ${gameState.player2_name}: ${gameState.p2_pieces} peças | Tempo médio: ${gameState.p2_avg_time}s</p>
    `;
    
    modal.classList.add('active');
}

// ========================================
// INICIALIZAÇÃO
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🎮 Jogo de Dama carregado e pronto!');
});

