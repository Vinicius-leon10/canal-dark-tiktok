# canal-dark-tiktok

Canal dark de futebol para o TikTok: vídeos curtos estilo documentário, com narração, contando curiosidades e fatos históricos do futebol.

Produção semiautomática com Claude Code + ffmpeg:

1. **Roteiro** com gancho, escalada e revelação, dividido em cenas (`projetos/<slug>/roteiro.json`).
2. **Visuais** por cena (fotos de domínio público, IA ou stock) em `projetos/<slug>/imagens/`.
3. **Narração** com voz neural grátis (`ferramentas/narrar.py`, edge-tts).
4. **Edição** automática (`ferramentas/montar_video.py`): Ken Burns, filtro de arquivo/sépia/PB, grão de filme, transições, legendas palavra a palavra, textos de tela, música com ducking e efeitos.

## Começar

```bash
# requisitos: Python 3.10+ e ffmpeg (brew install ffmpeg / sudo apt install ffmpeg / winget install ffmpeg)
pip install -r requirements.txt
```

No Claude Code, peça: **"faz um vídeo sobre a Guerra do Futebol de 1969"** — a skill `video-futebol` conduz o resto.

Manual:
```bash
python ferramentas/narrar.py projetos/exemplo-maracanazo
python ferramentas/montar_video.py projetos/exemplo-maracanazo --previa
python ferramentas/montar_video.py projetos/exemplo-maracanazo
```
(o exemplo precisa das imagens `01.jpg`…`12.jpg` em `projetos/exemplo-maracanazo/imagens/` — veja `descricao_visual` em cada cena.)

## Recursos para baixar uma vez
- `assets/fontes/`: Montserrat (Black) e Playfair Display (Black) — Google Fonts.
- `assets/musicas/tensao.mp3`: trilha tensa sem letra (YouTube Audio Library / Pixabay Music).
- `assets/efeitos/whoosh.mp3` e `impacto.mp3`: Pixabay Sound Effects.
