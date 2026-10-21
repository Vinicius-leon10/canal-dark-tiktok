---
name: imagens-futebol
description: Planeja e organiza os visuais (fotos de arquivo, imagens geradas por IA, clipes) de cada cena de um vídeo do canal dark de futebol, cuidando de direitos autorais e de um estilo visual consistente. Use quando o usuário pedir imagens, visuais, prompts de IA, fotos para o vídeo, "o que colocar em cada cena", ou quando faltar arquivo de visual no roteiro.json.
---

# Visuais das cenas

Cada cena do `roteiro.json` precisa de um arquivo em `visual` (imagem `.jpg/.png/.webp` ou clipe `.mp4/.mov`), guardado em `projetos/<slug>/imagens/` com o número da cena (`01.jpg`, `02.jpg`…).

## Direitos autorais — leia antes

Canal dark que monetiza **não pode** usar transmissões de TV, lances de jogos recentes ou fotos de agência (Getty, AP, Reuters): dá strike, derruba o vídeo e bloqueia a monetização. Use, nesta ordem:

1. **Domínio público / licença livre**: Wikimedia Commons (filtre por licença; fotos brasileiras anteriores a ~1950 e muitas do Arquivo Nacional são de domínio público), Arquivo Nacional, Biblioteca Nacional (Hemeroteca), Library of Congress, Nationaal Archief (Holanda, muito material de Copa de 1950–1980 em CC0). Anote autor e licença em `creditos.txt` no projeto.
2. **Imagens geradas por IA** (Midjourney, Leonardo, Ideogram, DALL·E, Flux…): ótimas para reconstituir cenas. Não gere o rosto realista de jogador identificável vivo nem logotipos oficiais de clubes/FIFA — use silhuetas, de costas, à distância ou ilustração.
3. **Banco de vídeo grátis** (Pexels, Pixabay): estádio vazio, bola, gramado, torcida genérica, chuva, vestiário — ótimos para "respiro" entre fotos.
4. **Mapas, recortes de jornal recriados, placares e datas** feitos por você (Canva/Photoshop) — sempre autorais.

## Estilo visual do canal (consistência = identidade)

Prompt base para IA (em inglês, acrescente a cena no começo):

```
<cena>, 1950s archival documentary photograph, black and white film grain, dramatic chiaroscuro lighting,
cinematic, moody, high contrast, vertical composition 9:16, no text, no logos
```

Variações:
- Época colorida (1970–1990): troque por `1980s faded color film photograph, kodachrome, soft grain`.
- Tensão/mistério: acrescente `fog, silhouette, low angle, empty stadium at night`.
- Sempre `vertical 9:16` (ou `--ar 9:16` no Midjourney) — imagem horizontal perde as laterais no corte.

Para cada cena, entregue: arquivo esperado, tipo (arquivo real / IA / stock), e o **prompt** ou o **termo de busca** (ex.: Commons: `Maracanã 1950`, `FIFA World Cup 1950`, `Barbosa goalkeeper`). Grave isso em `descricao_visual` da cena.

## Configurações por tipo de visual (no roteiro.json)

| Visual | Configuração recomendada |
|---|---|
| Foto antiga horizontal | `"enquadramento": "encaixar"` (foto inteira com fundo desfocado) + `"filtro": "arquivo"` ou `"pb"` |
| Foto/IA vertical | `"enquadramento": "preencher"` (padrão) + `movimento` |
| Rosto / detalhe | `"movimento": "zoom_in"` |
| Estádio / multidão | `"movimento": "pan_direita"` ou `"pan_esquerda"` |
| Clipe de vídeo | `"inicio_clipe": 2.5` para pular o começo; é repetido em loop se for curto |

Resolução mínima: 1080 px no lado menor. Imagens pequenas ficam borradas com o zoom.

## Checklist antes de montar

- [ ] Todas as cenas têm `visual` apontando para um arquivo que existe.
- [ ] Não há dois visuais iguais seguidos.
- [ ] A cena do gancho (1) tem a imagem mais forte do vídeo.
- [ ] Nenhuma imagem com marca d'água, logo de TV ou texto em outra língua grande no meio.
- [ ] `creditos.txt` com as fontes das fotos reais.
