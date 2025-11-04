# 🌐 Guia de Uso do NandaBot no Streamlit

## 🚀 Executar Localmente

1. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

2. **Configure a API Key:**
   - Certifique-se de que o arquivo `.env` existe com sua `GROQ_API_KEY`

3. **Execute o Streamlit:**
```bash
# Windows
python -m streamlit run streamlit_app.py

# Linux/Mac
streamlit run streamlit_app.py
```

4. **Acesse no navegador:**
   - O Streamlit abrirá automaticamente em `http://localhost:8501`

## ☁️ Deploy no Streamlit Cloud

### Passo a Passo:

1. **Crie um repositório GitHub:**
   - Faça push de todo o código para um repositório GitHub
   - ⚠️ **IMPORTANTE:** Certifique-se de que o `.env` está no `.gitignore` (já está!)

2. **Acesse Streamlit Cloud:**
   - Vá para [share.streamlit.io](https://share.streamlit.io)
   - Faça login com sua conta GitHub

3. **Conecte seu repositório:**
   - Clique em "New app"
   - Selecione seu repositório
   - Selecione a branch (geralmente `main` ou `master`)
   - Defina o arquivo principal: `streamlit_app.py`

4. **Configure a variável de ambiente:**
   - Na seção "Advanced settings"
   - Adicione a variável de ambiente:
     - **Key:** `GROQ_API_KEY`
     - **Value:** Sua API key do Groq
   - Clique em "Save"

5. **Deploy:**
   - Clique em "Deploy"
   - Aguarde alguns minutos
   - Seu bot estará disponível na web! 🎉

## 📋 Checklist para Deploy

- [ ] Código no GitHub
- [ ] `.env` não está commitado (está no `.gitignore`)
- [ ] `requirements.txt` está atualizado
- [ ] Variável `GROQ_API_KEY` configurada no Streamlit Cloud
- [ ] Arquivo principal: `streamlit_app.py`

## 🎯 Funcionalidades Disponíveis na Web

### ✅ O que funciona:
- ✅ Upload de PDF via drag-and-drop
- ✅ Carregamento de sites via URL
- ✅ Carregamento de transcrições do YouTube
- ✅ Chat interativo com histórico
- ✅ Todas as validações de segurança
- ✅ Guardrails de conteúdo
- ✅ Interface moderna e responsiva

### 📝 Notas:
- O bot funciona exatamente como a versão terminal
- Todas as validações de segurança estão ativas
- O histórico de conversa é mantido durante a sessão
- Você pode limpar o documento e começar uma nova conversa

## 🔧 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install streamlit
```

### Erro: "streamlit não é reconhecido" (Windows)
No Windows, use:
```bash
python -m streamlit run streamlit_app.py
```
Em vez de apenas `streamlit run streamlit_app.py`

### Erro: "GROQ_API_KEY não encontrada"
- Verifique se a variável está configurada no Streamlit Cloud
- Ou se o arquivo `.env` existe localmente

### Erro ao fazer upload de PDF
- Verifique o tamanho do arquivo (máximo 50MB)
- Certifique-se de que é um PDF válido

## 💡 Dicas

- Use o botão "Limpar Conversa" para começar uma nova conversa
- Use "Limpar Documento" para carregar um novo documento
- O histórico é mantido durante toda a sessão
- Você pode fazer múltiplas perguntas sobre o mesmo documento

## 🌍 URL do seu Bot

Após o deploy, você receberá uma URL como:
```
https://seu-usuario-nandabot.streamlit.app
```

Compartilhe essa URL com quem quiser usar seu bot!

