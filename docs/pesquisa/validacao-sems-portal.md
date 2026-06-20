# Validação Visual do SEMS Portal

## Objetivo

Este documento registra a inspeção visual feita no **SEMS Portal/Sense Plus web** em 20/06/2026, usando a aba aberta no Comet Browser. O objetivo foi verificar quais dados aparecem de fato na plataforma antes de prometer uma integração ou relatório que talvez não exista no acesso disponível ao grupo.

Essa validação não substitui documentação oficial da GoodWe nem o teste com exportações reais, mas ajuda a deixar a proposta tecnicamente honesta.

## Ambiente Observado

| Item | Observado |
| --- | --- |
| Portal | `semsportal.com` |
| Tela principal | `Plant Status` |
| Planta | `LAB FIAP Eco Smart Home` |
| Status visível | `Offline` |
| Criação da planta | `07.01.2025` |
| Classificação | `Battery Storage` |
| Capacidade FV | `6.00 kW` |
| Capacidade de bateria | `0 kWh` |
| Localização exibida | Campus FIAP Cambuci, São Paulo |

## Dados Visíveis no Dashboard da Planta

Na tela `Plant Status`, o SEMS exibiu dados agregados da planta, com foco em geração fotovoltaica, bateria, rede e consumo.

| Bloco | Dados observados |
| --- | --- |
| Indicador instantâneo | `PV Power` em W, exibindo 540 W no momento da inspeção |
| Bateria | indicador visual em 100%, com estado `Discharging` |
| Geração do dia | `PV Generation Today`, exibindo 4.10 kWh |
| Receita/renda do dia | `Income Today`, exibindo 4.10 BRL |
| Geração total | `Total Generation`, exibindo 3769.60 kWh |
| Receita/renda total | `Total Income`, exibindo 3769.60 BRL |
| Clima | previsão meteorológica por dia |
| Fluxo de energia | diagrama de fluxo entre FV, casa/carga, rede e bateria |

## Abas Analíticas Observadas

### Power

A aba `Power` mostra curvas ao longo do dia. A legenda visível inclui:

- `PV(W)`;
- `Battery(W)`;
- `Grid(W)`;
- `Load(W)`;
- `Genset Power(W)`;
- `Micro-grid Power(W)`.

Também há seleção de data, com navegação por dia.

### Generation & Income

A aba `Generation & Income` mostra gráficos por:

- `Day`;
- `Month`;
- `Year`.

Indicadores observados:

- `PV(kWh)`;
- `Genset Generation(kWh)`;
- `Micro-grid Generation(kWh)`;
- `Income (BRL)`.

Na visualização observada, o painel exibiu geração e renda agregadas da planta. Isso é útil para contexto energético, mas não equivale a relatório de sessão de recarga por usuário.

### Energy Statistics

A aba `Energy Statistics` exibe dois blocos principais:

- `AC Output`;
- `Load Consumption`.

Na captura observada, o painel mostrou distribuição entre:

- `In-house`;
- `Feed-in`;
- `Grid`;
- `PV+BAT.`;
- `Generator`;
- `Micro-grid`.

Exemplo observado:

- `Feed-in (100%)`: 3.10 kWh;
- `In-house (0%)`: 0.00 kWh;
- `Grid (100%)`: 0.10 kWh;
- `PV+BAT. (0%)`: 0.00 kWh;
- `Generator (0%)`: 0.00 kWh;
- `Micro-grid (0%)`: 0.00 kWh.

## Tela de Reports Observada

Ao abrir `Reports`, a plataforma mostrou a tela `Data Selection`.

Campos e opções visíveis:

| Área | Opções observadas |
| --- | --- |
| Busca | `Plant/SN`, `Location`, campo `Please enter the plant/SN` |
| Tipo de dado | `Real-time parameters` e `Energy Analysis` |
| Período | intervalo de data/hora |
| Formato de saída | `Excel` ou `Curve` |
| Seleção de equipamento | área `Inverter Selection` |
| Equipamento selecionado | área `Inverter` |
| Indicadores | área `Indicator`, com `Select All` e `Clear All` |

Ponto crítico: na tela observada, o relatório é estruturado em torno de **planta, inversor e indicadores de energia**, não em torno de **sessões de carregador, RFID ou usuário**.

## Tela de Management Observada

Em `Management`, o menu lateral mostrou:

- `Plants`;
- `Devices`;
- `Operation Records`;
- `Warranty`.

Nas telas visíveis de `Plants` e `Devices`, a listagem retornou `No Data` no estado/filtragem observado. A tela de `Devices` exibia colunas como:

- `Plant`;
- `Classification`;
- `Capacity`;
- `Creation Date`.

Não foi observada, nessa navegação visual, uma lista explícita do carregador HCA G2, sessões de recarga ou credenciais RFID.

## Conclusão Técnica

A validação visual fortalece uma decisão importante:

> O SEMS Portal web, no acesso observado, comprova dados energéticos agregados da planta, mas ainda não comprova acesso direto a sessões de recarga do carregador por usuário/RFID.

Isso significa que a solução não deve prometer que o SEMS web, sozinho, entrega todos os campos necessários para rateio individual. A documentação e a Sprint 2 devem trabalhar com três cenários:

1. **Cenário confirmado agora:** importação ou consulta de dados agregados de energia da planta, úteis para contexto energético, gráficos e validação de consumo geral.
2. **Cenário a confirmar:** exportação de sessões do carregador pelo Sense Plus app, por relatório específico do carregador ou por acesso liberado pela GoodWe/FIAP.
3. **Cenário de prototipação:** uso de dataset simulado com estrutura esperada de sessão para implementar e testar rateio, IA e auditoria até que os relatórios reais sejam disponibilizados.

## Impacto na Solução

O EV ChargeOps continua fazendo sentido, mas a arquitetura precisa ser mais precisa:

- não depender da API GoodWe;
- não assumir que o SEMS web já fornece sessões de carregador;
- criar adaptadores separados para `sems_energia_planta` e `sessoes_recarga`;
- manter dataset simulado para a Sprint 2;
- validar exportações reais antes de afirmar suporte a CSV/PDF/Excel de sessão;
- usar os dados energéticos agregados do SEMS como contexto para IA, demanda e comparação, não como base única do rateio por usuário.

Essa postura evita uma falsa solução e torna o projeto mais forte perante avaliação técnica.
