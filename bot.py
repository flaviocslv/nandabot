"""
Bot assistente usando LangChain Groq
API Key protegida através de variáveis de ambiente
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Carrega variáveis de ambiente do arquivo .env
# Garante que o arquivo .env seja encontrado no diretório do script
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Obtém a API key do ambiente (sem expor no código)
api_key = os.getenv('GROQ_API_KEY')

# Verifica se a API key foi configurada
if not api_key:
    raise ValueError(
        "GROQ_API_KEY não encontrada! "
        "Certifique-se de criar um arquivo .env com sua API key."
    )

# Configura a API key no ambiente
os.environ['GROQ_API_KEY'] = api_key

# Inicializa o chat
chat = ChatGroq(model='llama-3.3-70b-versatile')


def truncar_documento(documento, max_caracteres=60000):
    """
    Trunca o documento de forma inteligente para caber no limite de tokens.
    
    Args:
        documento: Documento completo
        max_caracteres: Número máximo de caracteres (padrão: 60000, ~15000 tokens)
                       Deixa espaço para system message, mensagens e resposta
    
    Returns:
        str: Documento truncado
    """
    if len(documento) <= max_caracteres:
        return documento
    
    # Se o documento é muito grande, tenta manter o início e partes relevantes
    # Primeiro, divide por seções (páginas)
    partes = documento.split('=== PÁGINA:')
    
    if len(partes) == 1:
        # Se não há separadores de página, apenas trunca
        return documento[:max_caracteres] + "\n\n[... documento truncado por limite de tamanho ...]"
    
    # Calcula quantas partes cabem
    documento_truncado = ""
    tamanho_atual = 0
    
    # Mantém o início (primeira página completa)
    if partes:
        primeira_parte = partes[0] if not partes[0].startswith('===') else '=== PÁGINA:' + partes[0]
        if tamanho_atual + len(primeira_parte) <= max_caracteres:
            documento_truncado += primeira_parte
            tamanho_atual += len(primeira_parte)
    
    # Adiciona páginas seguintes até o limite
    for parte in partes[1:]:
        parte_completa = '=== PÁGINA:' + parte
        if tamanho_atual + len(parte_completa) <= max_caracteres:
            documento_truncado += parte_completa
            tamanho_atual += len(parte_completa)
        else:
            # Se não cabe mais, adiciona aviso
            documento_truncado += f"\n\n[... documento truncado: {len(partes) - len(documento_truncado.split('=== PÁGINA:')) - 1} páginas restantes não incluídas por limite de tamanho ...]"
            break
    
    return documento_truncado


def resposta_bot(mensagens, documento):
    """
    Gera uma resposta do bot usando o modelo Groq.
    
    Args:
        mensagens: Lista de tuplas (role, content) com as mensagens
        documento: String com as informações para o contexto do bot
    
    Returns:
        str: Conteúdo da resposta gerada pelo bot
    """
    # Trunca documento se necessário para evitar exceder limite de tokens
    documento_truncado = truncar_documento(documento)
    
    # Se foi truncado, adiciona aviso (mas não adiciona ao documento para não consumir tokens)
    # O aviso será mostrado apenas se necessário
    if len(documento_truncado) < len(documento):
        # Não adiciona aviso ao documento para economizar tokens
        # O usuário será informado pela resposta se houver limitação
        pass
    
    system_message = '''Você é Nanda, um assistente amigável do NandaBot.
Você utiliza as seguintes informações para formular as suas respostas: {informacoes}

IMPORTANTE: Você deve sempre:
- Ser respeitoso e profissional
- Não fornecer instruções para atividades ilegais ou perigosas
- Não gerar conteúdo ofensivo, discriminatório ou de ódio
- Não expor informações pessoais sensíveis
- Ser útil e preciso nas respostas'''
    
    mensagens_modelo = [('system', system_message)]
    mensagens_modelo += mensagens
    
    template = ChatPromptTemplate.from_messages(mensagens_modelo)
    chain = template | chat
    
    return chain.invoke({'informacoes': documento_truncado}).content

