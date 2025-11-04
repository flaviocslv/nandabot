# NandaBot - Assistente Inteligente com IA

## Descrição

O **NandaBot** é um assistente virtual inteligente desenvolvido em Python que utiliza inteligência artificial para conversar sobre conteúdos extraídos de diferentes fontes. O bot é capaz de processar e responder perguntas sobre documentos carregados de sites web, arquivos PDF e transcrições de vídeos do YouTube.

## Funcionalidades Principais

### 🤖 Assistente Conversacional
- Interface amigável chamada "Nanda"
- Capacidade de manter contexto durante a conversa
- Respostas baseadas no conteúdo dos documentos carregados

### 📄 Carregamento de Documentos
- **Sites Web**: Extrai e processa conteúdo de páginas web através de URL
- **Arquivos PDF**: Lê e extrai texto completo de documentos PDF
- **Vídeos do YouTube**: Obtém transcrições automáticas de vídeos do YouTube

### 🔒 Segurança
- **API keys protegidas**: Variáveis de ambiente (arquivo `.env`) não versionado
- **Validação de PDF**: Verificação de formato, tamanho (50MB), estrutura e conteúdo
- **Detecção de código malicioso**: Escaneamento de padrões suspeitos (scripts, comandos, exploits)
- **Guardrails de conteúdo**: Validação de entrada e saída para filtrar conteúdo ofensivo, danoso ou ilegal
- **Sanitização**: Limpeza de entrada do usuário para prevenir injeção
- **Limites de segurança**: Máximo de 1000 páginas por PDF, 50MB por arquivo

## Tecnologias Utilizadas

- **LangChain**: Framework para aplicações com LLM (Large Language Models)
- **LangChain Groq**: Integração com a API Groq para modelos de IA
- **LangChain Community**: Módulos comunitários para carregamento de documentos
- **YouTube Transcript API**: Extração de transcrições de vídeos
- **PyPDF**: Processamento de arquivos PDF
- **Python-dotenv**: Gerenciamento seguro de variáveis de ambiente

## Modelo de IA

O bot utiliza o modelo **Llama 3.3 70B Versatile** através da plataforma Groq, proporcionando respostas rápidas e precisas.

## Compatibilidade

- ✅ Ambiente local (Windows, Linux, Mac)
- ✅ Google Colab (detecção automática do ambiente)
- ✅ Suporte a múltiplos idiomas nas transcrições do YouTube

## Arquitetura

O projeto segue uma arquitetura modular com múltiplas camadas de segurança:
- **`bot.py`**: Lógica do assistente e gerenciamento da API com instruções de segurança
- **`carregadores.py`**: Módulo para extrair conteúdo de diferentes fontes com validação
- **`seguranca.py`**: Validações de segurança para PDFs (formato, tamanho, conteúdo malicioso)
- **`guardrails.py`**: Filtros de conteúdo para entrada e saída (ofensivo, perigoso, ilegal)
- **`main.py`**: Interface principal com menu interativo e validações integradas
- **`requirements.txt`**: Gerenciamento de dependências
- **`.env`**: Configurações sensíveis (não versionado)

## Uso

Execute `python main.py` para iniciar o assistente interativo, escolha a fonte de dados desejada e comece a conversar sobre o conteúdo carregado!
