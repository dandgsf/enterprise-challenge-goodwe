# Revisão Sênior do Tópico 1

## Diagnóstico

A primeira versão do Tópico 1 estava correta em relação ao enunciado, mas ainda genérica. Ela explicava bem o problema de recarga compartilhada, porém poderia servir para quase qualquer projeto de carregador elétrico. Depois da leitura do transcript da mentoria GoodWe/FIAP, ficou claro que o documento precisava ser mais específico.

O ponto principal da revisão foi transformar o texto de "pesquisa sobre recarga compartilhada" em "pesquisa aplicada ao cenário real GoodWe/FIAP".

## Lacunas Encontradas

| Lacuna | Risco | Correção aplicada |
| --- | --- | --- |
| Pouca referência ao carregador real da FIAP | A solução pareceria genérica e distante da operação real. | Inclusão do modelo GW7K HC20/HCA G2, 7 kW, CA. |
| Suposição implícita de API | A arquitetura futura poderia prometer uma integração indisponível nesta sprint. | Registro explícito de que a API pública não será liberada para os alunos nesta etapa. |
| OCPP tratado de forma muito ampla | Poderia sugerir que o carregador GoodWe usa OCPP. | Ajuste para indicar que OCPP é referência de mercado, mas o HCA G2 usa Modbus. |
| Sense Plus pouco explorado | O projeto deixaria passar a principal fonte prática de dados. | Inclusão do Sense Plus como fonte de histórico, potência, energia, status e relatórios. |
| Limite de RFID ausente | O problema de escala em condomínios ficaria fraco. | Inclusão do limite de até 10 cartões RFID como dor de escala. |
| MVP ainda amplo | A solução poderia tentar resolver tudo ao mesmo tempo. | Recomendação de MVP focado em rateio/cobrança a partir de relatórios do Sense Plus. |

## Decisão de Produto

O MVP mais forte para a Sprint 02 deve ser:

> Importar relatórios de sessões do Sense Plus, organizar os dados por usuário/unidade/RFID, calcular consumo e rateio, gerar relatório mensal e aplicar inteligência para detectar anomalias, horários de pico e padrões de demanda.

Essa escolha é melhor do que começar pelo controle dinâmico de demanda porque:

- não depende de API pública;
- pode usar CSV, Excel, PDF ou dados simulados no mesmo formato dos relatórios;
- resolve diretamente a dor de condomínios e ambientes compartilhados;
- cria uma base de dados útil para IA na próxima sprint;
- respeita as limitações reais do carregador instalado na FIAP.

## Veredito

Após a revisão, o Tópico 1 deixou de ser "água com açúcar". Ele agora tem:

- contexto de mercado;
- problema operacional claro;
- conexão com dados reais da FIAP;
- restrições técnicas assumidas;
- benchmark de mercado;
- leitura crítica das lacunas da GoodWe/Sense Plus;
- recomendação objetiva de MVP.

