# Revisão Sênior do Tópico 1

## Diagnóstico

A primeira versão do Tópico 1 estava correta em relação ao enunciado, mas ainda genérica. Ela explicava bem o problema de recarga compartilhada, porém poderia servir para quase qualquer projeto de carregador elétrico. Depois da leitura do transcript da mentoria GoodWe/FIAP, ficou claro que o documento precisava ser mais específico.

O ponto principal da revisão foi transformar o texto de "pesquisa sobre recarga compartilhada" em "pesquisa aplicada ao cenário real GoodWe/FIAP". Após a validação do SEMS Portal e a evolução da proposta, o texto também passou a defender o EV ChargeOps como uma plataforma de **governança energética**, não apenas como um sistema de rateio.

## Lacunas Encontradas

| Lacuna | Risco | Correção aplicada |
| --- | --- | --- |
| Pouca referência ao carregador real da FIAP | A solução pareceria genérica e distante da operação real. | Inclusão do modelo GW7K HC20/HCA G2, 7 kW, CA. |
| Suposição implícita de API | A arquitetura futura poderia prometer uma integração indisponível nesta sprint. | Registro explícito de que a API pública não será liberada para os alunos nesta etapa. |
| OCPP tratado de forma muito ampla | Poderia sugerir que o carregador GoodWe usa OCPP. | Ajuste para indicar que OCPP é referência de mercado, mas o HCA G2 usa Modbus. |
| Sense Plus pouco explorado | O projeto deixaria passar a principal fonte prática de dados. | Inclusão do Sense Plus como fonte de histórico, potência, energia, status e relatórios. |
| Limite de RFID ausente | O problema de escala em condomínios ficaria fraco. | Inclusão do limite de até 10 cartões RFID como dor de escala. |
| MVP ainda amplo | A solução poderia tentar resolver tudo ao mesmo tempo. | Recomendação de MVP focado em rateio/cobrança com sessões reais quando confirmadas e dados SEMS como contexto energético. |
| IA ainda muito operacional | A proposta poderia parecer "mais do mesmo", limitada a painel, fatura e alerta. | Inclusão de IA para economia energética, redução de pico, melhor horário de recarga e pré-viabilidade solar. |

## Decisão de Produto

O MVP mais forte para a Sprint 02 deve ser:

> Importar dados energéticos disponíveis no SEMS/Sense Plus, integrar relatórios reais de sessões quando a exportação do carregador for confirmada, organizar os dados por usuário/unidade/RFID quando esses campos existirem, calcular consumo e rateio, gerar relatório mensal e aplicar IA para detectar anomalias, prever demanda e recomendar economia energética para o condomínio/local.

Essa escolha é melhor do que começar pelo controle dinâmico de demanda porque:

- não depende de API pública;
- pode usar dados SEMS de planta, CSV/Excel/PDF quando confirmados e dados simulados no formato esperado para sessões;
- resolve diretamente a dor de condomínios e ambientes compartilhados;
- cria uma base de dados útil para IA de rateio, demanda e economia;
- respeita as limitações reais do carregador instalado na FIAP.

## Veredito

Após a revisão, o Tópico 1 deixou de ser "água com açúcar". Ele agora tem:

- contexto de mercado;
- problema operacional claro;
- conexão com dados reais da FIAP;
- restrições técnicas assumidas;
- benchmark de mercado;
- leitura crítica das lacunas da GoodWe/Sense Plus;
- recomendação objetiva de MVP;
- proposta menos comum, com IA voltada à redução de gasto energético local.

## Complemento Após Validação do SEMS Portal

Em 20/06/2026, foi feita uma inspeção visual do SEMS Portal web. A tela observada mostrou dados de planta, geração fotovoltaica, bateria, renda, curvas de potência, estatísticas energéticas e relatórios por inversor/indicador.

Ponto crítico: nessa navegação web, não foi observada uma tela explícita com sessões do carregador, RFID ou usuário. Portanto, a documentação foi ajustada para não prometer que o SEMS web, sozinho, fornece a base completa de rateio.

A decisão de MVP ficou mais precisa:

> Usar dados agregados do SEMS para governança energética e usar sessões reais somente quando a exportação do carregador for confirmada. Até lá, implementar o motor de rateio com dataset simulado, criar recomendações de economia com dados de planta e manter a arquitetura preparada para receber a fonte real.

## Veredito Atualizado

A proposta atual é mais forte porque muda a pergunta do produto.

Antes, a pergunta era:

> Quanto cada usuário deve pagar pela recarga?

Agora, a pergunta passa a ser:

> Como operar recarga compartilhada com cobrança justa e menor gasto energético para o condomínio/local?

Essa mudança reduz o risco de parecer "mais do mesmo". Rateio e fatura continuam necessários, mas o diferencial passa a ser a IA como apoio à decisão: reduzir pico, sugerir janelas de recarga, aproveitar melhor energia solar e indicar quando vale estudar placas solares ou expansão de infraestrutura.
