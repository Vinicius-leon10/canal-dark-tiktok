# Canal dark de futebol no TikTok

Vídeos verticais (9:16, 45–75s) em formato documentário narrado: curiosidades, histórias e fatos históricos do futebol. Tudo em português do Brasil.

**Leia `docs/PLANO.md` antes de qualquer coisa** — tem a ideia completa, o fluxo de produção, o ambiente decidido (computador do usuário + navegador com Gemini Pro + ElevenLabs), as regras do canal e o checklist da primeira sessão local.

## Estado atual
- Pipeline de edição pronto e testado (`ferramentas/montar_video.py`).
- Narração com ElevenLabs implementada, testada só com resposta simulada — validar com a API real.
- Próximo passo: checklist da seção 4 do `docs/PLANO.md` (ambiente local, escolher voz, vídeo piloto do Maracanazo).

## Skills do projeto (.claude/skills/)
- `video-futebol` — fluxo completo do tema ao MP4 (use quando pedirem "um vídeo sobre X").
- `roteiro-futebol` — pesquisa, checagem de fatos e roteiro em cenas (`projetos/<slug>/roteiro.json`).
- `imagens-futebol` — imagens por cena: Gemini pelo navegador, fotos de arquivo, direitos autorais.
- `narracao-documentario` — voz (`ferramentas/narrar.py`, ElevenLabs ou edge-tts).
- `edicao-documentario` — montagem/render com ffmpeg (`ferramentas/montar_video.py`).

## Comandos
```bash
pip install -r requirements.txt
python ferramentas/narrar.py --vozes elevenlabs              # escolher voz
python ferramentas/narrar.py projetos/<slug>                 # narração (chave no .env)
python ferramentas/montar_video.py projetos/<slug> --previa  # rascunho 540x960
python ferramentas/montar_video.py projetos/<slug>           # final 1080x1920
```

## Regras
- Fatos checados e fontes em `roteiro.json` → `fontes`.
- Nada de trechos de TV ou fotos de agência; só domínio público, licença livre, IA ou stock grátis.
- Chaves de API só no `.env` local (está no .gitignore) ou em variáveis de ambiente; nunca no git nem no chat. Não abra nem mostre o `.env`.
- `projetos/*/saida/` não vai para o git (renders pesados).
- Ao tomar uma decisão nova com o usuário (voz, estilo, @ do canal), registre em `docs/PLANO.md` seção 10.
