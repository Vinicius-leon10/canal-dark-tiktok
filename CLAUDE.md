# Canal dark de futebol no TikTok

Vídeos verticais (9:16, 45–75s) em formato documentário narrado: curiosidades, histórias e fatos históricos do futebol. Tudo em português do Brasil.

## Skills do projeto (.claude/skills/)
- `video-futebol` — fluxo completo do tema ao MP4 (use esta quando pedirem "um vídeo sobre X").
- `roteiro-futebol` — pesquisa, checagem de fatos e roteiro em cenas (`projetos/<slug>/roteiro.json`).
- `imagens-futebol` — visuais por cena, prompts de IA e cuidados com direitos autorais.
- `narracao-documentario` — voz TTS (`ferramentas/narrar.py`).
- `edicao-documentario` — montagem/render com ffmpeg (`ferramentas/montar_video.py`).

## Comandos
```bash
pip install -r requirements.txt                              # edge-tts (ffmpeg precisa estar instalado)
python ferramentas/narrar.py projetos/<slug>
python ferramentas/montar_video.py projetos/<slug> --previa
python ferramentas/montar_video.py projetos/<slug>
```

## Regras
- Fatos checados e fontes em `roteiro.json` → `fontes`.
- Nada de trechos de TV ou fotos de agência; só domínio público, licença livre, IA ou stock grátis.
- `projetos/*/saida/` não vai para o git (renders pesados).
