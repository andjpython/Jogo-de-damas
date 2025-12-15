// ========================================
// MULTIPLAYER - JOGO ONLINE
// ========================================

let socket = null;
let currentRoomId = null;
let isPlayer1 = false;
let playerName = '';
let isMultiplayerMode = false;

// ========================================
// INICIALIZAÇÃO
// ========================================

function initSocket() {
    if (socket) {
        socket.disconnect();
    }
    
    socket = io();
    
    socket.on('connect', () => {
        console.log('✅ Conectado ao servidor multiplayer!', socket.id);
        showMessage('✅ Conectado ao servidor!', 'success');
        
        // Reabilitar botão se estava desabilitado
        const btn = document.getElementById('createRoomBtn') || document.querySelector('button[onclick*="createMultiplayerRoom"]');
        if (btn && btn.disabled) {
            btn.disabled = false;
            btn.textContent = '➕ Criar Sala';
        }
    });
    
    socket.on('disconnect', () => {
        console.log('❌ Desconectado do servidor');
        showMessage('❌ Desconectado do servidor', 'error');
        
        // Reabilitar botão
        const btn = document.getElementById('createRoomBtn') || document.querySelector('button[onclick*="createMultiplayerRoom"]');
        if (btn) {
            btn.disabled = false;
            btn.textContent = '➕ Criar Sala';
        }
    });
    
    socket.on('connect_error', (error) => {
        console.error('❌ Erro de conexão:', error);
        showMessage('❌ Erro ao conectar ao servidor. Tente novamente.', 'error');
        
        // Reabilitar botão
        const btn = document.getElementById('createRoomBtn') || document.querySelector('button[onclick*="createMultiplayerRoom"]');
        if (btn) {
            btn.disabled = false;
            btn.textContent = '➕ Criar Sala';
        }
    });
    
    socket.on('connected', (data) => {
        console.log('Servidor:', data.message);
    });
    
    socket.on('room_created', (data) => {
        currentRoomId = data.room_id;
        document.getElementById('roomIdDisplay').textContent = currentRoomId;
        document.getElementById('shareRoomId').textContent = currentRoomId;
        document.getElementById('roomInfo').style.display = 'block';
        document.getElementById('roomsList').style.display = 'none';
        showMessage(`✅ Sala ${currentRoomId} criada! Aguardando adversário...`, 'success');
        
        // Reabilitar botão após criar sala
        const btn = document.getElementById('createRoomBtn') || document.querySelector('button[onclick*="createMultiplayerRoom"]');
        if (btn) {
            btn.disabled = false;
            btn.textContent = '➕ Criar Sala';
        }
    });
    
    socket.on('game_state', (data) => {
        if (isMultiplayerMode) {
            gameState = data;
            renderBoard();
            updateScoreboard();
        }
    });
    
    socket.on('room_joined', (data) => {
        currentRoomId = data.room_id;
        isPlayer1 = data.is_player1;
        isMultiplayerMode = true;
        
        showMessage(`✅ Entrou na sala ${currentRoomId}!`, 'success');
        showScreen('gameScreen');
        startTimer();
        
        // Atualizar interface para mostrar que é multiplayer
        document.querySelector('.game-header').innerHTML += 
            `<div class="multiplayer-badge">🌐 Online - Sala: ${currentRoomId}</div>`;
    });
    
    socket.on('game_started', (data) => {
        showMessage('🎮 Jogo iniciado!', 'success');
        fetchGameState();
    });
    
    socket.on('move_result', (data) => {
        if (data.status === 'success') {
            gameState = data.game_state;
            clearSelection();
            renderBoard();
            updateScoreboard();
            showMessage(data.message, 'success');
            
            // Efeito de captura se houver
            if (data.captured_pos) {
                createCaptureEffect(data.captured_pos.row, data.captured_pos.col);
            }
            
            // Verificar promoção
            const piece = gameState.board[data.start_row]?.[data.start_col];
            if (piece) {
                const willPromote = (piece === P1 && data.end_row === 0) || 
                                   (piece === P2 && data.end_row === 7);
                if (willPromote) {
                    setTimeout(() => createPromoteEffect(data.end_row, data.end_col), 100);
                }
            }
            
            resetTimer();
            
            if (data.time_analysis && data.time_analysis.message) {
                setTimeout(() => {
                    showMessage(data.time_analysis.message, 'warning');
                }, 1000);
            }
            
            if (gameState.winner) {
                showWinner();
            }
        }
    });
    
    socket.on('move_error', (data) => {
        showMessage(data.message, 'error');
    });
    
    socket.on('game_over', (data) => {
        gameState = data.game_state;
        renderBoard();
        updateScoreboard();
        showWinner();
    });
    
    socket.on('join_error', (data) => {
        showMessage(data.message, 'error');
    });
    
    socket.on('create_room_error', (data) => {
        showMessage(data.message, 'error');
        // Reabilitar botão em caso de erro
        const btn = document.getElementById('createRoomBtn') || document.querySelector('button[onclick*="createMultiplayerRoom"]');
        if (btn) {
            btn.disabled = false;
            btn.textContent = '➕ Criar Sala';
        }
    });
    
    socket.on('host_left', (data) => {
        showMessage('❌ O host saiu da sala. Voltando ao menu...', 'error');
        setTimeout(() => {
            backToMenu();
        }, 2000);
    });
    
    socket.on('guest_left', (data) => {
        showMessage('⚠️ O adversário saiu da sala.', 'warning');
    });
    
    socket.on('rooms_list', (data) => {
        displayRoomsList(data.rooms);
    });
}

