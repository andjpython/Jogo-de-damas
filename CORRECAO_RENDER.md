# 🔧 Correção do Erro no Render

## ❌ Erro Atual

```
ModuleNotFoundError: Nenhum módulo chamado 'app'
Executando 'gunicorn app:app'
```

## ✅ Solução

O Render está tentando executar `gunicorn app:app`, mas o arquivo se chama `dama.py`, então deve ser `gunicorn dama:app`.

### Passo a Passo para Corrigir:

1. **Acesse o Dashboard do Render**
   - Vá em: https://dashboard.render.com
   - Clique no seu serviço `jogo-de-dama`

2. **Vá em "Settings" (Configurações)**

3. **Encontre "Start Command"**

4. **Altere de:**
   ```
   gunicorn app:app
   ```
   
   **Para:**
   ```
   gunicorn dama:app
   ```

5. **Salve as alterações**

6. **O Render vai fazer redeploy automaticamente**

7. **Aguarde o build completar**

## ✅ Verificação

Após o redeploy, verifique os logs:
- Deve aparecer: `Executando 'gunicorn dama:app'`
- Não deve mais aparecer o erro `ModuleNotFoundError`

## 📝 Nota

Os arquivos `Procfile` e `render.yaml` já estão corretos com `gunicorn dama:app`.
O problema é que o Render pode ter uma configuração manual no dashboard que está sobrescrevendo.

