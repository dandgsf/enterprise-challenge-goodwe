# Fontes Verificadas

Este arquivo registra as fontes consultadas para a Sprint 01 do Enterprise Challenge 2026 - GoodWe + FIAP.

## Enunciado e Mentoria

- FIAP. `enterprise_challenge_2026_goodwe_fiap.md`. Arquivo local em `1st semester/fase-04/enterprise_challenge_2026_goodwe_fiap.md`.
- Mentoria GoodWe/FIAP. Transcript local anexado em `C:\Users\Usuário\.codex\attachments\d9f898e0-dc63-4039-be76-b7a68971591e\pasted-text.txt`.

Uso no projeto:

- Definição do escopo da Sprint 01.
- Confirmação de que o README é o entregável central do repositório.
- Identificação do termo EV ChargeOps como nome conceitual da solução no enunciado.
- Critérios exigidos para as três frentes.
- Recorte real do desafio: carregador GW7K HC20/HCA G2, 7 kW, Sense Plus, ausência de API pública liberada nesta etapa, comunicação Modbus, ausência de OCPP, limite de RFID, necessidade de trabalhar com relatórios exportados quando disponíveis e oportunidade de usar dados energéticos do SEMS para recomendações de economia.

Observação sênior:

- O enunciado pede estudo de API GoodWe/SEMS, mas a mentoria esclareceu que a API para carregadores não estará disponível para os alunos nesta etapa. Por isso, a documentação trata API como evolução futura e define importação de dados disponíveis, rateio auditável e recomendações energéticas como MVP.

## Mercado Brasileiro de Eletromobilidade

- ABVE - Associação Brasileira do Veículo Elétrico. Página institucional e ABVE Data. Disponível em: https://abve.org.br/
- ABVE. "Produção nacional já impulsiona crescimento recorde de vendas de eletrificados leves no Brasil". Publicado em 16 de junho de 2026. Disponível em: https://abve.org.br/producao-nacional-ja-impulsiona-crescimento-recorde-de-vendas-de-eletrificados-leves-no-brasil/

Uso no projeto:

- Contextualização do crescimento dos veículos eletrificados no Brasil.
- Apoio à relevância de soluções de recarga compartilhada.
- Dados citados pela ABVE sobre maio de 2026: 44.981 eletrificados leves emplacados, 17% de participação no mercado doméstico e crescimento de BEV e PHEV.

## Protocolo e Operação Técnica de Recarga

- Open Charge Alliance. "OCPP: Discover our open standards for future-ready EV charging". Disponível em: https://openchargealliance.org/protocols/open-charge-point-protocol/

Uso no projeto:

- Referência para explicar OCPP como protocolo aberto global entre estações de recarga e sistemas centrais de gestão.
- Comparação com a realidade do projeto GoodWe/FIAP, em que a mentoria informou uso de Modbus e não OCPP.
- Apoio à decisão de criar uma arquitetura com adaptadores, sem prometer integração OCPP no HCA G2.

## GoodWe, Sense Plus e HCA G2

- GoodWe SEMS/Sense Plus. Disponível em: https://semsplus.goodwe.com/
- Mentoria GoodWe/FIAP. Transcript local anexado.
- Inspeção visual autorizada do SEMS Portal no Comet Browser, realizada em 20/06/2026.

Uso no projeto:

- A página do Sense Plus foi usada como referência de plataforma indicada pelo enunciado.
- As informações específicas sobre modelo GW7K HC20/HCA G2, 7 kW, app Sense Plus, Solar Go, Modbus, RFID e ausência de API liberada foram extraídas da mentoria, não inferidas de página pública.
- A inspeção visual do SEMS Portal mostrou dados agregados de planta, geração, renda, curvas de potência, estatísticas energéticas, tela de relatórios por inversor/indicador e telas de gerenciamento. Não foi observada, nessa navegação, tela web explícita de sessões do carregador por RFID/usuário. Esses dados agregados foram usados para justificar a camada de IA voltada à economia energética.

Observação:

- Manual e data sheet oficiais do HCA G2 devem ser baixados pelo grupo no site GoodWe ou fornecidos pela GoodWe/FIAP quando o acesso estiver liberado. A Sprint 2 deve validar registradores Modbus, campos de relatório e limites técnicos diretamente nesses documentos.

## Base Regulatória e Dados Públicos de Energia

- ANEEL Open Data. Portal de Dados Abertos da Agência Nacional de Energia Elétrica. Disponível em: https://dadosabertos.aneel.gov.br/
- ANEEL Open Data. Conjunto "Tarifas de aplicação das distribuidoras de energia elétrica". Disponível a partir do portal de dados abertos.
- ANEEL. Resolução Normativa nº 1.000/2021. Referenciada pelo enunciado local do desafio.

