Trabalho desenvolvido para a disciplina de Redes de Computadores I, ministrada pelo professor Jorge Lima de Oliveira Filho.

# Sistema Integrado de Monitoramento de Demandas

O **Sistema Integrado de Monitoramento de Demandas** é uma aplicação distribuída baseada na arquitetura Cliente-Servidor desenvolvida em Python 3. O projeto foi concebido a partir de um problema observado na rotina de governança de um departamento da Educação, onde o acompanhamento diário de prazos e demandas das unidades escolares e setores internos sofria com a falta de padronização, atrasos e perda de informações causadas pelo uso de canais de comunicação informais (como o WhatsApp).

A aplicação centraliza a coleta de indicadores através de conexões de rede seguras, implementando uma interface gráfica na ponta (unidades escolares e setores) e um consolidador automatizado na central.

---

## 1. Documentação do protocolo 

Para reger a comunicação entre o cliente e o servidor de forma padronizada e segura, foi desenvolvido um protocolo na Camada de Aplicação denominado **PRMD** (*Protocolo de Relatório de Monitoramento de Demandas*). O PRMD opera diretamente sobre a camada de transporte utilizando sockets TCP.

### Máquina de estados lógicos
Tanto a central quanto as unidades locais obedecem a uma transição de estados:
1. **`DESCONECTADO`**: Estado inicial de repouso do cliente. O utilizador pode interagir com a interface e registar dados, mas não há canal de rede ativo.
2. **`AGUARDANDO_AUTENTICACAO`**: O socket TCP foi aberto. O servidor aguarda as credenciais válidas do cliente e bloqueia qualquer envio de dados prematuro.
3. **`PRONTO_PARA_DADOS`**: A credencial foi validada com sucesso pelo servidor. O canal está liberado para a transmissão dos payloads de indicadores.
4. **`CONCLUIDO`**: O lote de dados foi recebido, o recibo de confirmação foi emitido e os recursos de rede são liberados com o fecho do canal.

### Dicionário de mensagens e comandos
O PRMD utiliza mensagens textuais estritas com codificação UTF-8, estruturadas através do delimitador caractere pipe (`|`):

| Origem | Mensagem Padrão | Propósito Técnico |
| :--- | :--- | :--- |
| **Cliente** | `'AUTH|senha'` | Inicia a tentativa de identificação e validação com a central. |
| **Servidor** | `'200_AUTH_OK'` | Confirma a autenticidade e altera o estado para prontidão de dados. |
| **Servidor** | `'401_UNAUTH'` | Rejeita a credencial incorreta e encerra o socket de forma imediata. |
| **Cliente** | `'DATA|json_string'` | Transmite o lote estruturado de relatórios persistidos no buffer. |
| **Servidor** | `'201_DATA_ACK'` | Recibo oficial emitido após guardar os dados com sucesso. |
| **Servidor** | `'400_BAD_REQ'` | Alerta de pacote malformado ou erro na descodificação do payload. |

### Eventos e mecanismo de resiliência 
O maior diferencial do protocolo PRMD é o tratamento de falhas em conexões intermitentes, comum em regiões isoladas ou polos escolares com oscilação geográfica de sinal:
* **Evento de Queda de Conexão:** Ao registar uma demanda sem internet, o cliente interceta a falha de rede silenciosamente e aciona a rotina offline, gravando o payload localmente num ficheiro JSON.
* **O Acordo de Confiança:** O cliente **nunca** apaga os relatórios locais imediatamente após o envio. O evento de limpeza do buffer só ocorre no exato milissegundo em que o cliente recebe a resposta `'201_DATA_ACK'` da central, blindando o sistema contra perda de dados ou apagões de energia no meio da transmissão.

---

## 2. Documentação da Aplicação 

### Propósito do sistema
O SIMD substitui o fluxo de mensagens de texto soltas por um formulário visual obrigatório e padronizado. Ele extrai a carga de trabalho manual da coordenação central: em vez de ler dezenas de mensagens no WhatsApp e tabelar manualmente, o servidor atua como um funil automático que consolida as transmissões diretamente num ficheiro unificado compatível com o Google Planilhas.

### Por que foi utilizado o TCP nessa aplicação?
A camada de transporte utiliza obrigatoriamente **Sockets TCP** (`socket.SOCK_STREAM`). A justificativa arquitetural baseia-se na criticidade dos dados de governança pública. Enquanto o protocolo UDP prioriza a velocidade e tolera a perda de pacotes (como em transmissões de vídeo), o TCP garante:
1. **Entrega Confiável:** Certeza absoluta de que cada caractere do relatório chegará ao destino através de retransmissões automáticas ao nível de transporte.
2. **Controlo de Ordenação:** Garante que os pacotes de dados não cheguem invertidos ou corrompidos, invalidando o formato JSON da Camada de Aplicação.

### Requisitos mínimos de funcionamento
* **Sistema Operativo:** Linux (Ubuntu/WSL) ou Windows com suporte a Python 3.
* **Dependências Nativas:** Biblioteca `socket`, `json`, `csv`, `os` e `tkinter`.
* **Ambiente Linux (WSL):** Necessário instalar o suporte gráfico do Tkinter executando o comando:
  ```bash
  sudo apt update && sudo apt install python3-tk


### Como executar a aplicação:
1. Abra dois terminais divididos. No primeiro, inicie o receptor de dados executando o comando:
```bash
python3 servidor.py

---

2. No segundo terminal, execute a interface visual do usuário:
```bash
python3 cliente.py
