# Roteiro cronometrado do pitch — EV ChargeOps

Tempo-alvo: **2min48s**. Deixe o painel aberto na aba **Visão geral**, com os dados padrão já
processados. O roteiro abaixo reserva margem de 12 segundos em relação ao limite de 3 minutos.

## 0:00–0:20 — Problema

**Tela:** título e indicadores da Visão geral.

**Fala:**

> Em condomínios e empresas, compartilhar um carregador elétrico cria uma questão de
> governança: quem consumiu, quanto deve pagar e como impedir uma cobrança baseada em dados
> inconsistentes? O EV ChargeOps transforma registros de recarga e energia em um rateio
> explicável e em recomendações operacionais.

## 0:20–0:40 — Fonte dos dados e limite real

**Tela:** barra lateral e avisos do painel.

**Fala:**

> A API GoodWe/SEMS ainda não está disponível aos alunos. Por isso, este MVP usa dois CSVs
> simulados e compatíveis com a arquitetura proposta. Eles são processados somente em memória,
> e a interface também permite trocar as duas fontes por uploads futuros.

Não sugira que os arquivos representam dados reais da FIAP.

## 0:40–1:08 — Reconciliação

**Tela:** indicadores e tabela de reconciliação.

**Fala:**

> Nesta demonstração, dez sessões somam 100,50 kWh. Sete passam pelas regras de faturamento,
> totalizando 86,10 kWh. Três ficam em revisão; assim, 14,40 kWh são protegidos da cobrança
> automática. Com tarifa de 92 centavos e custo comum de 80 reais, o total é 159 reais e
> 21 centavos.

## 1:08–1:38 — Bloqueios e IA consultiva

**Tela:** aba **Sessões e alertas**; filtre por **Em revisão**.

**Fala:**

> As regras determinísticas bloqueiam casos como falha, revisão explícita ou usuário sem
> vínculo. Cada linha mantém o motivo para auditoria. O Isolation Forest aparece como um sinal
> experimental para ordenar a revisão humana, mas nunca libera, bloqueia ou altera uma cobrança.

## 1:38–2:08 — Fatura auditável

**Tela:** aba **Rateio e faturas**; selecione `APT-1201`.

**Fala:**

> A unidade APT-1201 teve 45,70 kWh faturáveis. A memória de cálculo soma as sessões válidas,
> aplica a tarifa com arredondamento monetário e adiciona 20 reais de custo comum, chegando a
> 62 reais e 4 centavos. Os filtros só detalham a informação; eles não mudam o denominador do
> rateio global.

## 2:08–2:36 — Recomendações energéticas

**Tela:** aba **Energia e recomendações**; mostre o gráfico, “Priorizar excedente solar” e
“Reduzir pico noturno”.

**Fala:**

> Os snapshots de energia permitem comparar geração solar, carga e uso da rede. O sistema
> sugere aproveitar janelas com excedente solar e escalonar recargas no pico noturno. Cada
> recomendação mostra evidência e premissas. Uma decisão sobre expansão fotovoltaica continua
> dependendo de série histórica e validação de engenharia.

## 2:36–2:48 — Encerramento

**Tela:** retorne à Visão geral.

**Fala:**

> Assim, o EV ChargeOps prova um fluxo ponta a ponta: importa, valida, protege o usuário,
> calcula um rateio auditável e apoia a economia energética. O próximo passo é substituir os
> adaptadores CSV pela fonte oficial quando a GoodWe a disponibilizar.

## Plano de contingência

Se o tempo estiver acima de 2min50s, remova a frase sobre filtros da seção de fatura e a frase
sobre expansão fotovoltaica. Se o painel falhar durante a gravação, use os quatro screenshots
listados no [guia de evidências](evidencias-e-comandos.md), mantendo a mesma ordem narrativa.
