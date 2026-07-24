Documentação Técnica: Aplicativo de Teste de Largura de Banda
1. Visão Geral do Sistema
O aplicativo em questão é uma interface gráfica (GUI) desenvolvida para testes de desempenho de rede, atuando como um cliente para ferramentas de medição de largura de banda (tipicamente baseadas no iperf3). Ele permite que administradores de rede e suporte técnico avaliem a velocidade de Upload, Download ou tráfego bidirecional (Ambos) entre a estação de trabalho e um servidor remoto.

2. Componentes da Interface (UI) e Funcionalidades
A. Dados do Servidor
Configuração do endpoint remoto onde o serviço de testes está escutando.

IP/Host: Campo de entrada para o endereço IP ou domínio do servidor de testes (ex: 200.152.98.6).

Porta: Porta de comunicação utilizada pelo servidor (padrão comum: 5201).

B. Configurações do Teste
Parâmetros que definem o comportamento e o tipo de tráfego gerado durante a execução.

Protocolo:

TCP: Realiza testes orientados à conexão, ideais para medir a largura de banda máxima confiável.

UDP: Realiza testes sem conexão, úteis para avaliar perda de pacotes, jitter e latência sob uma taxa de bits específica.

Direção:

Upload: Envia dados do cliente para o servidor.

Download: Recebe dados do servidor para o cliente.

Ambos: Executa testes em ambas as direções (modo bi-direcional).

Parâmetros Avançados:

Threads (-P): Número de fluxos paralelos utilizados para o teste (configurado para 1 na imagem).

Tempo (seg): Duração de cada execução de teste em segundos (configurado para 10).

Banda UDP: Taxa de transferência alvo para testes UDP (configurada para 100M).

C. Controles de Execução
INICIAR (ENTER): Botão verde para iniciar o teste com base nos parâmetros configurados. Atalho via teclado: tecla ENTER.

PARAR: Botão vermelho para interromper um teste em andamento.

LIMPAR GRÁFICO: Botão cinza para resetar os dados exibidos na área de visualização.

D. Visualização de Dados
Comparativo de Largura de Banda (Mbps): Gráfico cartesiano em tempo real que exibe a velocidade em função do tempo ou amostras.

Console de Saída (Log): Área inferior preta destinada à exibição de logs textuais, status de conexão e resultados brutos retornados pela engine de teste.

3. Especificações Técnicas e Requisitos Operacionais
Arquitetura: Cliente-Servidor.

Plataforma da GUI: Aplicação Desktop baseada em tema escuro (Dark Mode), otimizada para legibilidade em ambientes corporativos ou centros de operações de rede (NOC).

Indicadores de Desempenho: Medições em Megabits por segundo (Mbps).
