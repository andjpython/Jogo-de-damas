# 🚀 Guia de Deploy no Render

## Passo a Passo Completo

### 1️⃣ Preparar o Código

✅ Todos os arquivos já estão prontos:
- `render.yaml` - Configuração do Render
- `Procfile` - Comando de inicialização
- `requirements.txt` - Dependências
- `runtime.txt` - Versão Python
- `dama.py` - Configurado para produção

### 2️⃣ Fazer Push para GitHub

```bash
# Certifique-se que está na pasta do projeto
cd "d:\AREA DO PROGRAMADOR\PYTHON NA MARRA\Meus_jogos"

# Adicionar todos os arquivos
git add .

# Commit
git commit -m "Preparado para deploy no Render"

# Push
git push origin main
```

### 3️⃣ Criar Conta no Render

1. Acesse: https://render.com
2. Clique em "Get Started for Free"
3. Faça login com GitHub (recomendado)

### 4️⃣ Conectar Repositório

1. No Dashboard do Render, clique em **"New +"**
2. Selecione **"Web Service"**
3. Conecte sua conta GitHub (se ainda não conectou)
4. Selecione o repositório: **`andjpython/Jogo-de-damas`**

### 5️⃣ Configurar o Serviço

**Configurações Básicas:**
- **Name**: `jogo-de-dama` (ou qualquer nome)
- **Region**: Escolha a mais próxima (ex: `Oregon (US West)`)
- **Branch**: `main`
- **Root Directory**: (deixe vazio)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn dama:app`

**Plan:**
- Escolha **Free** (gratuito, mas pode "dormir" após inatividade)
- Ou **Starter** ($7/mês) para sempre online

### 6️⃣ Variáveis de Ambiente (Opcional)

Clique em **"Advanced"** → **"Add Environment Variable"**:

- `PYTHON_VERSION` = `3.11.0`
- `FLASK_ENV` = `production`

### 7️⃣ Deploy

1. Clique em **"Create Web Service"**
2. Render começará o build automaticamente
3. Aguarde 3-5 minutos
4. Você verá os logs do build em tempo real

### 8️⃣ Acessar sua Aplicação

Após o deploy bem-sucedido:
- Render fornecerá uma URL como: `https://jogo-de-dama-xxxx.onrender.com`
- Clique na URL para acessar seu jogo!

## ✅ Verificação

Após o deploy, verifique:
- ✅ Site carrega corretamente
- ✅ Imagens das peças aparecem
- ✅ CSS e JavaScript funcionam
- ✅ Jogo inicia normalmente

## 🔧 Troubleshooting

### Erro: "Module not found"
- Verifique se `requirements.txt` tem todas as dependências
- Execute: `pip freeze > requirements.txt` localmente

### Erro: "Port already in use"
- O código já está configurado para usar `$PORT` do Render
- Não precisa alterar nada!

### Erro: "Static files not found"
- Certifique-se que a pasta `static/` está no repositório
- Verifique se fez `git add static/`

### Site "dorme" após inatividade
- Isso é normal no plano Free
- Primeira requisição pode demorar ~30 segundos
- Considere upgrade para plano pago se precisar

## 📊 Monitoramento

No Dashboard do Render você pode:
- Ver logs em tempo real
- Verificar status do serviço
- Ver métricas de uso
- Configurar auto-deploy

## 🎉 Pronto!

Seu jogo está online e acessível para todos!

**URL do seu jogo**: `https://jogo-de-dama-xxxx.onrender.com`

Compartilhe com seus amigos! 🎮





