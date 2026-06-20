# Frente 3 - Arquitetura e IA

## Objetivo desta Frente

Esta frente transforma a pesquisa em uma solução desenhável e implementável. A pergunta agora é:

> Como sair de uma sessão registrada no Sense Plus e chegar a uma fatura justa, auditável e útil para gestão?

A resposta proposta é organizar o EV ChargeOps como uma camada de operação por cima do carregador GoodWe. O carregador faz a recarga. O Sense Plus mostra e exporta os dados. O EV ChargeOps transforma esses dados em controle, rateio, alertas e decisão.

## Tese de Produto

O EV ChargeOps não deve ser apenas um "app do carregador". Ele deve ser um **sistema de gestão da operação compartilhada de recarga**.

Na prática, isso significa três funções centrais:

1. **Ledger de sessões:** cada recarga vira um registro confiável, com origem, usuário, unidade, kWh, duração, status e evidência.
2. **Motor de rateio:** cada sessão entra em uma regra clara de cobrança, separando consumo individual de custos comuns.
3. **Camada de inteligência:** a plataforma identifica pico, anomalia, uso recorrente, ociosidade e tendência de demanda.

Esse posicionamento resolve a dor principal da turma online, citada na mentoria: gestão compartilhada, rateio inteligente e cobrança em condomínios.

## Camadas da Plataforma

| Camada | Componentes | Responsabilidade |
| --- | --- | --- |
| Física | Carregador GoodWe GW7K HC20/HCA G2, veículo elétrico, cartão RFID, smart meter T6 opcional, rede elétrica. | Realizar a recarga, medir energia e gerar eventos técnicos. |
| Conectividade | Wi-Fi, LAN, Sense Plus, Solar Go, Modbus/RS-485 para evolução técnica. | Levar dados do equipamento até a plataforma GoodWe e permitir configuração/monitoramento. |
| Aplicação | Importador de relatórios, normalizador, banco de dados, motor de rateio, motor de IA, auditoria. | Transformar dados brutos em registros, faturas, indicadores e alertas. |
| Apresentação | Painel do gestor, relatório do usuário, tela de fatura, alertas, exportação mensal. | Dar clareza para síndico/gestor e transparência para usuário. |

## Diagrama de Arquitetura

![Arquitetura proposta do EV ChargeOps](../../assets/diagrams/arquitetura-ev-chargeops.svg)

## Fluxo dos Dados: Da Sessão até a Fatura

1. **Sessão acontece no carregador**
   - Usuário conecta o veículo.
   - A recarga é liberada por RFID, app ou modo configurado.
   - O carregador registra energia, duração, potência, status e eventos.

2. **Dados aparecem no SEMS/Sense Plus**
   - O gestor visualiza dados da planta, potência, energia, status e modo de operação.
   - Na validação visual do SEMS web, foram observados dados agregados de planta, geração, renda, curvas de potência e estatísticas energéticas.
   - Sessões do carregador por usuário/RFID ainda precisam ser confirmadas em app, relatório específico ou liberação GoodWe/FIAP.

3. **EV ChargeOps importa o relatório**
   - O arquivo é carregado no sistema.
   - Para dados SEMS de planta, o importador identifica data, potência, geração, consumo, rede, bateria e indicadores energéticos.
   - Para dados de sessão, quando disponíveis, o importador identifica colunas, datas, kWh, status, RFID e carregador.
   - O sistema guarda o arquivo original como evidência.

4. **Dados são normalizados**
   - Datas viram timestamps padronizados.
   - Energia vira número em kWh.
   - RFID é associado a usuário, unidade ou centro de custo quando esse campo existir na fonte.
   - Sessões duplicadas ou incompletas são sinalizadas.

5. **IA e regras verificam qualidade**
   - Regras simples identificam campos faltantes, duração negativa, kWh zero com longa duração e status de falha.
   - Modelos de IA detectam sessões fora do padrão e previsão de horários de pico.

