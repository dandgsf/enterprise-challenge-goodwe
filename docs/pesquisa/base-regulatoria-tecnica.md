# Frente 2 - Base Regulatória e Técnica

## Objetivo desta Frente

Esta frente responde a uma pergunta prática: **o EV ChargeOps pode funcionar no mundo real, respeitando regra regulatória, limite técnico do carregador GoodWe e a forma como os dados realmente chegam até a equipe?**

O ponto mais importante da análise é não prometer uma integração que ainda não existe para os alunos. O enunciado cita a API GoodWe/SEMS como fonte possível de dados, mas a mentoria esclareceu que a API para carregadores está em desenvolvimento e **não será liberada para os alunos nesta etapa**. Por isso, a arquitetura da Sprint 1 deve tratar a API como evolução futura, e não como dependência do MVP.

O caminho mais realista para a Sprint 2 é:

1. acessar a planta `labrifiap eco smart home` no Sense Plus;
2. visualizar o carregador **GW7K HC20/HCA G2**;
3. exportar ou consultar relatórios de sessões, conforme acesso disponível;
4. importar esses dados no EV ChargeOps;
5. calcular consumo, rateio, alertas e indicadores.

## Premissas Vindas da Mentoria GoodWe/FIAP

| Tema | O que foi esclarecido | Impacto no projeto |
| --- | --- | --- |
| Equipamento base | GoodWe GW7K HC20, linha HCA G2, geração 2, 7 kW, corrente alternada. | A solução deve ser pensada para um carregador AC residencial/semi-compartilhado, não para eletroposto DC de alta potência. |
| Plataforma operacional | Sense Plus, com versão web e app. Solar Go é mais voltado ao comissionamento local. | O Sense Plus vira a fonte prática de histórico, potência, energia, status e relatórios. |
| API | A API para carregadores está em desenvolvimento, mas não será liberada para os alunos nesta fase. | O MVP não deve depender de API. Deve aceitar CSV, Excel, PDF ou dados simulados no mesmo formato dos relatórios. |
| Protocolo | O carregador trabalha com Modbus, não OCPP. | Não se deve vender a ideia como integração pronta com plataformas OCPP de cobrança. |
| RFID | O carregador vem com 2 cartões e suporta até 10 cartões configuráveis. | O limite de identificação nativa é uma dor real para condomínios maiores. |
| Cobrança | Não há cobrança automática integrada ao carregador atual. | O cálculo de rateio/cobrança é o coração da solução, não um acessório. |
| Controle dinâmico | Pode ser configurado com smart meter T6 para limitar corrente/demanda. | É um diferencial futuro, mas depende de validação técnica e não deve ser o primeiro MVP. |

## Recorte Regulatório

O enunciado exige atenção à **Resolução Normativa ANEEL nº 1.000/2021**, principalmente em três pontos: exploração comercial da recarga, comunicação prévia à distribuidora e exigência de protocolos abertos de comunicação para equipamentos que não sejam de uso privado exclusivo.

Como esta sprint é de pesquisa e documentação, a decisão mais responsável é transformar esses pontos em requisitos de conformidade para a Sprint 2.

### 1. Exploração Comercial da Recarga

Quando a recarga deixa de ser apenas uso próprio e passa a envolver cobrança de terceiros, ela entra em uma lógica comercial ou coletiva. Em condomínio, isso pode aparecer como:

- cobrança direta por kWh consumido;
- taxa mensal para usuários habilitados;
- rateio no boleto condominial;
- cobrança por tempo conectado;
- combinação entre consumo medido e custos comuns.

Para o EV ChargeOps, a consequência é clara: **a plataforma precisa separar consumo individual de custos administrativos ou comuns**. Misturar tudo em uma única linha de cobrança deixa o modelo frágil, difícil de auditar e potencialmente injusto.

Na prática, a fatura deve mostrar:

- energia consumida em kWh;
- tarifa usada no cálculo;
- custo variável de energia;
- custos comuns rateados, quando aprovados pelo condomínio;
- ajustes, descontos, contestação ou exceção;
- regra aplicada no mês.

### 2. Comunicação Prévia à Distribuidora

O enunciado aponta a necessidade de comunicação prévia à distribuidora em determinados contextos de operação. Para o projeto, isso não significa que o protótipo da Sprint 2 precise conversar com a distribuidora, mas significa que a solução deve deixar rastreável:

- local da instalação;
- unidade consumidora ou condomínio responsável;
- potência instalada do carregador;
- quantidade de carregadores;
- modo de uso: privado, compartilhado interno ou comercial;
- existência de medidor dedicado ou medição interna;
- política de cobrança/rateio adotada.

Esse registro ajuda o gestor a comprovar que a operação não foi improvisada. Também prepara a solução para crescer sem virar uma planilha solta.

### 3. Protocolos Abertos de Comunicação

O enunciado pede atenção à exigência de protocolos abertos para equipamentos que não sejam exclusivos de uso privado. Esse ponto é sensível porque a mentoria informou que o HCA G2 usa **Modbus** e não **OCPP**.

