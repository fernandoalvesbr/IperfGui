## 🚀 Visão Geral do Sistema

O **Wireless Network Tester** é uma aplicação desktop que atua como uma **interface gráfica (GUI) oficial/alternativa para o iperf3**. Desenvolvida para auxiliar administradores de rede, equipes de suporte técnico e engenheiros, a ferramenta elimina a necessidade de uso direto via linha de comando, facilitando a medição de largura de banda de links de dados (Upload, Download e Bidirecional).

---

## ⚙️ Principais Funcionalidades

### 1. 🖥️ Dados do Servidor
Configuração do endpoint remoto onde o servidor `iperf3` está rodando e escutando conexões.
* **IP/Host:** Endereço IP ou domínio do servidor (ex: `200.152.98.6`).
* **Porta:** Porta de escuta do servidor (padrão do iperf3: `5201`).

### 2. 🎛️ Configurações do Teste
Controle total sobre os parâmetros suportados pelo motor do `iperf3`:
* **Protocolo:**
  * `TCP`: Medição de largura de banda confiável orientada à conexão.
  * `UDP`: Avaliação de perda de pacotes, *jitter* e estabilidade do link.
* **Direção do Tráfego:**
  * `Upload`: Envio de dados do cliente para o servidor.
  * `Download`: Recepção de dados do servidor para o cliente.
  * `Ambos`: Teste simultâneo nas duas direções (*bidirectional*).
* **Parâmetros Avançados (Flags do iperf3):**
  * **Threads (-P):** Número de fluxos paralelos utilizados no teste.
  * **Tempo (seg):** Duração da execução do teste em segundos.
  * **Banda UDP:** Taxa de transferência limite/alvo para pacotes UDP.

### 3. 🎮 Controles de Execução e Visualização
* **Iniciar (`ENTER`):** Executa o comando `iperf3` com os parâmetros configurados.
* **Parar:** Encerra o processo do teste de forma segura.
* **Limpar Gráfico:** Reseta a área de plotagem dos resultados.
* **Gráfico em Tempo Real:** Acompanhamento visual da taxa de transferência em Megabits por segundo (Mbps).
* **Console de Logs:** Exibição em tempo real da saída padrão (*stdout*) gerada pelo `iperf3`.

---

## 🛠️ Especificações Técnicas

* **Engine:** `iperf3`
* **Arquitetura:** Cliente (GUI) / Servidor
* **Interface:** Tema escuro (*Dark Mode*) otimizado para operações de rede e NOCs.
* **Unidade de Medida:** Mbps (Megabits por segundo).

---

## 💡 Como Usar

1. Certifique-se de ter um servidor `iperf3` ativo no destino.
2. Insira o **IP/Host** e a **Porta** do servidor.
3. Selecione o **Protocolo** e a **Direção** desejados.
4. Ajuste as **Threads** e o **Tempo** conforme necessário.
5. Pressione `ENTER` ou clique em **INICIAR** para disparar os testes.

### Modo servidor

Selecione a aba **Modo servidor** para receber testes neste computador. O terminal
mostra o IP local ao abrir a aplicação. Ajuste a **Porta** se necessário (padrão
**5201**) e clique em **INICIAR SERVIDOR**. O mesmo botão passa a **PARAR SERVIDOR**.
A porta fica bloqueada enquanto o servidor está em execução.

A saída do iperf3 aparece no terminal e o gráfico acompanha a largura de banda em
Mbps, somando os fluxos paralelos e separando TX/RX nos testes bidirecionais.
O servidor continua disponível para novos testes até ser parado. A aba **Modo
cliente** mantém os controles existentes; ENTER atua na aba selecionada.

### Histórico de IPs no cliente

O campo **IP/Host** permite digitar ou selecionar um endereço pela seta. Ao iniciar
um teste, o endereço é salvo no histórico dos últimos 30 IPs/hosts, sem duplicatas.
O histórico é mantido entre aberturas e o endereço mais recente fica selecionado.
O IP padrão `200.152.98.6` aparece sempre no início da lista; os demais seguem
a ordem dos mais recentes, sem repetir o padrão.
Os dados ficam em `~/.config/IperfGui/historico_ips.json` (ou `XDG_CONFIG_HOME`)
no Linux e em `%APPDATA%/IperfGui/historico_ips.json` no Windows.

### Atualização do script

Ao abrir, o aplicativo verifica em segundo plano se há uma versão mais recente
na branch `main` de `fernandoalvesbr/IperfGui`. Também é possível usar o botão
**Verificar atualizações**, disponível nas duas abas. Sem internet, o aplicativo
continua funcionando normalmente.

Após sua confirmação em **Atualizar e reiniciar**, o aplicativo valida a sintaxe
do novo script, salva o anterior em `iperf3gui.py.bak`, substitui o arquivo e
reinicia com o mesmo Python. Pare qualquer teste ou servidor antes de atualizar.
O histórico de IPs permanece na pasta de configurações do usuário.

Para publicar uma atualização, aumente `APP_VERSION` (por exemplo, de `(1, 1, 0)`
para `(1, 1, 1)`) e envie o script para `main`. Alterações apenas no README não
disparam atualização. A primeira instalação deste recurso exige copiar o script
novo ou executar `git pull`. Dependências novas ainda precisam ser instaladas
separadamente. A pasta do script precisa permitir escrita.