Uso no projeto:

- Apoio à Frente 2 para tarifas, dados de distribuidoras e simulações futuras de custo.
- Construção de requisito de conformidade sobre exploração comercial de recarga, comunicação prévia à distribuidora e protocolos abertos, conforme recorte exigido pelo enunciado.

Observação sênior:

- Para operação real fora do contexto acadêmico, a equipe deve validar o texto consolidado vigente da RN 1.000/2021 no portal oficial da ANEEL e verificar atualizações normativas aplicáveis à cidade/estado da instalação.

## APIs Complementares

- Open Charge Map. "Developing using Open Charge Map data and services". Disponível em: https://openchargemap.org/develop
- Google Places API. REST Resource: Places, campo `evChargeOptions`. Disponível em: https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places
- IBGE. API de Localidades. Disponível em: https://servicodados.ibge.gov.br/api/docs/localidades
- ANEEL Open Data. Disponível em: https://dadosabertos.aneel.gov.br/

Uso no projeto:

- Open Charge Map: localização de pontos de recarga, comentários, check-ins e fotos.
- Google Places: enriquecimento de informações de locais e opções de recarga via `evChargeOptions`.
- IBGE Localidades: padronização de municípios, UF e regiões.
- ANEEL Open Data: tarifas e dados públicos do setor elétrico.

Cuidados:

- Open Charge Map informa que seus dados vêm de fontes públicas e contribuições, sem garantia de precisão.
- Google Places API exige chave, billing e respeito às políticas da Google Maps Platform.
- ANEEL e IBGE exigem tratamento correto de período, localidade, códigos e escopo dos dados.

## Soluções de Mercado

- NeoCharge. "Plataforma de Gestão NeoCharge". Disponível em: https://www.neocharge.com.br/plataforma-gestao-recarga
- NeoCharge. "Monitoramento e Controle de Acesso". Disponível em: https://www.neocharge.com.br/empresa/carregador-carro-eletrico/monitoramento-controle-acesso
- Zaptec. "Zaptec Pro". Disponível em: https://www.zaptec.com/charging-solutions/business-and-commercial/zaptec-pro
- Wallbox. "Pulsar Plus EV Charger". Disponível em: https://wallbox.com/en_us/pulsar-plus-ev-charger
- GoodWe/FIAP. Mentoria de alinhamento do Enterprise Challenge, transcript local anexado.

Uso no projeto:

- Benchmark da Frente 1 - Opção A.
- Identificação de funcionalidades já existentes: cobrança por recarga, controle de acesso, relatórios, status em tempo real, balanceamento de carga, histórico de sessões e monitoramento de energia.
- Identificação de lacunas que o EV ChargeOps pode explorar: rateio auditável, importação de dados disponíveis do SEMS/Sense Plus, relatórios de sessão quando confirmados, IA energética e operacional, recomendação de economia energética e foco em gestão compartilhada brasileira.

## IA e Modelagem

- scikit-learn. `LinearRegression`. Disponível em: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html
- scikit-learn. `IsolationForest`. Disponível em: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html
- scikit-learn. `KMeans`. Disponível em: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html

Uso no projeto:

- Apoio à Frente 3 - Opção B.
- Justificativa técnica para previsão de consumo, detecção de anomalias, agrupamento de perfis de uso e score de oportunidade energética.

## Observações da Mentoria que Afetam o MVP

- API pública para carregadores: mencionada como em desenvolvimento, mas não liberada para os alunos nesta etapa.
- Fonte prática de dados: SEMS/Sense Plus, com visualização de dados da planta e possibilidade de relatórios conforme acesso disponível.
- Validação posterior: o SEMS web observado confirma dados agregados da planta, mas não confirma por si só exportação de sessões de carregador/RFID.
- Equipamento real: GoodWe GW7K HC20, linha HCA G2, 7 kW, CA.
- Identificação: suporte a cartões RFID, com limite nativo de até 10 cartões.
- Comunicação: Modbus; não há OCPP no carregador citado.
- Cobrança: não há cobrança automática integrada no equipamento atual.
- Direcionamento de solução: rateio/cobrança e gestão compartilhada são dores reais; controle de demanda também é relevante, mas depende mais de medidor, configuração e validação técnica. A camada de IA deve recomendar economia, melhor horário de recarga, redução de pico e pré-viabilidade solar sem substituir projeto técnico.