6. **Motor de rateio calcula valores**
   - O consumo individual é calculado por usuário/unidade.
   - Custos comuns são rateados conforme regra aprovada.
   - Exceções são tratadas com justificativa e trilha de auditoria.
   - Se houver apenas dado agregado da planta, o sistema gera análise energética e não fecha rateio individual automaticamente.

7. **Fatura e painel são gerados**
   - Usuário vê consumo, custo, sessões e regra aplicada.
   - Gestor vê total do mês, ranking de uso, inadimplência operacional, alertas e ocupação.

8. **Auditoria fecha o ciclo**
   - Toda alteração manual fica registrada.
   - A fatura pode ser revisada com base no relatório original importado.

## Modelo de Rateio Proposto

O modelo recomendado combina justiça por consumo real com custos comuns transparentes.

### Fórmula Base

```text
consumo_usuario_mes_kwh = soma(kWh das sessões válidas do usuário no mês)

custo_energia_usuario = consumo_usuario_mes_kwh * tarifa_kwh_aplicada

custo_comum_usuario = custo_comum_mensal * regra_rateio_comum

penalidade_ociosidade = max(0, minutos_ociosos - franquia_ociosidade) * tarifa_ociosidade_minuto

ajustes = créditos - débitos validados pelo gestor

fatura_usuario = custo_energia_usuario
                + custo_comum_usuario
                + penalidade_ociosidade
                + ajustes
```

### Variáveis Usadas

| Variável | Explicação |
| --- | --- |
| `kwh_sessao` | Energia entregue em cada sessão. É a base mais justa para consumo individual. |
| `tarifa_kwh_aplicada` | Valor de referência por kWh, definido pelo gestor com base na conta de energia, ANEEL Open Data ou política local. |
| `usuario_id` | Pessoa responsável pela sessão. |
| `unidade_id` | Apartamento, sala, setor ou centro de custo vinculado ao usuário. |
| `rfid_id` | Cartão ou credencial usada para identificar a sessão. |
| `inicio` e `fim` | Horários usados para duração, auditoria e análise de pico. |
| `status_sessao` | Indica se a sessão foi concluída, interrompida, falhou ou precisa de revisão. |
| `custo_comum_mensal` | Manutenção, conectividade, administração, depreciação ou taxa aprovada em assembleia/contrato. |
| `regra_rateio_comum` | Critério de divisão do custo comum: por usuário ativo, por unidade habilitada ou por consumo proporcional. |
| `minutos_ociosos` | Tempo conectado sem carregar após tolerância. Ajuda a liberar vaga. |

### Regra Recomendada para Condomínio

Para o MVP, a regra mais defensável é:

- consumo de energia: cobrado por kWh medido por sessão;
- custo comum: dividido entre usuários ativos no mês ou unidades habilitadas, conforme decisão do condomínio;
- ociosidade: aplicada apenas depois de uma tolerância clara;
- falhas: cobradas apenas pelo kWh efetivamente entregue;
- ajustes manuais: permitidos, mas sempre com justificativa e auditoria.

Essa regra é simples o suficiente para implementar na Sprint 2 e forte o suficiente para explicar em uma assembleia.

## Casos Excepcionais

| Caso | Como tratar |
| --- | --- |
| Sessão interrompida | Cobrar apenas kWh entregue. Marcar sessão como `revisao` se houver falha, queda de comunicação ou dado incompleto. |
| Usuário não carregou no mês | Não cobrar consumo variável. Custo comum só deve ser cobrado se a regra do condomínio incluir unidades habilitadas mesmo sem uso. |
| Dois veículos da mesma unidade | Agregar por unidade para cobrança principal e manter separação por RFID/veículo para transparência. |
| RFID sem usuário vinculado | Bloquear faturamento automático e enviar para conciliação manual. |
| Sessão duplicada no relatório | Manter uma sessão válida, marcar duplicidade e preservar evidência de importação. |
| kWh zero com longa duração | Não cobrar energia, mas sinalizar possível ociosidade, falha ou veículo já carregado. |
| Contestação do usuário | Exibir relatório original, regra aplicada, sessões envolvidas e histórico de alterações. |

