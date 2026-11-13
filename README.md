# Citizen Assist AI – Nexo 
**Global Solution 2026.2 – Pensamento Computacional e Automação com Python (FIAP) – desafio CitizenTech**

O projeto se chama **Citizen Assist AI**, e o assistente que conversa com o usuário no terminal se chama **Nexo**.

---

## Integrantes:

| Nome | RM |
|------|----|
| Caio Henrique Ferraz da Silva | 568992 |
| Enzo Caruso Peter | 570908 |

---

## Público e problema escolhidos

**Público:** jovens que estão buscando ou começando o primeiro emprego.

**Problema:** quem entra no mercado de trabalho pela primeira vez tem muitas dúvidas ao mesmo tempo: *"Preciso de qual documento?", "O que é FGTS?", "A empresa me registrou direito?", "Essa vaga pede para eu pagar uma taxa, é golpe?"*

A informação existe, mas está espalhada em vários sites, em linguagem técnica e, às vezes, misturada com páginas que parecem oficiais e não são. Esse público ainda é alvo frequente de golpes de falsa vaga que cobram "taxas".

**Nossa solução:** o Nexo reúne essas orientações em **linguagem simples**, mostra a **fonte oficial** de cada uma, diz **quando a informação foi conferida** e deixa claro que **não é um canal oficial**.

---

## Como executar

Requisitos: **Python 3.8 ou superior**. Não precisa instalar nenhuma biblioteca (só a biblioteca padrão).

```bash
git clone https://github.com/CaioSilva2026/GS2026.2_Citizen_Assist_AI_Assistente_Digital.git
cd GS2026.2_Citizen_Assist_AI_Assistente_Digital
python main.py
```

Execute sempre a partir da pasta do projeto, porque os caminhos dos arquivos são relativos (`data/...`). A pasta `data/` é criada automaticamente se não existir. Já o arquivo `data/base_conhecimento.json` é obrigatório: sem ele, o programa avisa o que houve e encerra sem travar.

### Menu

```
1. Fazer uma pergunta                 (pergunta em texto livre)
2. Consultar assuntos por categoria   (navegação numerada)
3. Ver indicadores de atendimento
4. Exportar atendimentos para CSV
0. Sair                              (pede nota de facilidade e exporta o CSV)
```

Em todas as telas, **digitar 0 volta** para a tela anterior. Se a pessoa apertar `Ctrl+C`, o programa encerra com uma mensagem, sem mostrar erro.

### Exemplo de uso

```
Qual sua dúvida sobre o primeiro emprego? (0 para voltar): O que é jovem aprendiz?

Confiança da resposta: ALTA (8 pontos)

>> Entrar no mercado como Jovem Aprendiz  [Trabalho e direitos]
O contrato de Jovem Aprendiz é um contrato especial, com duração de até 2 anos, ...
Documentos necessários:
  - Comprovante de matrícula e frequência escolar (se não terminou o ensino médio)
  - ...
Onde: Instituições de aprendizagem e empresas que contratam aprendizes
Fonte: https://www.trt4.jus.br/portais/trt4/jovem-aprendiz (verificado em 2026-11-11)
Aviso: este assistente NÃO é um canal oficial.

Essa orientação respondeu sua dúvida? (s/n): s

Qual sua dúvida sobre o primeiro emprego? (0 para voltar): meu cpf é 123.456.789-00
Não digite CPF, telefone ou e-mail.
```

---

## Estrutura do projeto

```
citizen-assist-ai/
├── README.md
├── .gitignore               # ignora .idea/ e __pycache__/
├── main.py                  # menu principal
├── orientacao.py            # classe Orientacao
├── base_conhecimento.py     # classe BaseConhecimento + normalizar()
├── assistente.py            # classe Assistente
└── data/
    ├── base_conhecimento.json   # as orientações (o "conhecimento" do assistente)
    ├── historico.json           # um registro por atendimento
    ├── notas.json               # notas de facilidade de uso (1 a 5)
    └── atendimentos.csv         # atendimentos exportados para planilha
```

---

## Como o código funciona

### As três classes e a composição

Cada classe tem uma responsabilidade, e elas se encaixam por **composição**: um `Assistente` *tem uma* `BaseConhecimento`, que *tem uma lista de* `Orientacao`.

```
Assistente
└── base: BaseConhecimento
    └── orientacoes: [Orientacao, Orientacao, Orientacao, ...]
```