// ========================================
// INTERFACE MULTIPLAYER
// ========================================

function showMultiplayerMenu() {
    showScreen('multiplayerScreen');
    document.getElementById('roomInfo').style.display = 'none';
    document.getElementById('roomsList').style.display = 'none';
    
    // Inicializar socket se ainda não foi inicializado
    if (!socket) {
        initSocket();
    } else if (!socket.connected) {
        socket.connect();
    }
    
    // Garantir que o botão está habilitado
    const btn = document.getElementById('createRoomBtn');
    if (btn) {
        btn.disabled = false;
        btn.textContent = '➕ Criar Sala';
    }
}

async function ensureSocketConnected(timeoutMs = 4000) {
    return new Promise((resolve, reject) => {
        if (!socket) {
            initSocket();
        }

        // Já conectado
        if (socket && socket.connected) {
            return resolve();
        }

        let resolved = false;

        const onConnect = () => {
            if (!resolved) {
                resolved = true;
                cleanup();
                resolve();
            }
        };

        const onError = (err) => {
            if (!resolved) {
                resolved = true;
                cleanup();
                reject(err || new Error('Falha ao conectar'));
            }
        };

        const cleanup = () => {
            socket.off('connect', onConnect);
            socket.off('connect_error', onError);
        };

        socket.on('connect', onConnect);
        socket.on('connect_error', onError);
        socket.connect();

        setTimeout(() => {
            if (!resolved) {
                resolved = true;
                cleanup();
                reject(new Error('Tempo de conexão esgotado'));
            }
        }, timeoutMs);
    });
}

async function createMultiplayerRoom() {
    const btn = event?.target || document.getElementById('createRoomBtn') || document.querySelector('button[onclick*="createMultiplayerRoom"]');
    
    // Prevenir múltiplos cliques
    if (btn && btn.disabled) {
        return;
    }
    
    playerName = document.getElementById('multiplayerName').value.trim();
    
    if (!playerName || playerName.length < 2) {
        alert('Por favor, digite um nome válido (mínimo 2 caracteres)');
        return;
    }
    
    // Desabilitar botão enquanto processa
    if (btn) {
        btn.disabled = true;
        btn.textContent = '⏳ Criando...';
    }
    
    try {
        await ensureSocketConnected(5000);
        socket.emit('create_room', { player_name: playerName });
    } catch (error) {
        console.error('Erro ao conectar para criar sala:', error);
        alert('Erro: Não foi possível conectar ao servidor. Tente novamente.');
        if (btn) {
            btn.disabled = false;
            btn.textContent = '➕ Criar Sala';
        }
    }
}

function showJoinRoom() {
    const roomId = prompt('Digite o código da sala (6 caracteres):');
    
    if (!roomId || roomId.length !== 6) {
        alert('Código da sala inválido! Deve ter 6 caracteres.');
        return;
    }
    
    playerName = document.getElementById('multiplayerName').value.trim();
    
    if (!playerName || playerName.length < 2) {
        alert('Por favor, digite um nome válido (mínimo 2 caracteres)');
        return;
    }
    
    ensureSocketConnected(5000)
        .then(() => {
            socket.emit('join_room', {
                room_id: roomId.toUpperCase(),
                player_name: playerName
            });
        })
        .catch(() => {
            alert('Erro: Não foi possível conectar ao servidor. Tente novamente.');
        });
}

function refreshRoomsList() {
    ensureSocketConnected(5000)
        .then(() => {
            socket.emit('get_rooms');
            document.getElementById('roomsList').style.display = 'block';
        })
        .catch(() => {
            alert('Erro: Não foi possível conectar ao servidor.');
        });
}