OCPP é uma referência forte de mercado porque padroniza a comunicação entre estações de recarga e sistemas centrais de gestão. A própria Open Charge Alliance define o OCPP como protocolo aberto global entre estações de carregamento e sistemas de gerenciamento, com foco em interoperabilidade, escala e menor dependência de sistemas proprietários.

Para o EV ChargeOps, a leitura sênior é:

- **não declarar que o HCA G2 é compatível com OCPP**, porque isso contraria a mentoria;
- **não construir o MVP dependendo de OCPP**, porque o equipamento real usa Modbus;
- **documentar a lacuna de interoperabilidade** como risco técnico;
- **prever uma camada adaptadora**, para que no futuro a plataforma aceite dados por arquivo, API GoodWe, Modbus validado ou integração com equipamentos OCPP.

Essa postura é mais forte do que tentar esconder a limitação. Ela mostra maturidade técnica.

## LGPD e Dados Pessoais

Mesmo que a LGPD não tenha sido o foco do enunciado, ela aparece naturalmente no projeto. Uma sessão de recarga pode revelar hábitos de uma pessoa: horário em que chega, frequência de uso, volume de energia consumido, veículo provável e unidade residencial.

Portanto, a Sprint 2 deve tratar dados de sessão como dados sensíveis do ponto de vista operacional, ainda que nem todos sejam dados pessoais sensíveis na definição legal.

Requisitos mínimos:

- associar RFID a usuário/unidade com controle de acesso;
- exibir para cada usuário apenas suas próprias sessões;
- exibir para o gestor dados agregados e auditáveis;
- registrar alterações manuais em trilha de auditoria;
- evitar publicar IDs reais de RFID em prints ou datasets públicos;
- usar dados simulados no repositório quando os dados reais da FIAP não puderem ser publicados.

## Carregador GoodWe HCA G2 e Interfaces Técnicas

| Interface | O que permite | Como o EV ChargeOps deve usar |
| --- | --- | --- |
| RS-485/Modbus | Comunicação técnica com equipamentos compatíveis, medidores, inversores, baterias ou smart meter. | Tratar como caminho futuro para leitura técnica validada e controle de demanda. Não assumir integração direta sem documentação de registradores. |
| LAN | Conectividade por rede local para monitoramento e envio de dados ao ecossistema GoodWe. | Apoiar a disponibilidade do Sense Plus e reduzir dependência de sinal Wi-Fi. |
| Wi-Fi | Conexão do carregador à internet/plataforma de monitoramento. | Fonte indireta para que o Sense Plus receba histórico e status. |
| Bluetooth | Configuração local próxima ao equipamento, especialmente via Solar Go. | Usar para comissionamento e diagnóstico local, não como canal principal de dados do MVP. |
| RFID | Autorização local de usuários por cartão. | Mapear RFID para usuário/unidade no EV ChargeOps. Tratar o limite de até 10 cartões como risco de escala. |
| Sense Plus | Visualização remota de histórico, potência, energia, status, modos e relatórios. | Fonte operacional principal para importação de relatórios e conferência mensal. |
| Solar Go | Aplicativo de comissionamento/configuração local. | Apoiar configuração inicial, pareamento e diagnóstico; não é a base da fatura. |

## GoodWe API/SEMS: Tensão Entre Enunciado e Mentoria

O enunciado pede pesquisar a API GoodWe/SEMS e quais dados ela expõe sobre carregador, como status, potência, energia entregue e eventos de sessão. Porém, a mentoria esclareceu que a API dos carregadores ainda não será liberada para os alunos.

Essa diferença deve aparecer claramente no projeto:

| Camada | Decisão |
| --- | --- |
| Sprint 1 | Documentar a API como possibilidade prevista pelo enunciado, mas registrar que ela não está disponível para implementação acadêmica nesta etapa. |
| Sprint 2 MVP | Implementar importação de relatórios exportados do Sense Plus ou arquivos simulados no mesmo formato. |
| Sprint 2 evolução | Criar uma interface de integração com adaptadores: `arquivo`, `sense_plus_export`, `goodwe_api_futura` e `modbus_validado`. |
| Produto futuro | Caso a GoodWe libere documentação e credenciais, substituir parte da importação manual por coleta automatizada. |

Campos esperados para o modelo de dados, independentemente da fonte:

- identificador da sessão;
- data/hora de início;
- data/hora de fim;
- duração;
- energia entregue em kWh;
- potência média ou instantânea;
- corrente;
- status;
- modo de operação;
- RFID ou identificador de usuário;
- carregador;
- falhas ou eventos.

## Opção de Aprofundamento Escolhida: APIs Complementares

Para esta frente, a opção escolhida foi a **Opção C - Mapeamento de APIs complementares**. A escolha faz sentido porque a principal API GoodWe não estará disponível para os alunos nesta etapa. Em vez de travar a solução, o EV ChargeOps pode enriquecer o produto com fontes externas úteis para expansão, benchmark, localização, tarifa e contexto regional.