| Classe | O que representa | O que faz |
|--------|------------------|-----------|
| `Orientacao` | Uma informação da base (um registro do JSON) | Guarda os dados e se mostra na tela com `exibir()` |
| `BaseConhecimento` | O conjunto de todas as orientações | Lê o JSON (`carregar`), lista categorias (`categorias`, `por_categoria`) e busca a melhor orientação (`pontuar`, `buscar`) |
| `Assistente` | Quem conversa com o cidadão | Atende (`perguntar`, `navegar`), guarda o histórico (`registrar`), calcula indicadores (`indicadores`) e exporta o CSV (`exportar_csv`) |

No `main.py`, o uso é este:

```python
base = BaseConhecimento("data/base_conhecimento.json")
base.carregar()                       # lê o JSON e cria os objetos Orientacao
assistente = Assistente("Nexo", base)
assistente.perguntar()                # usa base.buscar() e orientacao.exibir()
```

### A base de conhecimento (JSON)

É uma **lista de dicionários**: cada dicionário é uma orientação, com os campos `id`, `categoria`, `titulo`, `palavras_chave`, `resposta`, `documentos`, `onde`, `fonte` e `verificado_em`:

```json
{
  "id": 4,
  "categoria": "Trabalho e direitos",
  "titulo": "Entrar no mercado como Jovem Aprendiz",
  "palavras_chave": ["jovem aprendiz", "aprendiz", "contrato de aprendizagem", "..."],
  "resposta": "O contrato de Jovem Aprendiz é um contrato especial, ...",
  "documentos": ["Comprovante de matrícula e frequência escolar (...)", "..."],
  "onde": "Instituições de aprendizagem e empresas que contratam aprendizes",
  "fonte": "https://www.trt4.jus.br/portais/trt4/jovem-aprendiz",
  "verificado_em": "2026-11-11"
}
```

Hoje a base tem **12 orientações** em **4 categorias**:

| Categoria | Orientações |
|-----------|-------------|
| Documentos | Carteira de Trabalho Digital, título de eleitor, CPF |
| Trabalho e direitos | Jovem Aprendiz, conferir se a empresa registrou o contrato, falar com o Ministério do Trabalho (158) |
| Salário e benefícios | FGTS, seguro-desemprego, 13º salário, férias |
| Golpes e segurança | Reconhecer vaga falsa, denunciar golpe de falsa vaga |

Todas têm pelo menos 3 palavras-chave (a maioria tem bem mais), fonte oficial e data de verificação. As respostas só usam o que foi conferido nas fontes listadas neste README.

---

## A busca com pontuação

A "inteligência" do Nexo é **baseada em regras**, sem nenhum modelo de IA. A pergunta é comparada com cada orientação, cada uma recebe pontos, e a de maior pontuação é exibida.

### 1. Normalização

Antes de comparar, a pergunta, as palavras-chave e os títulos passam por `normalizar()`: tudo em **minúsculas, sem acentos e sem pontuação**. Assim, `"Cartão do SUS?"` e `"cartao do sus"` viram a mesma coisa. O texto também ganha um espaço no começo e no fim, para que uma palavra curta não "case" dentro de outra (por exemplo, `sus` não casa dentro de `consus`).

### 2. Plural simples

Para a busca não falhar por causa do plural, usamos `radical()`, que tira o "s" ou o "es" do fim das palavras maiores: `golpes` vira `golpe` e `aprendizes` vira `aprendiz`. Isso é aplicado dos dois lados, na pergunta e nas palavras-chave.

### 3. Pontuação

| Regra | Pontos |
|-------|--------|
| Uma palavra-chave da orientação aparece na pergunta | **+3** (por palavra-chave) |
| Uma palavra importante da pergunta (4 letras ou mais) aparece no título | **+1** (cada palavra conta uma vez) |

**Ajuste que fizemos na regra do +1:** palavras muito comuns são ignoradas (`como, para, com, uma, qual, quais, onde, quando, meu, minha, seu, sua, que, dos, das, por, tem, ser, fazer`). Sem isso, qualquer pergunta que começasse com "como" ou "fazer" ganharia ponto à toa em várias orientações.

### 4. Confiança

| Melhor pontuação | Resultado |
|------------------|-----------|
| 6 pontos ou mais | Confiança **ALTA** |
| De 3 a 5 pontos | Confiança **MÉDIA** |
| Menos de 3 pontos | "Não encontrei": o assistente lista os assuntos que conhece e sugere outras palavras ou a navegação por categorias |

O método `buscar()` devolve uma **lista de tuplas** `(pontos, orientacao)`, da maior para a menor pontuação. O assistente mostra a melhor orientação e até **2 alternativas** que tenham 3 pontos ou mais.

### Exemplos de cálculo

**"O que é jovem aprendiz?"** → orientação *Jovem Aprendiz*

| Motivo | Pontos |
|--------|--------|
| Palavra-chave `jovem aprendiz` aparece | +3 |
| Palavra-chave `aprendiz` aparece | +3 |
| `jovem` está no título | +1 |
| `aprendiz` está no título | +1 |
| **Total** | **8 → ALTA** |

