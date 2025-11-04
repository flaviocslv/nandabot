# Meu Projeto

Descrição do projeto...

## Instalação

### 1. Criar ambiente virtual (recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar API Key (IMPORTANTE!)

**Crie um arquivo `.env` na raiz do projeto** com sua API key:

```bash
# Windows
echo GROQ_API_KEY=sua_api_key_aqui > .env

# Linux/Mac
echo "GROQ_API_KEY=sua_api_key_aqui" > .env
```

Ou crie manualmente um arquivo `.env` com o seguinte conteúdo:
```
GROQ_API_KEY=*********************************************
```

**⚠️ IMPORTANTE:** O arquivo `.env` já está no `.gitignore` e não será commitado no git. Nunca exponha sua API key no código!

## Uso

### 🌐 Versão Web (Streamlit) - RECOMENDADO

Execute a interface web do NandaBot:

```bash
# Windows
python -m streamlit run streamlit_app.py

# Linux/Mac
streamlit run streamlit_app.py
```

Isso abrirá uma interface web no seu navegador onde você pode:
- 📄 Fazer upload de arquivos PDF
- 🌐 Carregar conteúdo de sites via URL
- 📺 Obter transcrições de vídeos do YouTube
- 💬 Conversar com o bot em uma interface moderna

**Para usar na web (Streamlit Cloud):**
1. Faça push do código para um repositório GitHub
2. Acesse [streamlit.io](https://streamlit.io)
3. Conecte seu repositório
4. Configure a variável de ambiente `GROQ_API_KEY` no Streamlit Cloud
5. Deploy automático!

### 💻 Versão Terminal:

```bash
python main.py
```

Isso abrirá um menu interativo onde você pode:
1. Carregar conteúdo de um site
2. Carregar um arquivo PDF
3. Carregar transcrição de vídeo do YouTube
4. Conversar com o bot usando o documento carregado

### Uso programático:

#### Carregar documentos:

```python
from carregadores import carrega_site, carrega_pdf, carrega_youtube

# Carregar site
documento = carrega_site()

# Carregar PDF
documento = carrega_pdf('caminho/para/arquivo.pdf')

# Carregar YouTube
documento = carrega_youtube('https://www.youtube.com/watch?v=VIDEO_ID')
```

#### Usar o bot:

```python
from bot import resposta_bot

mensagens = [
    ('user', 'Olá, como você está?')
]
documento = "Informações sobre o projeto..."

resposta = resposta_bot(mensagens, documento)
print(resposta)
```

### Exemplo completo:

```python
from carregadores import carrega_youtube
from bot import resposta_bot

# Carrega transcrição do YouTube
documento = carrega_youtube('https://www.youtube.com/watch?v=VIDEO_ID')

# Faz perguntas sobre o conteúdo
mensagens = [
    ('user', 'Qual o tema principal deste vídeo?')
]

resposta = resposta_bot(mensagens, documento)
print(resposta)
```

### Nota sobre Google Colab:

Se você estiver usando no Google Colab, o código detecta automaticamente e:
- Permite montar o Google Drive
- Usa caminhos padrão do Colab para PDFs
- Funciona normalmente com todas as outras funcionalidades

## Estrutura do Projeto

```
.
├── README.md
├── requirements.txt
├── .gitignore
├── bot.py              # Bot assistente com API key protegida
├── carregadores.py     # Funções para carregar sites, PDFs e YouTube
├── seguranca.py        # Validações de segurança para PDFs
├── guardrails.py       # Guardrails para conteúdo ofensivo/perigoso
├── main.py             # Aplicação principal com menu interativo (terminal)
├── streamlit_app.py    # Interface web com Streamlit
├── exemplo.py          # Exemplos de uso das bibliotecas
├── projeto.md
└── .env                # Arquivo com API keys (não versionado)
```

## Segurança

O NandaBot implementa várias camadas de segurança:

### Validação de PDF
- ✅ Verificação de formato e estrutura
- ✅ Limite de tamanho (50MB)
- ✅ Limite de páginas (1000)
- ✅ Detecção de código malicioso
- ✅ Escaneamento de padrões suspeitos

### Guardrails
- ✅ Validação de entrada do usuário
- ✅ Validação de saída do bot
- ✅ Filtro de conteúdo ofensivo/perigoso
- ✅ Proteção contra tentativas de exploração
- ✅ Sanitização de entrada

## Módulos

### `bot.py`
- Gerencia a API key do Groq de forma segura (via `.env`)
- Função `resposta_bot()` para gerar respostas usando o modelo Llama 3.3
- Instruções de segurança incorporadas no prompt do sistema

### `carregadores.py`
- `carrega_site()`: Extrai conteúdo de sites web
- `carrega_pdf()`: Extrai texto de arquivos PDF com validação de segurança
- `solicitar_upload_pdf()`: Permite upload de arquivos PDF pelo usuário
- `carrega_youtube()`: Obtém transcrições de vídeos do YouTube
- `montar_drive()`: Monta Google Drive (apenas no Colab)

### `seguranca.py`
- `validar_pdf_completo()`: Validação completa de PDF (tamanho, formato, conteúdo)
- `escanear_conteudo_suspeito()`: Detecta padrões maliciosos no conteúdo
- Proteção contra exploits, código malicioso e arquivos corrompidos

### `guardrails.py`
- `validar_conteudo_entrada()`: Valida conteúdo de entrada do usuário
- `validar_resposta_saida()`: Valida respostas do bot antes de exibir
- `sanitizar_entrada_usuario()`: Sanitiza entrada do usuário
- Filtra conteúdo ofensivo, danoso, malicioso ou ilegal

### `main.py`
- Menu interativo completo (versão terminal)
- Integra carregadores com o bot
- Permite conversas contínuas com contexto
- Validação de entrada e saída com guardrails

### `streamlit_app.py`
- Interface web moderna com Streamlit
- Upload de arquivos PDF via drag-and-drop
- Carregamento de sites e YouTube via URL
- Chat interativo com histórico de mensagens
- Todas as validações de segurança integradas
- Pronto para deploy no Streamlit Cloud

