import tkinter as tk
from tkinter import messagebox
import socket
import json
import os

# ---------------------------------------------
# CONFIGURAÇÕES DE REDE E BUFFER
# ---------------------------------------------
HOST = 'localhost'
PORT = 5000
SENHA_ACESSO = 'nucleo_admin'
ARQUIVO_BUFFER = 'buffer_pendentes.json'

def salvar_no_buffer(dados):
    """Lê o arquivo local, adiciona o novo relatório e salva de novo."""
    lista_pendentes = []
    
    # Se já existir relatórios guardados, lê primeiro para não apagar
    if os.path.exists(ARQUIVO_BUFFER):
        with open(ARQUIVO_BUFFER, 'r', encoding='utf-8') as arquivo:
            try:
                lista_pendentes = json.load(arquivo)
            except json.JSONDecodeError:
                lista_pendentes = []
    
    # Adiciona o novo relatório do dia na lista
    lista_pendentes.append(dados)
    
    # Salva a lista inteira de volta no computador
    with open(ARQUIVO_BUFFER, 'w', encoding='utf-8') as arquivo:
        json.dump(lista_pendentes, arquivo)

def capturar_tela():
    """Função engatilhada quando o usuário clica no botão 'Enviar' da tela."""
    nome = entrada_nome.get()
    status = entrada_status.get()
    pendencias = entrada_pendencias.get()

    # Validação simples
    if nome == '' or status == '':
        messagebox.showwarning('Aviso', 'Preencha ao menos o Nome e o Status!')
        return

    pacote = {
        'nome': nome,
        'status': status,
        'pendencias': pendencias
    }
    
    # Em vez de jogar direto na rede, joga no cofre local
    salvar_no_buffer(pacote)
    
    messagebox.showinfo('Sucesso', 'Relatório registrado! O sistema sincronizará com a central assim que possível.')
    
    # Limpa as caixinhas brancas da tela
    entrada_nome.delete(0, tk.END)
    entrada_status.delete(0, tk.END)
    entrada_pendencias.delete(0, tk.END)

def verificador_de_rede():
    """Função de background: Tenta conectar de tempos em tempos para esvaziar o buffer."""
    if os.path.exists(ARQUIVO_BUFFER):
        with open(ARQUIVO_BUFFER, 'r', encoding='utf-8') as arquivo:
            try:
                dados_buffer = json.load(arquivo)
            except:
                dados_buffer = []

        if len(dados_buffer) > 0:
            try:
                # Tenta abrir o TCP
                cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                cliente.connect((HOST, PORT))
                
                # Envia a senha do nosso protocolo
                cliente.send(f'AUTH|{SENHA_ACESSO}'.encode('utf-8'))
                resposta_auth = cliente.recv(1024).decode('utf-8')
                
                if resposta_auth == '200_AUTH_OK':
                    # Transforma a lista de relatórios num texto JSON e envia
                    dados_texto = json.dumps(dados_buffer)
                    cliente.send(f'DATA|{dados_texto}'.encode('utf-8'))
                    
                    # Aguarda o recibo de que o servidor salvou tudo
                    resposta_dados = cliente.recv(1024).decode('utf-8')
                    
                    # Se o recibo oficial chegou, limpa o cofre da máquina
                    if resposta_dados == '201_DATA_ACK':
                        os.remove(ARQUIVO_BUFFER)
                        print('[SISTEMA] Sincronizacao concluida. Buffer limpo.')
                
                cliente.close()
            except (ConnectionRefusedError, socket.error):
                # Falha silenciosa. O usuário nem percebe que a rede falhou.
                print('[SISTEMA] Sem rede no momento. Buffer mantido para proxima tentativa.')

    # O segredo: Agenda para rodar esta MESMA função daqui a 10 segundos (10000 ms)
    # Na vida real do NTE, poderíamos colocar 60000 (1 minuto)
    janela.after(10000, verificador_de_rede)

# ---------------------------------------------
# CONSTRUÇÃO DA INTERFACE GRÁFICA (TKINTER)
# ---------------------------------------------
janela = tk.Tk()
janela.title('Portal de Demandas do Núcleo')
janela.geometry('350x350')

tk.Label(janela, text='Envio de Relatorio Diario', font=('Arial', 14, 'bold')).pack(pady=15)

tk.Label(janela, text='Nome da Unidade ou Setor:').pack()
entrada_nome = tk.Entry(janela, width=30)
entrada_nome.pack(pady=5)

tk.Label(janela, text='Demanda:').pack()
entrada_status = tk.Entry(janela, width=30)
entrada_status.pack(pady=5)

tk.Label(janela, text='Status (Ex: Concluído):').pack()
entrada_pendencias = tk.Entry(janela, width=30)
entrada_pendencias.pack(pady=5)

# O botão chama apenas a função de salvar no buffer local
tk.Button(janela, text='Registrar Demanda', command=capturar_tela, bg='lightgreen').pack(pady=20)

# Dá o 'start' no verificador de rede invisível antes de desenhar a janela na tela
verificador_de_rede()

janela.mainloop()
