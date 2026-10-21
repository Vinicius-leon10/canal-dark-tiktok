---
name: edicao-documentario
description: Edita e renderiza o vídeo vertical 9:16 estilo documentário do canal dark de futebol com ffmpeg — movimento de câmera nas fotos, tratamento de cor de arquivo, transições, legendas palavra a palavra, textos de tela, música com ducking e efeitos sonoros. Use quando o usuário pedir para editar, montar, renderizar, exportar, gerar prévia, mudar legenda, transição, filtro, música ou ritmo do vídeo.
---

# Edição documentário (ffmpeg)

A ferramenta é `ferramentas/montar_video.py`. Ela lê `projetos/<slug>/roteiro.json` + `saida/narracao.json` e gera o MP4 pronto para postar.

## Rodar

```bash
python ferramentas/montar_video.py projetos/<slug> --previa   # 540x960, rápido, para revisar
python ferramentas/montar_video.py projetos/<slug>            # final 1080x1920 30fps -> saida/<slug>.mp4
```

Também gera `saida/capa.jpg` (quadro de 0,8s) e `saida/legendas.ass`. Na prévia, as cenas ficam em cache (`saida/tmp_previa/`): mudar só legenda/música/efeitos não re-renderiza as cenas. A renderização final leva alguns minutos para 60s de vídeo.

Pré-requisitos: `ffmpeg` com libass (vem no ffmpeg comum) e `saida/narracao.json` (skill `narracao-documentario`).

## Fluxo de edição

1. Confira se todo `visual` existe (o script avisa qual falta).
2. Rode a **prévia** e extraia uma grade de quadros para revisar sem assistir tudo:
   ```bash
   ffmpeg -y -loglevel error -i projetos/<slug>/saida/previa.mp4 \
     -vf "fps=1/3,scale=180:320,tile=6x2" -frames:v 1 projetos/<slug>/saida/grade.jpg
   ```
   Abra `grade.jpg` (Read) e verifique: legenda legível e fora da área da interface do TikTok, textos de tela não cortados, nenhum quadro preto inesperado, imagens não esticadas.
3. Ajuste o roteiro.json e rode a prévia de novo.
4. Renderize o final e entregue: caminho do MP4, duração, `capa.jpg` e a `legenda_post`.

## O que dá para controlar (roteiro.json)

**Nível do vídeo**

| Campo | Padrão | Efeito |
|---|---|---|
| `musica` | — | Trilha de fundo (repete em loop, entra e sai em fade, abaixa sozinha sob a voz). |
| `volume_musica` | `0.22` | 0.15 = discreta, 0.3 = presente. |
| `transicao` | `"fade"` | Transição padrão entre cenas. |
| `granulacao` | `6` | Grão de filme no vídeo todo (0 desliga, 10+ bem "película"). |
| `marca` | — | @ do canal, discreto no canto superior direito (dificulta repost). |
| `legenda` | ver abaixo | Estilo das legendas. |

`legenda` aceita: `fonte` ("Montserrat Black"), `tamanho` (82), `cor` ("#FFFFFF"), `cor_destaque` ("#FFD400" — palavra sendo falada), `contorno` (6), `altura` (640 = distância da borda de baixo; não use menos de ~550, a interface do TikTok cobre a parte de baixo), `max_palavras` (3), `max_letras` (18), `maiusculas` (true), `fonte_titulo` ("Playfair Display Black"), `tamanho_titulo` (74), `altura_titulo` (300).

**Nível da cena**: `visual`, `filtro` (`documentario` | `arquivo` | `pb` | `nenhum`), `movimento` (`zoom_in` | `zoom_out` | `pan_direita` | `pan_esquerda` | `pan_cima` | `pan_baixo` | `estatico`; sem ele, alterna automaticamente), `enquadramento` (`preencher` | `encaixar`), `transicao` (`fade` | `corte` | `fadeblack` | `dissolve` | `slideleft` | `wipeleft` | `circleopen` | `zoomin`), `texto_tela`, `efeito` (som que toca na entrada da cena), `volume_efeito` (0.6), `pausa` (silêncio após a fala, 0.25s), `inicio_clipe`.

## Linguagem de edição do canal

- **Gancho (cena 1)**: imagem mais forte, `zoom_in`, `texto_tela` curto, sem fade de entrada (o vídeo já abre na imagem).
- **Ritmo**: troca de visual a cada 3–6s. Cena com mais de 7s → dividir.
- **Revelação**: `"transicao": "corte"` + `efeito` de impacto (`assets/efeitos/impacto.mp3`) + `"pausa": 0.5` na cena anterior + `zoom_in`.
- **Salto no tempo** ("Anos depois..."): `"transicao": "fadeblack"`.
- **Cor conta a época**: fotos até ~1960 em `arquivo` ou `pb`; o "hoje" em `documentario`. Não misture sépia e PB na mesma sequência.
- **Música**: tensa, sem letra, com crescendo (piano grave, cordas, drones). Fontes sem direitos: biblioteca de áudio do YouTube, Pixabay Music, ou a própria biblioteca de sons comerciais do TikTok ao postar. Guarde em `assets/musicas/`.
- **Efeitos**: whoosh nas transições importantes, "boom"/impacto na revelação, máximo 3–4 por vídeo. Guarde em `assets/efeitos/`.
- **Fontes**: coloque os `.ttf` de Montserrat e Playfair Display (Google Fonts, licença livre) em `assets/fontes/`. Sem elas, o libass usa uma fonte substituta.

## Problemas comuns

- `arquivo não encontrado`: caminho de `visual`/`musica`/`efeito` é relativo à pasta do projeto ou à raiz do repositório.
- `cena N sem narração`: rode `python ferramentas/narrar.py projetos/<slug> --cenas N`.
- Legenda dessincronizada depois de editar o texto: a cena não foi renarrada.
- Imagem "tremendo" no zoom: imagem de baixa resolução; troque por uma maior.
- Vídeo maior que ~90s: corte texto no roteiro, não acelere a voz acima de +15%.
