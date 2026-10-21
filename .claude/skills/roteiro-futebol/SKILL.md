---
name: roteiro-futebol
description: Escreve o roteiro narrado (formato documentário curto, 45–75s) de um vídeo do canal dark de futebol — curiosidades, histórias e fatos históricos — já dividido em cenas no arquivo roteiro.json. Use quando o usuário pedir roteiro, texto da narração, ideia de vídeo, pauta, "conta a história de...", ou der um tema de futebol (jogo, jogador, Copa, clube, tragédia, recorde, bastidor).
---

# Roteiro documentário de futebol (TikTok dark)

Você escreve como um narrador de documentário: voz grave, frases curtas, tensão crescente, fatos concretos (datas, números, nomes). Nada de "fala galera", nada de emoji na narração. O espectador tem que sentir que está ouvindo um segredo.

## 1. Pesquisa e checagem (obrigatório)

- Antes de escrever, liste os **fatos-chave** (datas, placar, minuto do gol, público, nomes) e, se tiver busca na web, confirme cada um em pelo menos uma fonte confiável (FIFA, CBF, jornais, Wikipédia com referência).
- Público de estádio, valores e citações costumam ter versões diferentes: use a versão oficial ou diga "cerca de", "segundo relatos".
- Citação famosa só entre aspas se for documentada. Se for lenda, narre como lenda ("dizem que...").
- Guarde as fontes no campo `fontes` do roteiro.json. Erro factual em canal de curiosidade destrói credibilidade nos comentários.

## 2. Estrutura (45–75 segundos ≈ 120–190 palavras)

| Bloco | Tempo | O que faz |
|---|---|---|
| **Gancho** | 0–3s | Frase de impacto que abre uma pergunta. Começa no meio da ação. |
| **Contexto** | 3–12s | Onde, quando, quem. Só o necessário. |
| **Escalada** | 12–45s | Os fatos em ordem, cada frase aumentando a tensão. Um "mas" ou virada a cada ~10s. |
| **Revelação** | 45–60s | O fato mais surpreendente, guardado para o fim. |
| **Fecho** | últimos 3–5s | Frase que fica na cabeça ou pergunta que gera comentário. Pode deixar gancho para parte 2. |

Fórmulas de gancho que funcionam:
- **Contradição**: "O maior goleiro do Brasil morreu sendo tratado como criminoso."
- **Número absurdo**: "Duzentas mil pessoas. E nenhuma delas fez barulho."
- **Segredo**: "A FIFA nunca gostou que você soubesse dessa história."
- **Começo in media res**: "Faltavam onze minutos quando o Maracanã inteiro parou de respirar."
- **Pergunta direta**: "Você sabe por que a seleção brasileira não joga mais de branco?"

Evite gancho que entrega a resposta. A resposta vem na revelação.

## 3. Regras de escrita para narração (TTS)

- Frases de **6 a 14 palavras**. Uma ideia por frase.
- Escreva números como se fala quando importa a pronúncia: "duzentas mil pessoas", "mil novecentos e cinquenta" pode ficar "1950" (o TTS lê bem anos), mas placares escreva "dois a um".
- Use pontuação para dar ritmo: ponto = pausa; reticências = suspense; vírgula = respiro. Evite parênteses e travessões longos.
- Siglas: escreva como deve ser lido ("Fifa", "CBF" funciona).
- Sem palavrões e sem descrições gráficas de violência/morte (TikTok derruba alcance). Tragédias: tom respeitoso.
- Português do Brasil, vocabulário simples, verbo no presente histórico dá urgência ("Ghiggia avança. Barbosa se adianta.").

## 4. Dividir em cenas

Cada cena = 1 a 2 frases = **3 a 7 segundos** de narração = 1 visual. Vídeo de 60s tem ~10–14 cenas. Troca de imagem a cada poucos segundos segura a retenção.

Para cada cena defina:
- `narracao`: texto exato que será falado.
- `visual`: caminho da imagem/clipe (ex.: `imagens/03.jpg`). Se ainda não existe, invente o nome e preencha `descricao_visual`.
- `descricao_visual`: o que deve aparecer (foto real de arquivo, ou prompt de imagem IA em inglês). A skill `imagens-futebol` usa isso.
- `texto_tela` (opcional): data/lugar/número em destaque, ex.: "MARACANÃ, 1950", "173.850 PESSOAS". Use em ~3–4 cenas, não em todas.
- `filtro`: `arquivo` (sépia, foto antiga), `pb` (preto e branco), `documentario` (padrão, cor dessaturada), `nenhum`.
- `movimento` (opcional): `zoom_in` para tensão/revelação, `zoom_out` para contexto, `pan_*` para paisagens/multidão.
- `transicao` (opcional): como a cena entra — `fade` (padrão), `corte` (impacto, revelação), `fadeblack` (mudança de tempo/tom).
- `efeito` (opcional): som de impacto/whoosh em `assets/efeitos/` na virada.

## 5. Saída

Crie a pasta `projetos/<slug>/` (slug curto, sem acento: `maracanazo-1950`) e grave `roteiro.json` no formato abaixo (veja um completo em `projetos/exemplo-maracanazo/roteiro.json`):

```json
{
  "titulo": "O dia em que o Maracanã se calou",
  "voz": "pt-BR-AntonioNeural",
  "velocidade": "+5%",
  "musica": "assets/musicas/tensao.mp3",
  "volume_musica": 0.22,
  "marca": "@seucanal",
  "legenda_post": "texto da legenda do TikTok com 3-5 hashtags",
  "fontes": ["https://..."],
  "cenas": [
    {
      "narracao": "Duzentas mil pessoas. E, de repente, nenhuma delas fez barulho.",
      "visual": "imagens/01.jpg",
      "descricao_visual": "Foto de arquivo do Maracanã lotado em 1950",
      "texto_tela": "MARACANÃ, 1950",
      "filtro": "arquivo",
      "movimento": "zoom_in"
    }
  ]
}
```

Depois mostre ao usuário o roteiro corrido (só as narrações, numeradas por cena), o total de palavras e a duração estimada (palavras ÷ 2,7 ≈ segundos). Sugira também:
- 1 legenda de post curta + 3–5 hashtags (#futebol #historiadofutebol #curiosidades + específicas);
- 1 texto de capa (3–5 palavras) para a thumbnail.

## Pautas que rendem no nicho

Tragédias e reviravoltas (Maracanazo, Superga, Chapecoense — com respeito), jogos absurdos (149 x 0 em Madagascar), regras que mudaram por causa de um lance, jogadores esquecidos, maldições e superstições, bastidores de Copas, recordes improváveis, guerra e futebol (Trégua de Natal 1914, Guerra do Futebol 1969), camisas e escudos com história, goleiros artilheiros, transferências bizarras. Séries ("Parte 1/2/3", "Copas esquecidas #4") aumentam o retorno de público.