### APIs Selecionadas

| API | Dados úteis | Uso possível no EV ChargeOps | Cuidado |
| --- | --- | --- | --- |
| Open Charge Map API | Localização de pontos de recarga, comentários, check-ins, fotos e informações de estações. | Comparar disponibilidade de recarga no entorno, mapear concorrência e estimar maturidade da região. | A própria Open Charge Map alerta que os dados vêm de fontes públicas e contribuições, sem garantia de precisão. |
| Google Places API - `evChargeOptions` | Quantidade de conectores, agregação por tipo, potência máxima, disponibilidade e status fora de serviço quando disponível. | Enriquecer mapa externo, comparar estações, apoiar análise de expansão e UX de localização. | Requer chave, custo de uso e respeito às políticas da Google Maps Platform. |
| ANEEL Open Data | Tarifas de energia, TUSD, TE, dados de distribuidoras e conjuntos públicos do setor elétrico. | Apoiar cálculo de custo estimado por distribuidora, simulação de cenário tarifário e contextualização regulatória. | Os dados precisam ser tratados por período, distribuidora, classe e modalidade tarifária. |
| IBGE Localidades API | Estados, municípios, regiões e códigos oficiais. | Padronizar cadastro de endereço, cidade, UF, região e expansão geográfica. | Não substitui dados de rede elétrica; serve para geografia e organização territorial. |

### Como Essas APIs Ajudam de Verdade

Essas APIs não são enfeite. Elas ajudam a transformar o EV ChargeOps em uma plataforma mais defensável:

- **Open Charge Map e Google Places** mostram o ecossistema ao redor: se há muitos carregadores próximos, o condomínio pode querer diferenciação por conveniência e transparência; se há poucos, a infraestrutura interna ganha valor estratégico.
- **ANEEL Open Data** aproxima o cálculo de custo do setor elétrico real, em vez de usar uma tarifa fictícia fixa para sempre.
- **IBGE Localidades** evita cadastros bagunçados e permite segmentar expansão por cidade, UF e região.

Para a Sprint 2, a prioridade ainda é importar sessões e calcular rateio. As APIs complementares entram como camada de inteligência e expansão, não como requisito mínimo para o primeiro protótipo.

## Riscos Técnicos e Mitigações

| Risco | Por que importa | Mitigação proposta |
| --- | --- | --- |
| API GoodWe indisponível | Pode impedir automação completa da coleta. | MVP baseado em importação de CSV, Excel, PDF ou dados simulados no layout do Sense Plus. |
| Relatório exportado variar por plataforma | App e web podem oferecer formatos diferentes. | Criar importador tolerante a nomes de colunas e manter dicionário de campos. |
| Ausência de OCPP | Reduz interoperabilidade com plataformas comerciais de cobrança. | Arquitetura com adaptadores e registro explícito de fonte de dados. |
| Limite de 10 RFID | Pode não atender condomínios grandes. | Mapear RFID para usuário/unidade e estudar camada externa de autenticação na evolução. |
| Dados reais não publicáveis | Pode comprometer evidência no repositório. | Usar dataset simulado com estrutura realista e manter dados reais apenas em ambiente controlado. |
| Tarifa elétrica complexa | Cálculo pode variar por distribuidora, modalidade e horário. | Começar com tarifa parametrizável e registrar a regra usada em cada fatura. |

## Decisão Técnica para a Sprint 2

A Frente 2 recomenda a seguinte decisão:

> O EV ChargeOps deve nascer como uma plataforma de importação, normalização e auditoria de sessões do Sense Plus, com arquitetura preparada para API futura, e não como um sistema que depende de uma API ainda indisponível.

Essa decisão torna o projeto mais executável, mais honesto e mais competitivo.

## Checklist de Atendimento ao Enunciado

| Exigência da Frente 2 | Atendido? | Onde aparece |
| --- | --- | --- |
| Considerar RN ANEEL nº 1.000/2021 | Sim | Seção "Recorte Regulatório" |
| Exploração comercial da recarga | Sim | Subseção "Exploração Comercial da Recarga" |
| Comunicação prévia à distribuidora | Sim | Subseção "Comunicação Prévia à Distribuidora" |
| Protocolos abertos de comunicação | Sim | Subseção "Protocolos Abertos de Comunicação" |
| Interfaces GoodWe HCA G2 | Sim | Seção "Carregador GoodWe HCA G2 e Interfaces Técnicas" |
| API GoodWe/SEMS | Sim, com ressalva | Seção "GoodWe API/SEMS: Tensão Entre Enunciado e Mentoria" |
| Escolher aprofundamento | Sim | Opção C - APIs complementares |
| Documentar ao menos duas APIs externas | Sim | Open Charge Map, Google Places, ANEEL Open Data e IBGE |
| Incorporar mentoria GoodWe/FIAP | Sim | Premissas, limitações, API, Sense Plus, Modbus e RFID |

## Fontes Usadas nesta Frente

As fontes completas desta frente estão registradas em `references/fontes.md`.