## Benchmark de Modelos de Rateio

| Modelo | Como funciona | Vantagem | Limitação | Decisão |
| --- | --- | --- | --- | --- |
| Igualitário entre todas as unidades | Divide o custo total do carregador entre todos os condôminos. | Muito simples. | Injusto para quem não usa e pouco transparente para uso intenso. | Não recomendado como regra principal. |
| Apenas usuários ativos | Divide custos entre quem usou no mês. | Mais justo que dividir entre todos. | Pode distorcer custos fixos quando poucos usam. | Útil para custo comum em fases iniciais. |
| Por kWh medido | Cada usuário paga pelo consumo real. | Mais justo para energia variável. | Não cobre manutenção e custos fixos sozinho. | Recomendado para energia. |
| Híbrido: kWh + custo comum + ociosidade | Combina consumo real, custo fixo transparente e incentivo de liberação da vaga. | Equilibra justiça, sustentabilidade financeira e operação. | Exige explicação clara e sistema auditável. | Modelo adotado. |

## Papel da IA na Solução

A IA precisa resolver problemas reais da operação. Ela não deve aparecer como "chatbot bonito" sem impacto no rateio ou na gestão.

### Abordagem 1 - Previsão de Consumo e Pico

| Item | Definição |
| --- | --- |
| Problema | Gestor não sabe quando o carregador tende a ficar mais demandado nem se a infraestrutura atual será suficiente. |
| Técnica | Regressão simples no MVP e evolução para modelos temporais quando houver histórico maior. |
| Dados necessários | Data, hora, dia da semana, kWh, duração, potência média, usuário/unidade e status da sessão. |
| Saída esperada | Previsão de consumo por dia/semana, horários de pico e recomendação de janela mais barata ou menos congestionada. |
| Impacto | Ajuda a planejar expansão, agenda, limite de corrente e política de preço. |

Na Sprint 2, uma `LinearRegression` ou modelo estatístico simples já é suficiente para demonstrar previsão inicial. A documentação do scikit-learn descreve a regressão linear como um modelo que ajusta coeficientes para minimizar a diferença entre valores observados e previstos.

### Abordagem 2 - Detecção de Anomalias

| Item | Definição |
| --- | --- |
| Problema | Algumas sessões podem indicar erro, falha, uso indevido ou dado inconsistente. |
| Técnica | Regras determinísticas no começo e `IsolationForest` quando houver volume de dados. |
| Dados necessários | kWh, duração, potência média, horário, status, RFID, frequência do usuário e histórico do carregador. |
| Saída esperada | Alertas como "duração alta com kWh baixo", "RFID fora do padrão", "pico incomum" ou "sessão com possível falha". |
| Impacto | Reduz cobrança errada, aumenta confiança e ajuda manutenção. |

O `IsolationForest` é adequado porque calcula pontuação de anomalia para amostras e identifica pontos mais isolados no conjunto de dados.

### Abordagem 3 - Agrupamento de Perfis de Uso

| Item | Definição |
| --- | --- |
| Problema | Usuários têm comportamentos diferentes: alguns carregam pouco e frequentemente, outros fazem recargas longas e raras. |
| Técnica | `KMeans` para segmentar perfis por consumo, frequência, duração média e horário de uso. |
| Dados necessários | Sessões agregadas por usuário/unidade: kWh mensal, número de sessões, horário preferido e tempo médio conectado. |
| Saída esperada | Perfis como "usuário eventual", "usuário frequente noturno", "alto consumo" e "risco de ociosidade". |
| Impacto | Apoia regras de plano, comunicação com usuários e decisões de expansão. |

O `KMeans` é útil porque forma grupos a partir de centroides e atribui rótulos às amostras, facilitando a leitura de padrões.

