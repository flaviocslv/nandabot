"""
NandaBot - Interface Web com Streamlit
"""

import streamlit as st
import os
import tempfile
from pathlib import Path
from bot import resposta_bot
from carregadores import carrega_site, carrega_pdf, carrega_youtube
from guardrails import sanitizar_entrada_usuario, validar_conteudo_entrada, validar_resposta_saida

# Configuração da página
st.set_page_config(
    page_title="NandaBot - Assistente Inteligente",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        padding: 1rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Funções adaptadas para Streamlit (sem input())
def extrair_links_internos(url_base, html_content):
    """Extrai links internos de uma página HTML"""
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin, urlparse
    
    soup = BeautifulSoup(html_content, 'html.parser')
    links = set()
    dominio_base = urlparse(url_base).netloc
    
    for tag in soup.find_all('a', href=True):
        href = tag['href']
        # Converte link relativo para absoluto
        url_completa = urljoin(url_base, href)
        parsed = urlparse(url_completa)
        
        # Verifica se é do mesmo domínio e não é um link de âncora
        if parsed.netloc == dominio_base and not href.startswith('#'):
            # Remove fragmentos e query strings desnecessárias
            url_limpa = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if url_limpa and url_limpa not in links:
                links.add(url_limpa)
    
    return list(links)

def carrega_site_web(url, max_paginas=20):
    """
    Carrega site completo com múltiplas páginas.
    
    Args:
        url: URL inicial do site
        max_paginas: Número máximo de páginas a carregar (padrão: 20)
    
    Returns:
        str: Conteúdo completo combinado de todas as páginas
    """
    from langchain_community.document_loaders import WebBaseLoader
    import requests
    from urllib.parse import urlparse
    
    try:
        # Carrega página inicial
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        urls_para_carregar = [url]
        urls_carregadas = set()
        documento_completo = ''
        
        total_paginas = 1
        status_text.text(f"Carregando página 1/??: {url}")
        
        while urls_para_carregar and len(urls_carregadas) < max_paginas:
            url_atual = urls_para_carregar.pop(0)
            
            # Evita carregar a mesma URL duas vezes
            if url_atual in urls_carregadas:
                continue
            
            try:
                # Carrega a página
                loader = WebBaseLoader(url_atual)
                documentos = loader.load()
                
                if documentos:
                    conteudo = ''
                    for doc in documentos:
                        conteudo += doc.page_content + '\n'
                    
                    documento_completo += f"\n\n=== PÁGINA: {url_atual} ===\n\n"
                    documento_completo += conteudo
                    
                    urls_carregadas.add(url_atual)
                    
                    # Se ainda não atingiu o limite, extrai links desta página
                    if len(urls_carregadas) < max_paginas:
                        try:
                            # Faz requisição para extrair links
                            response = requests.get(url_atual, timeout=10, headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                            })
                            if response.status_code == 200:
                                links_encontrados = extrair_links_internos(url_atual, response.text)
                                
                                # Adiciona novos links à fila
                                for link in links_encontrados:
                                    if link not in urls_carregadas and link not in urls_para_carregar:
                                        urls_para_carregar.append(link)
                        except:
                            pass  # Se falhar ao extrair links, continua
                    
                    # Atualiza progresso
                    progresso = min(len(urls_carregadas) / max_paginas, 1.0)
                    progress_bar.progress(progresso)
                    status_text.text(f"Carregando página {len(urls_carregadas)}/{max_paginas}: {url_atual[:50]}...")
                    
            except Exception as e:
                # Se uma página falhar, continua com as próximas
                st.warning(f"⚠️ Não foi possível carregar {url_atual}: {str(e)[:50]}")
                continue
        
        progress_bar.empty()
        status_text.empty()
        
        if documento_completo:
            st.info(f"✓ Carregadas {len(urls_carregadas)} página(s) do site")
            return documento_completo
        else:
            st.error("❌ Não foi possível carregar nenhuma página do site.")
            return None
            
    except Exception as e:
        st.error(f"Erro ao carregar o site: {e}")
        return None

def carrega_pdf_web(caminho):
    """Carrega PDF com validação de segurança"""
    from langchain_community.document_loaders import PyPDFLoader
    from seguranca import validar_pdf_completo
    
    # Validação de segurança
    sucesso, erro = validar_pdf_completo(caminho)
    if not sucesso:
        st.error(f"PDF rejeitado por segurança: {erro}")
        return None
    
    try:
        loader = PyPDFLoader(caminho)
        lista_documentos = loader.load()
        documento = ''
        for doc in lista_documentos:
            documento += doc.page_content
        return documento
    except Exception as e:
        st.error(f"Erro ao carregar o PDF: {e}")
        return None

