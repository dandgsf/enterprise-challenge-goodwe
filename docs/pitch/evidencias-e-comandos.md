# Evidências, comandos e resultados esperados

Este guia permite reproduzir o MVP antes da gravação e organizar as evidências visuais. Todos
os comandos devem ser executados na raiz do repositório.

## Instalação reproduzível

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e . -r requirements-dev.txt
```

O projeto usa layout `src/`; portanto, `-e .` faz parte do preflight. As fontes padrão são:

- `data/exemplo-sessoes-sense-plus.csv`;
- `data/exemplo-energia-sems.csv`.

Ambas são simuladas, não contêm dados operacionais reais e devem permanecer identificadas
como tal durante a apresentação.

## Verificações automáticas

```powershell
python -m ruff check .
python -m pytest
python -m pytest tests/test_acceptance.py -q
```

A suíte completa deve terminar sem falhas e com cobertura de domínio de pelo menos 85%. O
teste de aceitação isolado deve confirmar os números usados no pitch. Para iniciar o painel:

```powershell
streamlit run app.py
```

O estado inicial esperado contém quatro abas, dois seletores de upload, tarifa de R$ 0,92/kWh
e custo comum de R$ 80,00.

## Números que precisam coincidir

| Verificação | Esperado |
| --- | ---: |
| Sessões importadas / faturáveis / bloqueadas | 10 / 7 / 3 |
| Energia importada / faturável / em revisão | 100,50 / 86,10 / 14,40 kWh |
| Custo variável / comum / total | R$ 79,21 / R$ 80,00 / R$ 159,21 |
| APT-1201 | 45,70 kWh / R$ 62,04 |
| APT-0810 | 16,00 kWh / R$ 34,72 |
| APT-0911 | 17,90 kWh / R$ 36,47 |
| APT-0504 | 6,50 kWh / R$ 25,98 |

Ao trocar a tarifa para R$ 1,00/kWh, o total deve mudar para R$ 166,10, sem alterar os 86,10
kWh faturáveis nem os R$ 80,00 de custo comum. Retorne a tarifa para R$ 0,92 antes de gravar.

## Capturas validadas

As evidências da execução estão versionadas em `assets/prints/`:

1. `assets/prints/01-visao-geral.png` — cinco indicadores, avisos de dados simulados e tabela
   de reconciliação completa;
2. `assets/prints/02-sessoes-alertas.png` — aba Sessões e alertas filtrada por Em revisão,
   mostrando as três sessões bloqueadas e seus motivos;
3. `assets/prints/03-rateio-faturas.png` — aba Rateio e faturas com a memória de cálculo da
   APT-1201 e total de R$ 62,04;
4. `assets/prints/04-energia-recomendacoes.png` — recomendações de uso solar e redução de pico
   com evidências e premissas visíveis; o gráfico é mostrado ao vivo antes da rolagem.

Capture apenas a área do aplicativo, sem terminal, notificações ou dados pessoais. Não edite
os valores nas imagens: a evidência precisa corresponder à execução reproduzível.

## O que a demonstração comprova

- leitura de CSV UTF-8 com validação de estrutura e limite de 5 MB;
- quarentena de linhas inválidas e bloqueio determinístico de sessões inseguras;
- rateio por unidade com `Decimal`, memória de cálculo e reconciliação global;
- custo comum dividido entre unidades com consumo faturável;
- ociosidade exibida como não calculada quando `idle_minutes` não existe;
- alerta experimental de anomalia sem efeito no faturamento;
- recomendação energética acompanhada de evidência, premissas e revisão humana;
- processamento local em memória e hash SHA-256 da fonte importada.

## Limites que devem permanecer explícitos

- a API GoodWe/SEMS não foi disponibilizada aos alunos;
- os CSVs do MVP são simulados;
- não há integração ativa com carregador, Modbus, pagamento ou cobrança automática;
- não há persistência, autenticação ou operação multiusuário;
- o conjunto de dez sessões não sustenta alegação de precisão estatística da IA;
- recomendação fotovoltaica é apenas sinal preliminar e requer dados históricos e engenharia.

## Solução rápida de problemas

- `ModuleNotFoundError: ev_chargeops`: repita
  `python -m pip install -e . -r requirements-dev.txt` no ambiente ativo.
- `streamlit` não reconhecido: use `python -m streamlit run app.py`.
- Porta 8501 ocupada: use `streamlit run app.py --server.port 8502`.
- CSV rejeitado: confirme UTF-8, tamanho inferior a 5 MB, cabeçalhos do dicionário de dados e
  presença de pelo menos uma linha.
- Apenas um upload selecionado: envie os dois CSVs ou remova ambos para restaurar a demo.
