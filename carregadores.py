"""
Módulo para carregar documentos de diferentes fontes:
- Sites (Web)
- PDFs
- Vídeos do YouTube (transcrições)
"""

import re
import os
from pathlib import Path
from typing import Optional
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import PyPDFLoader
from youtube_transcript_api import YouTubeTranscriptApi
from seguranca import validar_pdf_completo

# Verifica se está rodando no Google Colab
try:
    from google.colab import drive
    IN_COLAB = True
except ImportError:
    IN_COLAB = False


def montar_drive():
    """
    Monta o Google Drive (apenas no Colab).
    Se não estiver no Colab, esta função não faz nada.
    """
    if IN_COLAB:
        drive.mount('/content/drive')
        print("Drive montado com sucesso!")
    else:
        print("Aviso: Esta função só funciona no Google Colab.")


def extrair_links_internos_terminal(url_base, html_content):
    """Extrai links internos de uma página HTML (versão terminal)"""
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin, urlparse
    
    soup = BeautifulSoup(html_content, 'html.parser')
    links = set()
    dominio_base = urlparse(url_base).netloc
    
    for tag in soup.find_all('a', href=True):
        href = tag['href']
        url_completa = urljoin(url_base, href)
        parsed = urlparse(url_completa)
        
        if parsed.netloc == dominio_base and not href.startswith('#'):
            url_limpa = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if url_limpa and url_limpa not in links:
                links.add(url_limpa)
    
    return list(links)

def carrega_site(max_paginas=20):
    """
    Carrega conteúdo de um site através da URL, incluindo múltiplas páginas.
    
    Args:
        max_paginas (int): Número máximo de páginas a carregar (padrão: 20)
    
    Returns:
        str: Conteúdo completo do site extraído de múltiplas páginas
    """
    url_site = input('Digite a URL do site: ')
    
    try:
        import requests
        from urllib.parse import urlparse
        
        urls_para_carregar = [url_site]
        urls_carregadas = set()
        documento_completo = ''
        
        print(f"\nCarregando até {max_paginas} páginas do site...")
        
        while urls_para_carregar and len(urls_carregadas) < max_paginas:
            url_atual = urls_para_carregar.pop(0)
            
            if url_atual in urls_carregadas:
                continue
            
            try:
                print(f"  Carregando: {url_atual}")
                loader = WebBaseLoader(url_atual)
                lista_documentos = loader.load()
                
                if lista_documentos:
                    conteudo = ''
                    for doc in lista_documentos:
                        conteudo += doc.page_content + '\n'
                    
                    documento_completo += f"\n\n=== PÁGINA: {url_atual} ===\n\n"
                    documento_completo += conteudo
                    
                    urls_carregadas.add(url_atual)
                    
                    # Extrai links se ainda não atingiu o limite
                    if len(urls_carregadas) < max_paginas:
                        try:
                            response = requests.get(url_atual, timeout=10, headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                            })
                            if response.status_code == 200:
                                links_encontrados = extrair_links_internos_terminal(url_atual, response.text)
                                for link in links_encontrados:
                                    if link not in urls_carregadas and link not in urls_para_carregar:
                                        urls_para_carregar.append(link)
                        except:
                            pass
                    
            except Exception as e:
                print(f"  ⚠️ Erro ao carregar {url_atual}: {str(e)[:50]}")
                continue
        
        if documento_completo:
            print(f"\n✓ Site carregado com sucesso! ({len(urls_carregadas)} páginas, {len(documento_completo)} caracteres)")
            return documento_completo
        else:
            print("❌ Não foi possível carregar nenhuma página do site.")
            return ''
    
    except Exception as e:
        print(f"Erro ao carregar o site: {e}")
        return ''


def solicitar_upload_pdf() -> Optional[str]:
    """
    Solicita ao usuário o caminho do arquivo PDF para upload.
    Suporta tanto caminho local quanto copiar arquivo.
    
    Returns:
        Optional[str]: Caminho do arquivo válido ou None
    """
    print("\n=== Upload de PDF ===")
    print("Opções:")
    print("1. Digite o caminho completo do arquivo PDF")
    print("2. Cole o arquivo nesta pasta e digite o nome do arquivo")
    
    opcao = input("\nEscolha uma opção (1 ou 2): ").strip()
    
    if opcao == '1':
        caminho = input('Digite o caminho completo do arquivo PDF: ').strip()
        caminho = caminho.strip('"').strip("'")  # Remove aspas se houver
        
        if os.path.exists(caminho):
            return caminho
        else:
            print(f"❌ Arquivo não encontrado: {caminho}")
            return None
    
    elif opcao == '2':
        nome_arquivo = input('Digite o nome do arquivo PDF (ex: documento.pdf): ').strip()
        nome_arquivo = nome_arquivo.strip('"').strip("'")
        
        # Procura na pasta atual
        caminho_atual = Path.cwd() / nome_arquivo
        
        if caminho_atual.exists():
            return str(caminho_atual)
        else:
            print(f"❌ Arquivo não encontrado na pasta atual: {nome_arquivo}")
            print(f"   Pasta atual: {Path.cwd()}")
            return None
    
    else:
        print("❌ Opção inválida")
        return None