**"Tenho 16 anos, posso trabalhar?"** → orientação *Jovem Aprendiz*: `tenho 16 anos` (+3) + `posso trabalhar` (+3) = **6 → ALTA**.

**"Quais são os golpes de vaga?"** → orientação *Reconhecer uma vaga falsa*: `golpe` (+3, graças ao plural simples) + `vaga` no título (+1; "quais" é ignorada) = **4 → MÉDIA**.

> Os pesos (+3 e +1) e os limites (3 e 6) são os sugeridos na atividade. A palavra-chave vale mais porque é uma pista bem mais forte de que a pergunta é sobre aquele assunto.

---

## Regras de atendimento

- **Entradas inválidas nunca encerram o programa.** Letras, números fora da faixa, resposta vazia ou algo diferente de `s`/`n` só geram um aviso, e a pergunta é refeita.
- **Dados pessoais são bloqueados.** O assistente nunca pede nome, CPF, telefone ou e-mail. Se a pergunta tiver **8 ou mais dígitos** ou um **@**, ela é recusada e **não é registrada**.
- **Transparência.** Toda resposta mostra a fonte, a data de verificação e o aviso "este assistente NÃO é um canal oficial".
- **Arquivos à prova de erro.** Se o JSON da base não existir, estiver corrompido, estiver vazio ou tiver um registro com campo faltando ou do tipo errado (por exemplo, `palavras_chave` como texto em vez de lista), o programa mostra uma mensagem clara em vez de quebrar. Se o histórico ou as notas estiverem ausentes ou estragados, o programa começa do zero e descarta registros incompletos.
- **Interrupção segura.** `Ctrl+C` ou fim da entrada encerram o programa com uma mensagem e exportam o CSV.
- **Navegação por categorias** com "0 para voltar" em todas as telas.

---

## Histórico, indicadores e CSV

Cada atendimento é salvo em `data/historico.json` com: **data, origem** (`pergunta` ou `categoria`), **pergunta, id da orientação, se encontrou, se ajudou, tentativas** e **tempo em segundos**. Ao sair, o programa pede uma **nota de facilidade de 1 a 5** (guardada em `data/notas.json`) e exporta `data/atendimentos.csv` com `csv.DictWriter`.

Na pergunta em texto livre, se a pessoa não encontra a resposta e reformula, tudo isso conta como **um atendimento** com várias tentativas. Uma pergunta não encontrada só é registrada quando a pessoa sai (digitando 0) sem achar nada.

| Indicador | O que significa |
|-----------|-----------------|
| Resposta encontrada (%) | Das perguntas em texto livre, quantas tiveram resposta |
| Taxa de acerto (%) | Atendimentos em que a pessoa disse que ajudou (`s`) |
| Tempo médio para encontrar | Média de segundos até achar uma orientação |
| Tentativas por atendimento | Média de vezes que a pessoa precisou perguntar |
| Facilidade de uso (1 a 5) | Média das notas dadas ao sair |
| Dúvidas sem solução | Perguntas que não ajudaram: é a lista que usamos para melhorar a base |

> "Resposta encontrada" conta **só as perguntas digitadas**. Na navegação por categorias, a pessoa escolhe de uma lista pronta e sempre "encontra", o que inflaria o número.

---

## Teste com usuários

Testamos o Nexo com **[N] pessoas de fora da equipe**, somando **[N] atendimentos**. Cada pessoa escreveu as próprias perguntas, sem ver a base de conhecimento. Nenhum nome ou dado pessoal foi registrado.

| Indicador                  | Resultado       |
|----------------------------|-----------------|
| atendimentos               | [11]            |
| Resposta encontrada (perguntas em texto livre)    | [	60,0 % (3 de 5)] % |
| Taxa de acerto (ajudou) | [81,8 % (9 de 11)] |
| Tempo médio para encontrar | [34,9 ]  s      |
| Tentativas por atendimento  | [1,1]           |
| Facilidade de uso (1 a 5)|   [5, 5, 4, 5]   |


## Integrações com outras disciplinas

Nenhuma.

---

## Fontes consultadas

Todas as respostas vêm de fontes oficiais, conferidas pela equipe em **11/11/2026**:

- Carteira de Trabalho Digital (gov.br): https://www.gov.br/pt-br/servicos/obter-a-carteira-de-trabalho
- Tribunal Superior Eleitoral (título de eleitor): https://www.tse.jus.br/comunicacao/noticias/2022/Dezembro/ainda-nao-tem-titulo-de-eleitor-emita-o-documento-de-forma-gratuita-e-sem-sair-de-casa
- Receita Federal (CPF): https://www.gov.br/receitafederal/pt-br
- TRT-4 (Jovem Aprendiz): https://www.trt4.jus.br/portais/trt4/jovem-aprendiz
- Caixa Econômica Federal (FGTS): https://www.caixa.gov.br/beneficios-trabalhador/fgts/
- Ministério do Trabalho e Emprego (seguro-desemprego, férias, 158 e golpes): https://www.gov.br/trabalho-e-emprego/pt-br
- Ministério do Trabalho e Emprego (13º salário): https://www.gov.br/trabalho-e-emprego/pt-br/noticias-e-conteudo/2024/Dezembro/decimo-terceiro-salario-entenda-o-direito-regras-e-prazos-de-pagamento
- Ministério Público do Trabalho (denúncias): https://www.mpt.mp.br

---

## Decisões técnicas

- **Busca por regras, sem IA externa:** a pontuação é simples, previsível e explicável. Dá para rastrear cada resposta até as palavras-chave que a geraram.
- **"Não sei" em vez de inventar:** se nenhuma orientação chega a 3 pontos, o assistente admite que não encontrou. Preferimos isso a dar uma resposta errada sobre direitos trabalhistas.
- **Espaços nas pontas do texto normalizado:** evita que uma palavra curta, como `sus`, "case" dentro de outra palavra.
- **Palavras ignoradas e plural simples:** reduzem falsos acertos e falhas por causa do plural.
- **`carregar()` valida cada registro e só troca a lista de orientações no fim:** se o JSON falhar no meio, ou tiver um campo com tipo errado, a base não fica pela metade e a mensagem diz qual registro está errado.
- **`perguntar()` dividido em métodos pequenos** (`ler_pergunta`, `atender_pergunta`, `mostrar_resposta`, `mostrar_nao_encontrei`), e os limites de confiança (3 e 6) ficam em constantes no topo do `assistente.py`.
- **A base cresce com o uso:** as "dúvidas sem solução" mostram quais palavras-chave faltam. Para melhorar o assistente, basta editar o JSON, sem mexer no código.

---

## Limitações

- **Não é um canal oficial.** Ele orienta, mas a palavra final é sempre do órgão responsável. Por isso toda resposta traz a fonte.
- **Só responde o que está na base.** São 12 orientações em 4 assuntos. Perguntas fora disso (por exemplo, sobre carreira em uma área específica) recebem "não encontrei".
- **A busca compara palavras, não entende o sentido.** Sinônimos, gírias e erros de digitação que não estejam nas palavras-chave podem não ser reconhecidos.
- **Palavras comuns ainda podem somar ponto.** Mesmo com a lista de palavras ignoradas, uma palavra de 4 letras ou mais que apareça em vários títulos (como "emprego") pode dar +1. O limite mínimo de 3 pontos evita a maioria dos falsos acertos.
- **Palavras-chave parecidas somam juntas.** Em "carteira de trabalho digital", por exemplo, tanto `carteira de trabalho` quanto `carteira de trabalho digital` pontuam.
- **As regras mudam.** Prazos e valores (seguro-desemprego, FGTS, 13º) podem ser atualizados pelo governo. A data de verificação existe para a pessoa saber o quão recente é a informação.
- **O filtro de dados pessoais é simples.** Ele bloqueia 8 ou mais dígitos no texto todo ou um `@`. Por isso uma pergunta como "lei 8.213 de 1991" (8 dígitos) também é bloqueada, e o usuário precisa reescrever.
- **Nomes não são bloqueados.** O assistente nunca pede o nome, mas se alguém digitar "meu nome é ...", o texto é salvo no histórico. Por isso o aviso inicial pede para não informar dados pessoais.
- **Palavras-chave muito específicas.** `tenho 16 anos` só casa com essa idade exata; quem digitar outra idade pode não ser encontrado.
- **As alternativas só mostram o título.** A pessoa vê as outras orientações sugeridas, mas precisa usar o menu de categorias para abri-las.
- **A base só é lida ao iniciar o programa.** Depois de editar o JSON, é preciso fechar e abrir o programa de novo.
- **Funciona só no terminal**, sem interface gráfica.

---

## Como melhorar a base (sem mexer no código)

1. Para uma pergunta passar a ser encontrada, adicione uma palavra-chave (sem acento, em minúsculas) na lista `palavras_chave` da orientação certa de `data/base_conhecimento.json`.
2. Para criar uma orientação nova, copie um registro, troque o `id` por um número novo e preencha **todos** os campos, incluindo uma `fonte` oficial e `verificado_em`.
3. Salve o arquivo e rode `python main.py` de novo.

---

## Vídeo técnico

Link (YouTube, não listado): [cole aqui o link]