## Onde a IA Entra no Fluxo

| Momento | IA/Regras aplicadas | Resultado |
| --- | --- | --- |
| Após importação | Validação de campos e detecção de dados ausentes. | Evita que relatório ruim gere cobrança errada. |
| Antes do rateio | Anomalias e revisão de sessões suspeitas. | Impede faturamento automático de casos duvidosos. |
| Fechamento mensal | Previsão de consumo e análise de pico. | Ajuda gestor a ajustar regra, agenda e infraestrutura. |
| Pós-fatura | Agrupamento de perfis de uso. | Permite comunicação e planos mais adequados. |

## Esquema de Dados da Plataforma

### Entidades Principais

| Entidade | Campos principais | Observação |
| --- | --- | --- |
| `usuario` | `usuario_id`, `nome`, `email`, `tipo`, `status` | Pessoa que usa ou administra a plataforma. |
| `unidade` | `unidade_id`, `codigo`, `bloco`, `tipo`, `responsavel_usuario_id` | Apartamento, sala, setor ou centro de custo. |
| `veiculo` | `veiculo_id`, `usuario_id`, `apelido`, `placa_hash`, `modelo`, `capacidade_bateria_kwh` | Placa deve ser protegida ou mascarada em ambiente público. |
| `carregador` | `carregador_id`, `fabricante`, `modelo`, `potencia_kw`, `local`, `fonte_dados` | No caso FIAP: GoodWe GW7K HC20/HCA G2. |
| `rfid_credencial` | `rfid_id`, `codigo_mascarado`, `usuario_id`, `unidade_id`, `status` | Associa cartão a usuário/unidade. |
| `relatorio_importado` | `relatorio_id`, `origem`, `arquivo_nome`, `hash_arquivo`, `importado_em`, `status` | Preserva evidência e auditoria. |
| `sessao_recarga` | `sessao_id`, `relatorio_id`, `carregador_id`, `rfid_id`, `usuario_id`, `unidade_id`, `inicio`, `fim`, `duracao_min`, `energia_kwh`, `potencia_media_kw`, `status`, `modo_operacao` | Registro central do produto. |
| `tarifa` | `tarifa_id`, `nome`, `valor_kwh`, `vigencia_inicio`, `vigencia_fim`, `fonte` | Parametriza cálculo sem fixar valor no código. |
| `regra_rateio` | `regra_id`, `nome`, `criterio_custo_comum`, `franquia_ociosidade_min`, `valor_ociosidade_min` | Permite governança condominial. |
| `fatura` | `fatura_id`, `usuario_id`, `unidade_id`, `mes_referencia`, `total_kwh`, `valor_total`, `status` | Resultado mensal. |
| `item_fatura` | `item_id`, `fatura_id`, `tipo`, `descricao`, `quantidade`, `valor_unitario`, `valor_total`, `sessao_id` | Explica cada cobrança. |
| `alerta_ia` | `alerta_id`, `sessao_id`, `tipo`, `severidade`, `mensagem`, `status` | Traz revisão humana para casos suspeitos. |
| `auditoria_evento` | `evento_id`, `ator_usuario_id`, `entidade`, `entidade_id`, `acao`, `antes`, `depois`, `criado_em` | Registra mudanças manuais. |

### Relacionamentos

| Relação | Tipo | Explicação |
| --- | --- | --- |
| Unidade tem usuários | 1:N | Uma unidade pode ter mais de um usuário autorizado. |
| Usuário tem veículos | 1:N | Um usuário pode cadastrar mais de um veículo. |
| Usuário/unidade tem RFID | 1:N | Um RFID aponta para o responsável operacional da sessão. |
| Carregador tem sessões | 1:N | Cada sessão pertence a um carregador. |
| Relatório importado tem sessões | 1:N | Permite rastrear a origem dos dados. |
| Sessão pode gerar item de fatura | 1:1 ou 1:N | Uma sessão pode gerar cobrança de energia e eventual ociosidade. |
| Fatura tem itens | 1:N | A fatura é explicada por linhas auditáveis. |
| Sessão pode ter alertas de IA | 1:N | Mais de uma regra/modelo pode sinalizar uma mesma sessão. |

