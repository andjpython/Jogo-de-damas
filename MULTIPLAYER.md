# 🌐 SISTEMA MULTIPLAYER - JOGO DE DAMAS ONLINE

## 📋 Visão Geral

O jogo de damas agora suporta **multiplayer online em tempo real**, permitindo que jogadores de diferentes dispositivos (computador, celular, tablet) joguem juntos!

## ✨ Funcionalidades

### 🎮 Modos de Jogo
1. **Local (PvP)**: Dois jogadores no mesmo dispositivo
2. **vs CPU**: Jogador contra IA "Romano"
3. **🌐 Online (Multiplayer)**: Jogadores em dispositivos diferentes

### 🌐 Sistema Multiplayer

#### Criar Sala
- Jogador cria uma sala e recebe um código único (6 caracteres)
- Compartilha o código com o adversário
- Aguarda o adversário entrar

#### Entrar em Sala
- Jogador digita o código da sala
- Conecta-se ao jogo em andamento
- Jogo sincroniza automaticamente

#### Lista de Salas
- Visualiza salas disponíveis
- Entra diretamente em salas públicas

## 🔧 Tecnologias Utilizadas

- **Flask-SocketIO**: Comunicação em tempo real via WebSockets
- **Eventlet**: Servidor assíncrono para suportar múltiplas conexões
- **Socket.IO (JavaScript)**: Cliente WebSocket no navegador

## 📁 Estrutura de Arquivos

```
Meus_jogos/
├── app.py                 # Backend Flask + WebSocket handlers
├── game_manager.py        # Gerenciador de salas multiplayer
├── static/
│   ├── js/
│   │   ├── game.js        # Lógica do jogo (local)
│   │   └── multiplayer.js # Lógica multiplayer (online)
│   └── css/
│       └── style.css      # Estilos (inclui multiplayer)
└── templates/
    └── index.html         # Interface (inclui tela multiplayer)
```

## 🚀 Como Usar

### Para Jogadores

1. **Acesse o jogo** no navegador (mesmo IP/URL)
2. **Clique em "🌐 Jogar Online (Multiplayer)"**
3. **Digite seu nome**
4. **Escolha:**
   - **Criar Sala**: Cria uma nova sala e recebe código
   - **Entrar em Sala**: Digite o código para entrar
   - **Atualizar Lista**: Veja salas disponíveis

### Para Desenvolvedores

#### Instalação
```bash
pip install -r requirements.txt
```

#### Executar Localmente
```bash
python app.py
```

O servidor iniciará na porta 5000 (ou PORT do ambiente).

#### Deploy no Render
O `Procfile` já está configurado para usar eventlet com gunicorn:
```
web: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app
```

## 🔌 Eventos WebSocket

### Cliente → Servidor
- `create_room`: Cria uma nova sala
- `join_room`: Entra em uma sala existente
- `get_rooms`: Solicita lista de salas
- `make_move`: Faz um movimento
- `surrender`: Desiste do jogo

### Servidor → Cliente
- `connected`: Confirma conexão
- `room_created`: Sala criada com sucesso
- `room_joined`: Entrou na sala
- `game_state`: Estado atual do jogo
- `game_started`: Jogo iniciado
- `move_result`: Resultado do movimento
- `game_over`: Jogo terminado
- `move_error`: Erro no movimento
- `join_error`: Erro ao entrar na sala
- `host_left`: Host saiu da sala
- `guest_left`: Adversário saiu

## 🎯 Fluxo de Jogo Multiplayer

1. **Jogador 1 cria sala** → Recebe código (ex: "ABC123")
2. **Jogador 2 entra com código** → Conecta-se à sala
3. **Jogo inicia automaticamente** → Ambos veem o tabuleiro
4. **Jogador 1 (P1) joga** → Movimento sincronizado
5. **Jogador 2 (P2) joga** → Movimento sincronizado
6. **Continua até vitória** → Vencedor anunciado para ambos

## 🔒 Segurança

- Cada sala tem ID único (6 caracteres aleatórios)
- Validação de turno no servidor
- Limpeza automática de salas vazias (1 hora)
- Desconexão automática ao sair

## 📱 Compatibilidade

- ✅ Desktop (Chrome, Firefox, Edge, Safari)
- ✅ Mobile (iOS Safari, Chrome Mobile)
- ✅ Tablet (iPad, Android)
- ✅ Qualquer dispositivo com navegador moderno

## 🐛 Troubleshooting

### "Não conectado ao servidor"
- Verifique se o servidor está rodando
- Verifique a URL/IP
- Verifique firewall/proxy

### "Sala não encontrada"
- Verifique se o código está correto (6 caracteres)
- Verifique se a sala ainda existe
- Tente criar uma nova sala

### Movimentos não sincronizam
- Verifique conexão de internet
- Recarregue a página
- Tente reconectar

## 🎉 Melhorias Futuras

- [ ] Sistema de ranking
- [ ] Chat em tempo real
- [ ] Salas privadas com senha
- [ ] Histórico de partidas
- [ ] Estatísticas de jogadores
- [ ] Torneios

---

**Desenvolvido com ❤️ para jogadores de damas!**


