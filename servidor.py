import socket
import json
import csv
import os

# ---------------------------------------------
# CONFIGURAÇÕES DA REDE E DO PROTOCOLO
# ---------------------------------------------
HOST = 'localhost'
PORT = 5000
SENHA_ACESSO = 'nucleo_admin'
ARQUIVO_CSV = 'dados_consolidados.csv'

def iniciar_servidor():
    # Cria o socket TCP
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))
    servidor.listen(5)
    
    print('==================================================')
    print('  SERVIDOR CENTRAL - LIGADO E ESCUTANDO  ')
    print('==================================================')

    # Cria o cabeçalho do arquivo Planilha/CSV se ele ainda não existir
    if not os.path.exists(ARQUIVO_CSV):
        with open(ARQUIVO_CSV, mode='w', newline='', encoding='utf-8') as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(['Origem', 'Status', 'Pendencias'])

    # Loop infinito para manter o servidor sempre rodando
    while True:
        conexao, endereco = servidor.accept()
        print(f'\n[REDE] Conexao recebida de: {endereco}')
        
        try:
            # ---------------------------------------------
            # CAMADA DE APLICAÇÃO: ESTADO DE AUTENTICAÇÃO
            # ---------------------------------------------
            msg_auth = conexao.recv(1024).decode('utf-8')
            
            if msg_auth.startswith('AUTH|'):
                senha_recebida = msg_auth.split('|')[1]
                
                if senha_recebida == SENHA_ACESSO:
                    # Senha correta: Transita para o estado PRONTO_PARA_DADOS
                    conexao.send('200_AUTH_OK'.encode('utf-8'))
                    print('[PROTOCOLO] Autenticacao aceita. Aguardando relatorios...')
                    
                    # ---------------------------------------------
                    # CAMADA DE APLICAÇÃO: ESTADO DE RECEBIMENTO
                    # ---------------------------------------------
                    msg_dados = conexao.recv(4096).decode('utf-8')
                    
                    if msg_dados.startswith('DATA|'):
                        # Desempacota o texto JSON que veio pela rede
                        json_dados = msg_dados.split('|')[1]
                        lista_relatorios = json.loads(json_dados)
                        
                        # Salva os dados recebidos no nosso arquivo consolidado (CSV)
                        with open(ARQUIVO_CSV, mode='a', newline='', encoding='utf-8') as arquivo:
                            escritor = csv.writer(arquivo)
                            for item in lista_relatorios:
                                escritor.writerow([item['nome'], item['status'], item['pendencias']])
                        
                        # Envia o recibo oficial de sucesso do nosso protocolo
                        conexao.send('201_DATA_ACK'.encode('utf-8'))
                        print(f'[PROTOCOLO] {len(lista_relatorios)} relatorio(s) salvo(s) na planilha com sucesso.')
                        
                    else:
                        conexao.send('400_BAD_REQ'.encode('utf-8'))
                else:
                    # Senha incorreta
                    conexao.send('401_UNAUTH'.encode('utf-8'))
                    print('[PROTOCOLO] Senha incorreta. Conexao rejeitada.')
        
        except Exception as erro:
            print(f'[ERRO] Falha no processamento: {erro}')
        
        finally:
            # Encerra apenas o canal deste cliente específico, mantendo o servidor vivo
            conexao.close()
            print('[REDE] Canal finalizado.')

if __name__ == '__main__':
    iniciar_servidor()
