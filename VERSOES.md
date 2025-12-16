# 📋 CONTROLE DE VERSÕES - JOGO DE DAMAS

## 🐍 Python
- **Versão**: `3.11.9`
- **Motivo**: Python 3.11 é LTS (Long Term Support) e totalmente compatível com eventlet
- **Problema evitado**: Python 3.13+ tem incompatibilidades conhecidas com eventlet

### Arquivos de configuração:
- `runtime.txt`: `python-3.11.9` (Render/Heroku)
- `.python-version`: `3.11.9` (pyenv/asdf)
- `render.yaml`: `PYTHON_VERSION: 3.11.9`

## 📦 Dependências Python

### Core Flask
```
Flask==3.1.2          # Framework web
Werkzeug==3.1.4       # WSGI toolkit
Jinja2==3.1.6         # Template engine
```

### Servidor WSGI
```
gunicorn==22.0.0      # Production server
```

### WebSocket / Async
```
flask-socketio==5.5.1    # WebSocket support para Flask
python-socketio==5.15.0  # Socket.IO Python client/server
eventlet==0.40.4         # Async networking library
python-engineio          # Engine.IO (instalado automaticamente)
dnspython                # DNS toolkit (instalado automaticamente)
```

### Utilidades
```
click==8.3.1             # CLI creation
itsdangerous==2.2.0      # Cryptographic signing
MarkupSafe==3.0.3        # String escaping
blinker==1.9.0           # Signal/event system
```

**Nota**: python-engineio e dnspython são dependências transitivas e serão instaladas automaticamente nas versões compatíveis.

## ✅ Compatibilidade Testada

| Componente | Versão | Status | Notas |
|------------|--------|--------|-------|
| Python | 3.11.9 | ✅ | Totalmente compatível |
| Flask | 3.1.2 | ✅ | Versão estável |
| eventlet | 0.40.4 | ✅ | Funciona perfeitamente com Python 3.11 |
| gunicorn | 22.0.0 | ✅ | Última versão estável |
| flask-socketio | 5.5.1 | ✅ | Compatível com eventlet |

## ⚠️ Versões NÃO Compatíveis

### Python 3.13+
- ❌ **NÃO usar Python 3.13 ou superior**
- Causa: eventlet não é totalmente compatível
- Sintomas: Worker timeouts, crashes, "Exceção não tratada no loop principal"

### eventlet < 0.35
- ❌ Versões antigas têm bugs conhecidos
- Recomendado: 0.40.4 ou superior

## 🔄 Como Atualizar

### 1. Atualizar dependências:
```bash
pip install --upgrade -r requirements.txt
```

### 2. Verificar versão Python local:
```bash
python --version
# Deve mostrar: Python 3.11.9
```

### 3. Recriar ambiente virtual (se necessário):
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3.11 -m venv .venv
source .venv/bin/activate
```

### 4. Instalar dependências:
```bash
pip install -r requirements.txt
```

## 🚀 Deploy (Render)

O Render lerá automaticamente:
1. `runtime.txt` → define Python 3.11.9
2. `requirements.txt` → instala dependências
3. `Procfile` ou `render.yaml` → comando de inicialização

## 📝 Notas de Atualização

### Dezembro 2025
- ✅ Forçado Python 3.11.9 (resolver incompatibilidade com 3.13)
- ✅ Atualizado gunicorn para 22.0.0
- ✅ Adicionado python-engineio explicitamente
- ✅ Adicionado dnspython para resolver dependências do eventlet
- ✅ Organizado requirements.txt com comentários

### Próximas Atualizações
- Monitorar eventlet para suporte Python 3.13
- Considerar migração para gevent quando Python 3.13 for estável
- Atualizar Flask quando 3.2 for lançado (se compatível)

## 🔍 Troubleshooting

### Erro: "Worker timeout"
- **Causa**: Incompatibilidade Python 3.13
- **Solução**: Garantir uso de Python 3.11.9

### Erro: "Sessão inválida" Socket.IO
- **Causa**: Configuração incorreta de cookies/CORS
- **Solução**: Já corrigido em app.py (cookie=None, cors_credentials=False)

### Erro: "ModuleNotFoundError"
- **Causa**: Dependências não instaladas
- **Solução**: `pip install -r requirements.txt`

## 📚 Links Úteis

- [Python 3.11 Release](https://www.python.org/downloads/release/python-3119/)
- [Flask-SocketIO Docs](https://flask-socketio.readthedocs.io/)
- [Eventlet Docs](https://eventlet.readthedocs.io/)
- [Gunicorn Docs](https://docs.gunicorn.org/)

