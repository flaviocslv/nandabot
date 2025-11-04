"""
Módulo de segurança e guardrails para o NandaBot
Valida conteúdo, detecta conteúdo ofensivo/perigoso e previne exploits
"""

import re
import os
from pathlib import Path
from typing import Tuple, Optional
import pypdf


# Tamanho máximo do arquivo (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024

# Padrões suspeitos para detectar código malicioso
PADROES_SUSPEITOS = [
    # Tentativas de execução de código
    (r'<script[^>]*>', 'Script embutido detectado'),
    (r'javascript:', 'JavaScript detectado'),
    (r'eval\s*\(', 'Função eval detectada'),
    (r'exec\s*\(', 'Função exec detectada'),
    (r'__import__', 'Importação dinâmica detectada'),
    (r'subprocess', 'Subprocess detectado'),
    (r'os\.system', 'Sistema operacional detectado'),
    (r'shell\s*=', 'Shell command detectado'),
    (r'cmd\s*=', 'Comando detectado'),
    # URLs suspeitas
    (r'file:///', 'Acesso a arquivo local detectado'),
    (r'\\\\', 'Caminho de rede detectado'),
    # Comandos SQL
    (r'(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\s+', 'Comando SQL detectado'),
    # Path traversal
    (r'\.\./', 'Path traversal detectado'),
    (r'\.\.\\\\', 'Path traversal detectado'),
]


def validar_tamanho_arquivo(caminho_arquivo: str) -> Tuple[bool, Optional[str]]:
    """
    Valida o tamanho do arquivo.
    
    Args:
        caminho_arquivo: Caminho do arquivo
        
    Returns:
        Tuple[bool, Optional[str]]: (sucesso, mensagem_erro)
    """
    try:
        tamanho = os.path.getsize(caminho_arquivo)
        
        if tamanho > MAX_FILE_SIZE:
            return False, f"Arquivo muito grande ({tamanho / 1024 / 1024:.2f}MB). Tamanho máximo: {MAX_FILE_SIZE / 1024 / 1024}MB"
        
        if tamanho == 0:
            return False, "Arquivo vazio"
        
        return True, None
    
    except Exception as e:
        return False, f"Erro ao verificar tamanho do arquivo: {e}"


def validar_formato_pdf(caminho_arquivo: str) -> Tuple[bool, Optional[str]]:
    """
    Valida se o arquivo é um PDF válido e não corrompido.
    
    Args:
        caminho_arquivo: Caminho do arquivo PDF
        
    Returns:
        Tuple[bool, Optional[str]]: (sucesso, mensagem_erro)
    """
    try:
        # Verifica extensão
        if not caminho_arquivo.lower().endswith('.pdf'):
            return False, "Arquivo não é um PDF (extensão inválida)"
        
        # Tenta ler o cabeçalho do PDF
        with open(caminho_arquivo, 'rb') as f:
            header = f.read(4)
            if header != b'%PDF':
                return False, "Arquivo não é um PDF válido (cabeçalho inválido)"
        
        # Tenta abrir com pypdf para verificar estrutura
        try:
            reader = pypdf.PdfReader(caminho_arquivo, strict=True)
            num_pages = len(reader.pages)
            
            if num_pages == 0:
                return False, "PDF não possui páginas"
            
            if num_pages > 1000:
                return False, f"PDF possui muitas páginas ({num_pages}). Limite: 1000 páginas"
            
            return True, None
        
        except pypdf.errors.PdfReadError as e:
            return False, f"PDF corrompido ou inválido: {str(e)}"
        except Exception as e:
            return False, f"Erro ao validar PDF: {str(e)}"
    
    except Exception as e:
        return False, f"Erro ao validar formato do PDF: {e}"


def escanear_conteudo_suspeito(conteudo: str) -> Tuple[bool, Optional[str]]:
    """
    Escaneia o conteúdo em busca de padrões suspeitos ou maliciosos.
    
    Args:
        conteudo: Conteúdo a ser escaneado
        
    Returns:
        Tuple[bool, Optional[str]]: (seguro, motivo_risco)
    """
    conteudo_lower = conteudo.lower()
    
    for padrao, descricao in PADROES_SUSPEITOS:
        if re.search(padrao, conteudo_lower, re.IGNORECASE):
            return False, f"Conteúdo suspeito detectado: {descricao}"
    
    # Verifica se há muitos caracteres especiais suspeitos
    caracteres_especiais = sum(1 for c in conteudo if ord(c) > 127 and not c.isalnum())
    if len(conteudo) > 0 and caracteres_especiais / len(conteudo) > 0.5:
        return False, "Alto percentual de caracteres especiais suspeitos detectado"
    
    return True, None


def validar_pdf_completo(caminho_arquivo: str) -> Tuple[bool, Optional[str]]:
    """
    Validação completa do PDF: tamanho, formato e conteúdo.
    
    Args:
        caminho_arquivo: Caminho do arquivo PDF
        
    Returns:
        Tuple[bool, Optional[str]]: (sucesso, mensagem_erro)
    """
    # Valida tamanho
    sucesso, erro = validar_tamanho_arquivo(caminho_arquivo)
    if not sucesso:
        return False, erro
    
    # Valida formato
    sucesso, erro = validar_formato_pdf(caminho_arquivo)
    if not sucesso:
        return False, erro
    
    # Extrai e valida conteúdo
    try:
        reader = pypdf.PdfReader(caminho_arquivo, strict=True)
        conteudo_total = ""
        
        # Limita a 100 primeiras páginas para validação (evita sobrecarga)
        paginas_validar = min(100, len(reader.pages))
        
        for i in range(paginas_validar):
            try:
                texto = reader.pages[i].extract_text()
                conteudo_total += texto
                
                # Valida cada página
                seguro, motivo = escanear_conteudo_suspeito(texto)
                if not seguro:
                    return False, f"Página {i+1}: {motivo}"
            
            except Exception as e:
                return False, f"Erro ao extrair texto da página {i+1}: {str(e)}"
        
        return True, None
    
    except Exception as e:
        return False, f"Erro ao validar conteúdo do PDF: {str(e)}"

