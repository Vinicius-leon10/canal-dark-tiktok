---
name: video-futebol
description: Produz um vídeo completo do canal dark de futebol no TikTok, do tema ao MP4 final — roteiro documentário, visuais, narração, edição e texto de postagem. Use quando o usuário pedir "faz um vídeo sobre...", "novo vídeo", "produz o vídeo", ou quiser o fluxo inteiro de uma vez.
---

# Produção completa de um vídeo

Orquestra as outras skills na ordem. A visão do projeto, o ambiente e as decisões estão em `docs/PLANO.md` — leia antes. Mostre ao usuário o resultado de cada etapa em poucas linhas e siga adiante, a menos que ele peça para revisar antes.

1. **Tema** — se o usuário não deu um, sugira 3 pautas (veja a lista em `roteiro-futebol`), com o gancho de cada uma, e use a que ele escolher.
2. **Roteiro** — skill `roteiro-futebol`: pesquisa, checa os fatos, escreve e grava `projetos/<slug>/roteiro.json`. Mostre o roteiro corrido e a duração estimada. **Pare aqui para aprovação do texto** — é a etapa que mais muda o resultado e refazer depois custa narração e render.
3. **Visuais** — skill `imagens-futebol`: gere as imagens no Gemini Pro pelo navegador (e busque fotos de arquivo quando houver), salvando em `projetos/<slug>/imagens/`. Mostre a grade das imagens ao usuário. Se faltar algum visual, diga quais cenas faltam; não monte com buracos.
4. **Narração** — skill `narracao-documentario`: `python ferramentas/narrar.py projetos/<slug>` (ElevenLabs, com a voz do canal registrada em `docs/PLANO.md`).
5. **Prévia** — skill `edicao-documentario`: `--previa`, grade de quadros, revisão, ajustes.
6. **Final** — render 1080x1920 e entrega: `saida/<slug>.mp4`, `saida/capa.jpg`, legenda do post com hashtags, sugestão de horário (TikTok BR: 12h–14h e 19h–22h) e o comentário fixado (pergunta para engajar ou "Parte 2?").
7. **Checklist antes de postar** — mostre ao usuário marcado:
   - [ ] Números, datas e placares conferidos em duas fontes (estão em `fontes`)
   - [ ] Nenhuma imagem de TV ou de agência; `creditos.txt` preenchido se houver foto real
   - [ ] Música e efeitos livres de direitos
   - [ ] Legenda do post revisada (ortografia e nomes próprios)
   - [ ] Lembrete: marcar como conteúdo gerado por IA ao postar
8. **Registro** — depois que o usuário postar, grave no `roteiro.json` o campo `"publicado": {"data": "AAAA-MM-DD", "link": "https://..."}`. É a base da planilha de métricas da Fase 3.

## Estrutura do repositório

```
docs/PLANO.md                 ideia, fluxo, ambiente, regras e decisões do canal
ferramentas/narrar.py         voz por cena (ElevenLabs / edge-tts) -> saida/audio + saida/narracao.json
ferramentas/montar_video.py   edição e render -> saida/<slug>.mp4
assets/musicas/  assets/efeitos/  assets/fontes/   recursos reaproveitados em todos os vídeos
projetos/<slug>/roteiro.json  imagens/  saida/     um vídeo por pasta
projetos/exemplo-maracanazo/                       roteiro completo de referência
```

## Boas práticas de canal dark

- Constância > perfeição: 1 vídeo por dia no começo. Reaproveite estilo, voz, música e estrutura.
- Séries numeradas e "Parte 2" aumentam seguidores.
- Primeiros 3 segundos decidem tudo: gancho falado + imagem forte + texto na tela.
- Nunca use trechos de transmissão de TV ou fotos de agência — veja `imagens-futebol`.
- Marque o conteúdo como gerado por IA no TikTok quando usar imagens/voz de IA (regra da plataforma).