## Exemplos de Registros Simulados

Os exemplos simulados para a Sprint 2 estão em:

- `data/exemplo-sessoes-sense-plus.csv`
- `data/dicionario-campos-sessoes.csv`

Eles não representam dados reais da FIAP. Servem para implementar e testar o importador, o rateio e os alertas sem expor informações operacionais.

## Plano da Sprint 2

| Ordem | Entrega | Tecnologias sugeridas | Critério de pronto |
| --- | --- | --- | --- |
| 1 | Estrutura do projeto e modelos de dados | Python, `dataclasses` ou Pydantic, SQLite/PostgreSQL | Entidades principais representadas e versionadas. |
| 2 | Importador de relatórios | Python, pandas, openpyxl, tabula/camelot ou leitura CSV inicial | Dados SEMS de planta importados; sessões simuladas validadas; sessões reais integradas quando exportação for confirmada. |
| 3 | Motor de rateio | Python puro, pytest | Fórmula calcula faturas e trata exceções com testes. |
| 4 | Painel mínimo | Streamlit ou FastAPI + front-end simples | Gestor vê sessões, total por usuário, alertas e faturas. |
| 5 | IA operacional | scikit-learn, pandas | Previsão simples, anomalia e cluster com dados simulados. |
| 6 | Evidência e pitch | README, prints, vídeo de 3 minutos | Fluxo demonstrável: importar relatório, calcular, explicar e alertar. |

## Métricas de Sucesso

| Métrica | Por que importa |
| --- | --- |
| Percentual de sessões importadas sem erro | Mede robustez do importador. |
| Diferença entre kWh importado e kWh faturado | Garante que o rateio não perdeu consumo. |
| Número de sessões marcadas para revisão | Mostra qualidade dos dados e utilidade da IA. |
| Tempo para fechar fatura mensal | Mede ganho operacional para o gestor. |
| Clareza da fatura para usuário | Reduz contestação e aumenta confiança. |
| Picos previstos vs picos observados | Valida a inteligência operacional. |

## Decisão de Arquitetura

A arquitetura recomendada para o EV ChargeOps é:

> Um sistema de importação e auditoria preparado para dados SEMS de planta e sessões de recarga quando confirmadas, com banco próprio, motor de rateio transparente e IA operacional aplicada a previsão, anomalia e perfis de uso.

Essa arquitetura é forte porque respeita o hardware real, aceita a ausência de API pública, não assume que o SEMS web já entrega sessões por RFID, resolve a dor de rateio quando houver base de sessão validada e deixa espaço para evoluir para API GoodWe, Modbus validado ou integrações OCPP em outros equipamentos.

## Checklist de Atendimento ao Enunciado

| Exigência da Frente 3 | Atendido? | Onde aparece |
| --- | --- | --- |
| Camadas da plataforma | Sim | Seção "Camadas da Plataforma" |
| Diagrama de arquitetura | Sim | Seção "Diagrama de Arquitetura" |
| Fluxo da sessão até a fatura | Sim | Seção "Fluxo dos Dados" |
| Modelo de rateio | Sim | Seção "Modelo de Rateio Proposto" |
| Casos excepcionais | Sim | Seção "Casos Excepcionais" |
| Aprofundamento em IA | Sim | Seção "Papel da IA na Solução" |
| Aprofundamento em esquema de dados | Sim | Seção "Esquema de Dados da Plataforma" |
| Benchmark de modelos de rateio | Sim | Seção "Benchmark de Modelos de Rateio" |
| Plano para Sprint 2 | Sim | Seção "Plano da Sprint 2" |

## Fontes Usadas nesta Frente

As fontes completas desta frente estão registradas em `references/fontes.md`.
