"""
Módulo de guardrails para filtrar conteúdo ofensivo, danoso, malicioso ou ilegal
"""

import os
from typing import Tuple, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


def _get_chat_instance():
    """Obtém instância do chat (evita import circular)"""
    # Importação local para evitar circular import
    import os
    from dotenv import load_dotenv
    from pathlib import Path
    from langchain_groq import ChatGroq
    
    # Carrega env se necessário
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise ValueError("GROQ_API_KEY não encontrada!")
    
    # Configura a API key no ambiente
    os.environ['GROQ_API_KEY'] = api_key
    
    return ChatGroq(model='llama-3.3-70b-versatile')


def validar_conteudo_entrada(conteudo: str) -> Tuple[bool, Optional[str]]:
    """
    Valida conteúdo de entrada usando IA para detectar conteúdo ofensivo/perigoso.
    
    Args:
        conteudo: Conteúdo a ser validado
        
    Returns:
        Tuple[bool, Optional[str]]: (seguro, motivo_rejeicao)
    """
    if not conteudo or len(conteudo.strip()) == 0:
        return True, None
    
    # Limite de caracteres para validação (evita custos altos)
    conteudo_limite = conteudo[:5000] if len(conteudo) > 5000 else conteudo
    
    prompt = ChatPromptTemplate.from_messages([
        ('system', '''Você é um filtro de segurança. Analise o conteúdo fornecido e determine se ele contém:
- Conteúdo ofensivo, discriminatório ou de ódio
- Instruções para atividades ilegais ou perigosas
- Informações pessoais sensíveis (CPF, senhas, cartões)
- Conteúdo malicioso ou código malicioso
- Spam ou phishing

Responda APENAS com "SEGURO" ou "PERIGOSO: [motivo]". Seja específico no motivo.'''),
        ('user', f'Conteúdo para análise:\n\n{conteudo_limite}')
    ])
    
    try:
        chat = _get_chat_instance()
        chain = prompt | chat
        resposta = chain.invoke({}).content.strip()
        
        if resposta.upper().startswith('SEGURO'):
            return True, None
        else:
            # Extrai o motivo
            motivo = resposta.split(':', 1)[1].strip() if ':' in resposta else "Conteúdo potencialmente perigoso detectado"
            return False, motivo
    
    except Exception as e:
        # Em caso de erro na validação, permite mas registra
        print(f"⚠️ Aviso: Erro na validação de conteúdo: {e}")
        return True, None


def validar_resposta_saida(resposta: str) -> Tuple[bool, Optional[str]]:
    """
    Valida resposta do bot antes de exibir para o usuário.
    
    Args:
        resposta: Resposta gerada pelo bot
        
    Returns:
        Tuple[bool, Optional[str]]: (seguro, resposta_filtrada)
    """
    if not resposta or len(resposta.strip()) == 0:
        return True, resposta
    
    # Valida usando IA
    prompt = ChatPromptTemplate.from_messages([
        ('system', '''Você é um filtro de segurança. Analise a resposta do assistente e determine se ela contém:
- Conteúdo ofensivo, discriminatório ou de ódio
- Instruções para atividades ilegais ou perigosas
- Informações pessoais sensíveis
- Conteúdo inapropriado

REGRAS IMPORTANTES:
- Se a resposta for SEGURA, retorne APENAS a resposta original, sem qualquer explicação ou texto adicional
- Se for PERIGOSA, retorne APENAS: "PERIGOSO: [motivo]"
- NÃO adicione explicações, não repita a resposta, não diga "a resposta é segura"
- Retorne APENAS a resposta original se for segura, sem modificações'''),
        ('user', f'Analise esta resposta e retorne APENAS a resposta original se for segura, ou "PERIGOSO: [motivo]" se for perigosa:\n\n{resposta}')
    ])
    
    try:
        chat = _get_chat_instance()
        chain = prompt | chat
        resultado = chain.invoke({}).content.strip()
        
        if resultado.upper().startswith('PERIGOSO'):
            motivo = resultado.split(':', 1)[1].strip() if ':' in resultado else "Resposta filtrada por segurança"
            return False, f"[Resposta filtrada por segurança: {motivo}]"
        else:
            # Se a resposta foi validada como segura, retorna a resposta original
            # (evita qualquer texto explicativo que o modelo possa adicionar)
            # A validação já confirmou que é segura, então não há necessidade de retornar
            # a resposta do modelo de validação, apenas a original
            return True, resposta
    
    except Exception as e:
        # Em caso de erro, permite mas retorna resposta genérica
        print(f"⚠️ Aviso: Erro na validação de resposta: {e}")
        return True, resposta


def sanitizar_entrada_usuario(entrada: str) -> str:
    """
    Sanitiza entrada do usuário removendo caracteres potencialmente perigosos.
    
    Args:
        entrada: Entrada do usuário
        
    Returns:
        str: Entrada sanitizada
    """
    # Remove caracteres de controle
    entrada = ''.join(char for char in entrada if ord(char) >= 32 or char in '\n\r\t')
    
    # Limita tamanho
    if len(entrada) > 10000:
        entrada = entrada[:10000] + "... [truncado]"
    
    return entrada.strip()

