---
name: imagens-futebol
description: Gera (Gemini Pro pelo navegador), busca e organiza os visuais (imagens IA, fotos de arquivo, clipes) de cada cena de um vídeo do canal dark de futebol, cuidando de direitos autorais e de um estilo visual consistente. Use quando o usuário pedir imagens, visuais, prompts de IA, fotos para o vídeo, "o que colocar em cada cena", ou quando faltar arquivo de visual no roteiro.json.
---

# Visuais das cenas

Cada cena do `roteiro.json` precisa de um arquivo em `visual` (imagem `.jpg/.png/.webp` ou clipe `.mp4/.mov`), guardado em `projetos/<slug>/imagens/` com o número da cena (`01.jpg`, `02.jpg`…).

## Gerar com o Gemini Pro pelo navegador (fluxo principal)

O usuário tem Gemini Pro na conta Google logada no navegador. Use a ferramenta de navegador disponível (Claude in Chrome ou o navegador do app — carregue a skill do navegador antes do primeiro uso):

1. Abra `gemini.google.com` numa aba nova. Comece **uma conversa por vídeo** (ajuda a manter o estilo entre as cenas).
2. Para cada cena, envie: descrição da cena (`descricao_visual`) + o **prompt de estilo do canal** (abaixo) + "formato vertical 9:16". Uma imagem por mensagem.
3. Confira o resultado antes de baixar: vertical, sem texto/logos estranhos, sem rosto realista de jogador real, sem dedos/rostos deformados em primeiro plano. Se ruim, peça ajuste na mesma conversa ("mesma cena, mais escura, câmera mais baixa").
4. Baixe no tamanho máximo e mova da pasta Downloads para `projetos/<slug>/imagens/NN.png` (NN = número da cena, dois dígitos). Atualize `visual` da cena se a extensão mudou.
5. Se aparecer marca d'água visível do Gemini num canto, verifique na prévia se o recorte 9:16 a esconde; se não, recorte a imagem com ffmpeg (`crop`) antes de usar.

Faça tudo por conta própria e só traga ao usuário a grade final das imagens para aprovação. Se a página pedir login, verificação ou mostrar limite de uso, pare e avise o usuário.

Prompt de estilo do canal (o mesmo em todos os vídeos — também em `docs/PLANO.md`):

```
Fotografia documental de arquivo dos anos 1950, preto e branco, granulação de filme,
iluminação dramática em claro-escuro, cinematográfica, atmosfera tensa e melancólica,
composição vertical 9:16, sem texto, sem logotipos.
```

## Direitos autorais — leia antes

Canal dark que monetiza **não pode** usar transmissões de TV, lances de jogos recentes ou fotos de agência (Getty, AP, Reuters): dá strike, derruba o vídeo e bloqueia a monetização. Use, nesta ordem:

1. **Domínio público / licença livre**: Wikimedia Commons (filtre por licença; fotos brasileiras anteriores a ~1950 e muitas do Arquivo Nacional são de domínio público), Arquivo Nacional, Biblioteca Nacional (Hemeroteca), Library of Congress, Nationaal Archief (Holanda, muito material de Copa de 1950–1980 em CC0). Anote autor e licença em `creditos.txt` no projeto.
2. **Imagens geradas por IA** (Gemini — principal —, Midjourney, Flux…): ótimas para reconstituir cenas. Não gere o rosto realista de jogador identificável vivo nem logotipos oficiais de clubes/FIFA — use silhuetas, de costas, à distância ou ilustração.
3. **Banco de vídeo grátis** (Pexels, Pixabay): estádio vazio, bola, gramado, torcida genérica, chuva, vestiário — ótimos para "respiro" entre fotos.
4. **Mapas, recortes de jornal recriados, placares e datas** feitos por você (Canva/Photoshop) — sempre autorais.

## Variações de estilo

- Época colorida (1970–1990): troque "preto e branco" por "foto colorida desbotada dos anos 1980, filme Kodachrome".
- Tensão/mistério: acrescente "neblina, silhueta, contra-luz, ângulo baixo, estádio vazio à noite".
- Outras ferramentas de IA (Midjourney, Flux, DALL·E) usam o mesmo prompt em inglês: `1950s archival documentary photograph, black and white film grain, dramatic chiaroscuro lighting, cinematic, moody, vertical 9:16, no text, no logos`.

Para cada cena, registre em `descricao_visual` o tipo (arquivo real / IA / stock) e o prompt ou termo de busca (ex.: Commons: `Maracanã 1950`).

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
