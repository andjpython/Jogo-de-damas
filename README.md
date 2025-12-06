# 🎯 Jogo de Dama Profissional

Um jogo de dama completo e interativo desenvolvido com Python Flask, HTML5, CSS3 e JavaScript.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

## 📋 Índice

- [Sobre](#sobre)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Screenshots](#screenshots)
- [Autor](#autor)

## 🎮 Sobre

Jogo de dama profissional com interface moderna, animações suaves e recursos avançados como:
- Modo Jogador vs Jogador
- Modo Jogador vs CPU (IA Romano)
- Sistema de timer com análise comparativa
- Efeitos visuais espetaculares
- Design responsivo (PC, Tablet, Mobile)

## ✨ Funcionalidades

### 🎯 Modos de Jogo
- **👥 Jogador vs Jogador**: Jogue localmente contra um amigo
- **🤖 Jogador vs Romano**: Enfrente a IA inteligente

### 🎨 Visual e Interatividade
- ✅ **Peças com imagens reais** em alta qualidade
- ✅ **Drag & Drop** suave e responsivo
- ✅ **4 temas de tabuleiro**: Clássico, Madeira, Moderno, Neon
- ✅ **Animações CSS avançadas**: Hover effects, movimentos, capturas
- ✅ **Efeitos especiais**: Partículas de explosão, flash de promoção
- ✅ **Damas brilhantes** com coroa dourada pulsante

### ⏱️ Sistema de Timer
- ✅ **60 segundos por jogada**
- ✅ **Timer visual** com cores (verde/amarelo/vermelho)
- ✅ **Análise comparativa de tempo** entre jogadores
- ✅ **Penalidades automáticas** para jogadores lentos
- ✅ **Timeout automático** com mensagens

### 🎯 Regras Completas
- ✅ **Capturas obrigatórias** com destaque visual (raio ⚡)
- ✅ **Capturas múltiplas** em sequência
- ✅ **Promoção a Dama** com efeito especial
- ✅ **Validação completa** de movimentos
- ✅ **Detecção de vitória** automática

### 📊 Estatísticas
- ✅ **Contagem de peças** em tempo real
- ✅ **Tempo médio** de jogadas
- ✅ **Histórico de movimentos**
- ✅ **Placar visual** animado

## 🛠️ Tecnologias

### Backend
- **Python 3.9+**
- **Flask 3.0+** - Framework web
- **Random** - IA básica

### Frontend
- **HTML5** - Estrutura semântica
- **CSS3** - Animações e responsividade
- **JavaScript ES6+** - Lógica do cliente
- **Fetch API** - Comunicação com backend

### Assets
- **Imagens JPG** - Peças customizadas
- **Fontes Web** - Segoe UI

## 📁 Estrutura do Projeto

```
Meus_jogos/
├── dama.py                    # Backend Flask (API REST)
├── .gitignore                 # Arquivos ignorados pelo Git
├── README.md                  # Documentação
├── requirements.txt           # Dependências Python
├── templates/
│   └── index.html            # Interface HTML
└── static/
    ├── css/
    │   └── style.css         # Estilos CSS
    ├── js/
    │   └── game.js           # Lógica JavaScript
    └── imagens/
        ├── peça_black_dama.jpg
        ├── peças_red_dama.jpg
        └── tabuleiro.png
```

## 🚀 Instalação

### Pré-requisitos
- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone o repositório**
```bash
git clone https://github.com/andjpython/Jogo-de-damas.git
cd Jogo-de-damas
```

2. **Crie um ambiente virtual** (recomendado)
```bash
python -m venv .venv
```

3. **Ative o ambiente virtual**
- Windows:
```bash
.venv\Scripts\activate
```
- Linux/Mac:
```bash
source .venv/bin/activate
```

4. **Instale as dependências**
```bash
pip install -r requirements.txt
```

5. **Execute o servidor**
```bash
python dama.py
```

6. **Acesse no navegador**
```
http://localhost:5000
```

## 🎮 Como Usar

### Iniciar Jogo

1. **Escolha o modo**:
   - 👥 Jogar vs Jogador
   - 🤖 Jogar vs Romano (CPU)

2. **Configure**:
   - Digite os nomes dos jogadores
   - Escolha o tema do tabuleiro (4 opções)
   - Clique em "🚀 Iniciar Partida"

3. **Jogue**:
   - Clique ou arraste as peças
   - Siga os indicadores visuais:
     - 🟢 Círculo verde = movimento normal
     - ⚡ Raio vermelho = captura obrigatória
   - Observe o timer (60 segundos)

### Controles do Jogo

- **🏳️ Desistir**: Abandona a partida
- **🔄 Reiniciar**: Recomeça o jogo
- **📋 Menu**: Volta ao menu principal
- **📖 Como Jogar**: Exibe as regras

## 📸 Screenshots

### Menu Principal
- Interface moderna com gradiente
- Botões intuitivos e responsivos

### Tela de Jogo
- Tabuleiro 8x8 com peças reais
- Placar com estatísticas ao vivo
- Timer visual colorido

### Efeitos Especiais
- Explosão de partículas ao capturar
- Flash dourado ao promover Dama
- Animações suaves de movimento

## 📊 Estatísticas do Projeto

- **Linhas de código**: ~1.960
- **Arquivos**: 8 principais
- **Animações CSS**: 12 tipos
- **Funcionalidades**: 25+
- **Tempo de desenvolvimento**: Profissional

## 🎯 Recursos Avançados

### IA Romano
- Prioriza capturas
- Tenta promover peças
- Movimentos estratégicos
- Delay de "pensamento"

### Sistema de Penalidades
- Análise de tempo médio
- Avisos progressivos
- Penalidade: perda de peça aleatória

### Responsividade
- Breakpoints: Desktop, Tablet, Mobile
- Touch events para dispositivos móveis
- Interface adaptável

## 🐛 Bugs Conhecidos

Nenhum bug conhecido no momento! 🎉

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

**Anderson**
- GitHub: [@andjpython](https://github.com/andjpython)
- Projeto: [Jogo de Dama](https://github.com/andjpython/Jogo-de-damas)

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
1. Fork o projeto
2. Criar uma branch (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abrir um Pull Request

## 🎓 Aprendizados

Este projeto demonstra:
- ✅ Arquitetura MVC
- ✅ API REST com Flask
- ✅ Manipulação do DOM
- ✅ Animações CSS avançadas
- ✅ Drag & Drop API
- ✅ Event handling
- ✅ Fetch API
- ✅ Estrutura modular
- ✅ Código limpo e organizado

## 📞 Contato

Para dúvidas ou sugestões, abra uma issue no GitHub!

---

⭐ Se você gostou deste projeto, não esqueça de dar uma estrela!

**Desenvolvido com ❤️ e Python**