function displayRoomsList(rooms) {
    const container = document.getElementById('roomsContainer');
    
    if (rooms.length === 0) {
        container.innerHTML = '<p>Nenhuma sala disponível no momento.</p>';
        return;
    }
    
    container.innerHTML = rooms.map(room => `
        <div class="room-item">
            <div class="room-info-item">
                <strong>Sala: ${room.room_id}</strong>
                <span>Host: ${room.host_name}</span>
            </div>
            <button class="btn btn-primary" onclick="joinRoomById('${room.room_id}')">
                Entrar
            </button>
        </div>
    `).join('');
}

function joinRoomById(roomId) {
    playerName = document.getElementById('multiplayerName').value.trim();
    
    if (!playerName || playerName.length < 2) {
        alert('Por favor, digite um nome válido (mínimo 2 caracteres)');
        return;
    }
    
    ensureSocketConnected(5000)
        .then(() => {
            socket.emit('join_room', {
                room_id: roomId,
                player_name: playerName
            });
        })
        .catch(() => {
            alert('Erro: Não foi possível conectar ao servidor. Tente novamente.');
        });
}

// ========================================
// MOVIMENTOS MULTIPLAYER
// ========================================

function makeMultiplayerMove(startRow, startCol, endRow, endCol) {
    if (!socket || !socket.connected) {
        showMessage('Erro: Não conectado ao servidor!', 'error');
        return;
    }
    
    if (!currentRoomId) {
        showMessage('Erro: Você não está em uma sala!', 'error');
        return;
    }
    
    // Verificar se é a vez do jogador
    const currentTurn = gameState.turn;
    const myTurn = (isPlayer1 && currentTurn === P1) || (!isPlayer1 && currentTurn === P2);
    
    if (!myTurn) {
        showMessage('⏳ Aguarde sua vez!', 'warning');
        return;
    }
    
    const moveTime = moveStartTime ? (60 - timeLeft) : 0;
    
    ensureSocketConnected(5000)
        .then(() => {
            socket.emit('make_move', {
                start_row: startRow,
                start_col: startCol,
                end_row: endRow,
                end_col: endCol,
                move_time: moveTime
            });
        })
        .catch(() => {
            showMessage('Erro: Não foi possível conectar ao servidor!', 'error');
        });
}

// ========================================
// SOBRESCREVER FUNÇÃO DE MOVIMENTO
// ========================================

// Salvar função original
const originalMakeMove = window.makeMove;

// Sobrescrever makeMove para usar multiplayer quando necessário
// Aguardar até que game.js seja carregado
setTimeout(() => {
    if (typeof makeMove !== 'undefined') {
        const originalMakeMove = window.makeMove;
        window.makeMove = function(startRow, startCol, endRow, endCol) {
            if (isMultiplayerMode) {
                makeMultiplayerMove(startRow, startCol, endRow, endCol);
            } else {
                // Usar função original para modo local
                if (originalMakeMove) {
                    originalMakeMove(startRow, startCol, endRow, endCol);
                }
            }
        };
    }
}, 100);

// ========================================
// DESISTIR MULTIPLAYER
// ========================================

function surrenderMultiplayer() {
    if (!socket || !socket.connected || !currentRoomId) {
        return;
    }
    
    if (confirm('Tem certeza que deseja desistir? 🏳️')) {
        socket.emit('surrender');
    }
}

// Sobrescrever função de desistir (se existir)
if (typeof confirmSurrender !== 'undefined') {
    const originalConfirmSurrender = window.confirmSurrender;
    window.confirmSurrender = function() {
        if (isMultiplayerMode) {
            surrenderMultiplayer();
        } else {
            if (originalConfirmSurrender) {
                originalConfirmSurrender();
            }
        }
    };
}

// ========================================
// LIMPEZA AO SAIR
// ========================================

function cleanupMultiplayer() {
    if (socket) {
        socket.disconnect();
        socket = null;
    }
    currentRoomId = null;
    isPlayer1 = false;
    isMultiplayerMode = false;
    playerName = '';
}

// Sobrescrever backToMenu para limpar multiplayer
const originalBackToMenu = window.backToMenu;
window.backToMenu = function() {
    cleanupMultiplayer();
    if (originalBackToMenu) {
        originalBackToMenu();
    } else {
        showScreen('menuScreen');
    }
};

// ========================================
// INICIALIZAÇÃO AUTOMÁTICA
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🌐 Módulo Multiplayer carregado!');
});