def carrega_pdf(caminho=None, validar_seguranca=True):
    """
    Carrega conteúdo de um arquivo PDF com validação de segurança.
    
    Args:
        caminho (str, optional): Caminho do arquivo PDF.
                                Se None, solicita upload do usuário.
        validar_seguranca (bool): Se True, valida segurança do PDF.
    
    Returns:
        str: Conteúdo completo do PDF extraído
    """
    if caminho is None:
        if IN_COLAB:
            # Caminho padrão para Colab
            caminho = '/content/drive/MyDrive/Colab Notebooks/arquivos/App. Colibri  Pro versão 3.pdf'
        else:
            # Solicita upload do usuário
            caminho = solicitar_upload_pdf()
            if caminho is None:
                return ''
    
    # Validação de segurança
    if validar_seguranca:
        print("🔒 Validando segurança do PDF...")
        sucesso, erro = validar_pdf_completo(caminho)
        
        if not sucesso:
            print(f"❌ PDF rejeitado por segurança: {erro}")
            return ''
        
        print("✓ Validação de segurança concluída")
    
    try:
        loader = PyPDFLoader(caminho)
        lista_documentos = loader.load()
        documento = ''
        
        for doc in lista_documentos:
            documento += doc.page_content
        
        print(f"✓ PDF carregado com sucesso! ({len(lista_documentos)} páginas, {len(documento)} caracteres)")
        return documento
    
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo não encontrado em {caminho}")
        return ''
    except Exception as e:
        print(f"❌ Erro ao carregar o PDF: {e}")
        return ''


def extract_video_id(url):
    """
    Extrai o ID do vídeo de uma URL do YouTube.
    
    Args:
        url (str): URL do vídeo do YouTube
    
    Returns:
        str: ID do vídeo
    
    Raises:
        ValueError: Se o ID não for encontrado na URL
    """
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    if match:
        return match.group(1)
    raise ValueError("ID do vídeo não encontrado na URL.")


def carrega_youtube(url_youtube=None):
    """
    Carrega a transcrição de um vídeo do YouTube.
    
    Args:
        url_youtube (str, optional): URL do vídeo do YouTube.
                                    Se None, solicita input do usuário.
    
    Returns:
        str: Transcrição completa do vídeo
    """
    if url_youtube is None:
        url_youtube = input("Digite a URL do vídeo: ")
    
    documento = ''
    
    try:
        video_id = extract_video_id(url_youtube)
        
        # Lista idiomas disponíveis
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            print("Idiomas disponíveis:")
            for transcript in transcript_list:
                print(f"  - {transcript.language} ({transcript.language_code})")
        except Exception as e:
            print(f"Aviso: Não foi possível listar idiomas disponíveis: {e}")
        
        # Tenta buscar em português primeiro
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'pt-BR'])
            documento = " ".join([item['text'] for item in transcript_data])
            print(f"✓ Transcrição em português carregada com sucesso! ({len(documento)} caracteres)")
        
        except:
            # Se não encontrar em português, busca em qualquer idioma disponível
            try:
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
                documento = " ".join([item['text'] for item in transcript_data])
                print(f"✓ Transcrição carregada com sucesso! ({len(documento)} caracteres)")
            except Exception as e:
                print(f"Erro: Não foi possível obter a transcrição do vídeo: {e}")
                documento = ''
        
        if not documento:
            print("Aviso: Não foi possível obter a transcrição do vídeo (não possui legenda pública disponível).")
    
    except ValueError as e:
        print(f"Erro na URL: {e}")
        documento = ''
    except Exception as e:
        print(f"Erro ao carregar transcrição: {e}")
        documento = ''
    
    return documento


# Exemplo de uso
if __name__ == "__main__":
    print("=== Teste dos Carregadores ===\n")
    
    # Exemplo de uso
    # documento_site = carrega_site()
    # documento_pdf = carrega_pdf()
    # documento_youtube = carrega_youtube()
    
    print("\nFunções disponíveis:")
    print("- carrega_site()")
    print("- carrega_pdf(caminho=None)")
    print("- carrega_youtube(url_youtube=None)")
    print("- montar_drive()  # Apenas no Colab")

