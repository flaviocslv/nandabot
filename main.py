"""
Aplicação principal do NandaBot
Integra o bot com os carregadores de documentos
"""

from bot import resposta_bot
from carregadores import carrega_site, carrega_pdf, carrega_youtube


def main():
    """
    Função principal do NandaBot com menu interativo e loop de conversa.
    """
    print('Bem vindo ao NandaBot')
    
    texto_selecao = '''\nDigite 1 se você quiser conversar com um site
Digite 2 se você quiser conversar com um PDF
Digite 3 se você quiser conversar com um vídeo do Youtube
Digite X se você quiser encerrar a conversa\n'''
    
    while True:
        selecao = input(texto_selecao)
        
        if selecao == '1':
            print('Você escolheu conversar com um site')
            documento = carrega_site()
            break
        
        if selecao == '2':
            print('Você escolheu conversar com um PDF')
            documento = carrega_pdf()
            break
        
        if selecao == '3':
            print('Você escolheu conversar com um vídeo do Youtube')
            documento = carrega_youtube()
            break
        
        if selecao.upper() == 'X':
            print('\nMuito obrigado por utilizar o NandaBot!')
            return
        
        print('Opção inválida!\n Digite uma opção entre 1 e 3: ')
    
    # Verifica se o documento foi carregado com sucesso
    if not documento:
        print('\n⚠️ Não foi possível carregar o documento. Encerrando...')
        return
    
    # Loop de conversa com o bot
    mensagens = []
    
    while True:
        pergunta = input('Usuário: ')
        
        if pergunta.lower() == 'x':
            break
        
        # Sanitiza e valida entrada do usuário
        from guardrails import sanitizar_entrada_usuario, validar_conteudo_entrada
        
        pergunta_sanitizada = sanitizar_entrada_usuario(pergunta)
        
        # Valida conteúdo de entrada
        seguro, motivo = validar_conteudo_entrada(pergunta_sanitizada)
        if not seguro:
            print(f'⚠️ Sua mensagem foi bloqueada por segurança: {motivo}')
            print('   Por favor, reformule sua pergunta de forma respeitosa e apropriada.')
            continue
        
        mensagens.append(('user', pergunta_sanitizada))
        
        try:
            resposta = resposta_bot(mensagens, documento)
            
            # Valida resposta do bot
            from guardrails import validar_resposta_saida
            seguro_resposta, resposta_final = validar_resposta_saida(resposta)
            
            if seguro_resposta:
                mensagens.append(('assistant', resposta_final))
                print(f'NandaBot: {resposta_final}')
            else:
                print(f'NandaBot: {resposta_final}')
                # Não adiciona resposta filtrada ao histórico
        except Exception as e:
            print(f'❌ Erro ao processar: {e}')
            # Remove a última mensagem em caso de erro
            mensagens.pop()
    
    print('\nMuito obrigado por utilizar o NandaBot!')


if __name__ == "__main__":
    main()

