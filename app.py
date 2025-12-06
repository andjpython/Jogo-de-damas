"""
========================================
APP.PY - WRAPPER PARA RENDER
Este arquivo permite que o Render encontre a aplicação
quando usar 'gunicorn app:app'
========================================
"""

# Importa tudo do dama.py
from dama import app

# Exporta a aplicação Flask
__all__ = ['app']

# Se executado diretamente, roda o servidor
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