def carrega_youtube_web(url):
    """Carrega YouTube sem usar input()"""
    from youtube_transcript_api import YouTubeTranscriptApi
    import re
    
    def extract_video_id(url):
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
        if match:
            return match.group(1)
        raise ValueError("ID do vídeo não encontrado na URL.")
    
    try:
        video_id = extract_video_id(url)
        
        # Tenta buscar em português primeiro
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'pt-BR'])
            documento = " ".join([item['text'] for item in transcript_data])
            return documento
        except:
            # Se não encontrar em português, busca em qualquer idioma disponível
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            documento = " ".join([item['text'] for item in transcript_data])
            return documento
    except Exception as e:
        st.error(f"Erro ao carregar transcrição: {e}")
        return None

# Inicialização do estado da sessão
if 'mensagens' not in st.session_state:
    st.session_state.mensagens = []
if 'documento' not in st.session_state:
    st.session_state.documento = None
if 'documento_carregado' not in st.session_state:
    st.session_state.documento_carregado = False
if 'tipo_documento' not in st.session_state:
    st.session_state.tipo_documento = None

# Header
st.markdown('<h1 class="main-header">🤖 NandaBot</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar para carregar documentos
with st.sidebar:
    st.header("📄 Carregar Documento")
    
    opcao = st.radio(
        "Escolha a fonte de dados:",
        ["🌐 Site (URL)", "📄 PDF", "📺 YouTube"],
        key="fonte_dados"
    )
    
    if opcao == "🌐 Site (URL)":
        url = st.text_input("Digite a URL do site:", placeholder="https://exemplo.com")
        max_paginas = st.slider(
            "Número máximo de páginas a carregar:",
            min_value=1,
            max_value=50,
            value=10,
            help="O bot tentará carregar múltiplas páginas do mesmo domínio. Recomendado: 5-10 páginas para evitar exceder limite de tokens."
        )
        if st.button("Carregar Site", type="primary", use_container_width=True):
            if url:
                with st.spinner("Carregando conteúdo do site..."):
                    try:
                        # Usa função adaptada para web que carrega múltiplas páginas
                        documento = carrega_site_web(url, max_paginas=max_paginas)
                        if documento:
                            st.session_state.documento = documento
                            st.session_state.documento_carregado = True
                            st.session_state.tipo_documento = "Site"
                            st.session_state.mensagens = []  # Limpa histórico
                            st.success(f"✓ Site carregado! ({len(documento)} caracteres)")
                            st.rerun()
                        else:
                            st.error("❌ Não foi possível carregar o site.")
                    except Exception as e:
                        st.error(f"❌ Erro: {e}")
            else:
                st.warning("Por favor, digite uma URL válida.")
    
    elif opcao == "📄 PDF":
        uploaded_file = st.file_uploader(
            "Faça upload do arquivo PDF:",
            type=['pdf'],
            help="Tamanho máximo: 50MB"
        )
        if uploaded_file is not None:
            if st.button("Carregar PDF", type="primary", use_container_width=True):
                with st.spinner("Validando e carregando PDF..."):
                    try:
                        # Salva arquivo temporário
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                            tmp_file.write(uploaded_file.read())
                            tmp_path = tmp_file.name
                        
                        # Carrega PDF com validação
                        documento = carrega_pdf_web(tmp_path)
                        
                        if documento:
                            st.session_state.documento = documento
                            st.session_state.documento_carregado = True
                            st.session_state.tipo_documento = "PDF"
                            st.session_state.mensagens = []  # Limpa histórico
                            st.success(f"✓ PDF carregado! ({len(documento)} caracteres)")
                            
                            # Remove arquivo temporário
                            os.unlink(tmp_path)
                            st.rerun()
                        else:
                            os.unlink(tmp_path)
                            st.error("❌ PDF rejeitado por segurança ou não pôde ser carregado.")
                    except Exception as e:
                        st.error(f"❌ Erro: {e}")
                        if 'tmp_path' in locals():
                            try:
                                os.unlink(tmp_path)
                            except:
                                pass
    
    elif opcao == "📺 YouTube":
        url_youtube = st.text_input("Digite a URL do vídeo:", placeholder="https://youtube.com/watch?v=...")
        if st.button("Carregar YouTube", type="primary", use_container_width=True):
            if url_youtube:
                with st.spinner("Carregando transcrição do YouTube..."):
                    try:
                        documento = carrega_youtube_web(url_youtube)
                        if documento:
                            st.session_state.documento = documento
                            st.session_state.documento_carregado = True
                            st.session_state.tipo_documento = "YouTube"
                            st.session_state.mensagens = []  # Limpa histórico
                            st.success(f"✓ Transcrição carregada! ({len(documento)} caracteres)")
                            st.rerun()
                        else:
                            st.error("❌ Não foi possível obter a transcrição do vídeo.")
                    except Exception as e:
                        st.error(f"❌ Erro: {e}")
            else:
                st.warning("Por favor, digite uma URL válida do YouTube.")
    
    st.markdown("---")
    if st.button("🔄 Limpar Conversa", use_container_width=True):
        st.session_state.mensagens = []
        st.rerun()
    
    if st.button("📋 Limpar Documento", use_container_width=True):
        st.session_state.documento = None
        st.session_state.documento_carregado = False
        st.session_state.tipo_documento = None
        st.session_state.mensagens = []
        st.rerun()

# Área principal - Status do documento
if st.session_state.documento_carregado:
    st.success(f"📄 Documento carregado: **{st.session_state.tipo_documento}** ({len(st.session_state.documento)} caracteres)")
    st.markdown("---")
else:
    st.info("👈 Use a barra lateral para carregar um documento (Site, PDF ou YouTube)")
    st.markdown("---")

# Área de chat
if st.session_state.documento_carregado:
    # Exibe histórico de mensagens
    for mensagem in st.session_state.mensagens:
        role = mensagem['role']
        content = mensagem['content']
        
        if role == 'user':
            with st.chat_message("user"):
                st.markdown(content)
        else:
            with st.chat_message("assistant"):
                st.markdown(content)
    
    # Input do usuário
    pergunta = st.chat_input("Digite sua pergunta sobre o documento...")
    
    if pergunta:
        # Adiciona pergunta do usuário
        with st.chat_message("user"):
            st.markdown(pergunta)
        
        # Sanitiza e valida entrada
        pergunta_sanitizada = sanitizar_entrada_usuario(pergunta)
        seguro, motivo = validar_conteudo_entrada(pergunta_sanitizada)
        
        if not seguro:
            with st.chat_message("assistant"):
                st.error(f"⚠️ Sua mensagem foi bloqueada por segurança: {motivo}")
                st.info("Por favor, reformule sua pergunta de forma respeitosa e apropriada.")
        else:
            # Adiciona ao histórico
            st.session_state.mensagens.append({'role': 'user', 'content': pergunta_sanitizada})
            
            # Prepara mensagens no formato esperado pelo bot
            mensagens_bot = []
            for msg in st.session_state.mensagens:
                if msg['role'] in ['user', 'assistant']:
                    mensagens_bot.append((msg['role'], msg['content']))
            
            # Gera resposta do bot
            with st.spinner("NandaBot está pensando..."):
                try:
                    # Verifica tamanho do documento e avisa se foi truncado
                    tamanho_original = len(st.session_state.documento)
                    resposta = resposta_bot(mensagens_bot, st.session_state.documento)
                    
                    # Se o documento original era muito grande, avisa o usuário
                    if tamanho_original > 60000:
                        st.info(f"ℹ️ Documento grande ({tamanho_original:,} caracteres). Apenas as primeiras páginas foram usadas para esta resposta.")
                    
                    # Valida resposta do bot
                    seguro_resposta, resposta_final = validar_resposta_saida(resposta)
                    
                    # Exibe resposta
                    with st.chat_message("assistant"):
                        st.markdown(resposta_final)
                    
                    # Adiciona resposta ao histórico se for segura
                    if seguro_resposta:
                        st.session_state.mensagens.append({'role': 'assistant', 'content': resposta_final})
                    
                except Exception as e:
                    with st.chat_message("assistant"):
                        st.error(f"❌ Erro ao processar: {e}")
                    # Remove última mensagem em caso de erro
                    if st.session_state.mensagens:
                        st.session_state.mensagens.pop()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    "🤖 NandaBot - Assistente Inteligente com IA | Powered by Groq & LangChain"
    "</div>",
    unsafe_allow_html=True
)

