# Plano do projeto — Canal dark de futebol no TikTok

> Documento de referência. Qualquer sessão do Claude que pegar este projeto deve ler isto primeiro.

## 1. A ideia

Canal **dark** (sem rosto, sem o dono aparecendo) no TikTok sobre **futebol**, contando **curiosidades, histórias e fatos históricos** em **formato documentário**:

- Vídeo vertical 9:16, **45 a 75 segundos**.
- **Narração** grave e séria, estilo documentário (é a "voz" do canal).
- **Imagens** de época (fotos de arquivo) e **imagens geradas por IA** reconstituindo as cenas, com movimento de câmera lento, tratamento de cor de arquivo (sépia/PB) e grão de filme.
- **Legendas** grandes palavra a palavra (palavra falada em amarelo) + textos na tela com datas e lugares ("MARACANÃ, 1950").
- **Música** tensa de fundo, que abaixa sozinha quando o narrador fala, e efeitos sonoros pontuais.
- Objetivo: crescer o canal e **monetizar** (Programa de Criadores do TikTok, publis, afiliados). Por isso: conteúdo original, nada de trechos de TV.

Exemplo de tom (gancho): *"Quase duzentas mil pessoas. E, em um segundo, nenhuma delas conseguiu fazer barulho."*

## 2. Como cada vídeo é produzido

```
TEMA ──► ROTEIRO ──► (aprovação) ──► IMAGENS ──► NARRAÇÃO ──► PRÉVIA ──► AJUSTES ──► FINAL ──► POSTAGEM
         roteiro-futebol             imagens-     narracao-    edicao-documentario            (manual)
                                     futebol      documentario
```

| Etapa | Quem faz | Ferramenta | Saída |
|---|---|---|---|
| 1. Tema | Claude sugere 3, usuário escolhe | pesquisa web | — |
| 2. Roteiro | Claude, com checagem de fatos | skill `roteiro-futebol` | `projetos/<slug>/roteiro.json` |
| 3. Aprovação | **Usuário** aprova/ajusta o texto | — | roteiro final |
| 4. Imagens | Claude, pelo **navegador**, no **Gemini Pro** do usuário (+ fotos de arquivo) | skill `imagens-futebol` | `projetos/<slug>/imagens/01.png …` |
| 5. Narração | Claude, pela **API da ElevenLabs** | `ferramentas/narrar.py` | `saida/audio/*.mp3` + `saida/narracao.json` |
| 6. Prévia | Claude | `ferramentas/montar_video.py --previa` | `saida/previa.mp4` + grade de quadros para revisar |
| 7. Final | Claude | `ferramentas/montar_video.py` | `saida/<slug>.mp4` + `saida/capa.jpg` |
| 8. Postagem | **Usuário** posta no TikTok | — | legenda + hashtags + comentário fixado sugeridos pelo Claude |

Um vídeo = uma pasta em `projetos/<slug>/` (slug curto sem acento, ex.: `maracanazo-1950`). Os renders (`saida/`) não vão para o git.

## 3. Ambiente de trabalho (decidido)

As sessões de produção rodam **no computador do usuário**, com:

- **Navegador** (Claude in Chrome ou o navegador do app Claude) logado na conta Google do usuário com **Gemini Pro** → geração de imagens.
- **ElevenLabs** com chave de API → narração. A chave fica na variável de ambiente `ELEVENLABS_API_KEY` (nunca no git, nunca colada no chat). A voz escolhida fica em `voz_elevenlabs` no roteiro.json (ou `ELEVENLABS_VOICE_ID`).
- **ffmpeg** + **Python 3.10+** instalados localmente.
- **edge-tts** continua como reserva grátis de voz (`--motor edge`).

## 4. Primeira sessão no computador — checklist

Faça nesta ordem e marque aqui quando concluir:

- [ ] `git pull` deste repositório (branch com as skills).
- [ ] Verificar ferramentas: `ffmpeg -version`, `python --version` (3.10+). Instalar se faltar:
      Windows `winget install Gyan.FFmpeg Python.Python.3.12` · Mac `brew install ffmpeg python`.
- [ ] `pip install -r requirements.txt`
- [ ] Usuário define `ELEVENLABS_API_KEY` no ambiente (Windows: `setx ELEVENLABS_API_KEY "..."` e abrir um terminal novo; Mac: `export` no `~/.zshrc`).
- [ ] `python ferramentas/narrar.py --vozes elevenlabs` → escolher a voz do canal (masculina, grave, narrador; testar 2–3 vozes com a mesma frase do gancho). Gravar o voice_id em `voz_elevenlabs` no roteiro de exemplo e anotar aqui: **voz do canal = _______**.
- [ ] Baixar fontes (Google Fonts, licença livre) para `assets/fontes/`: **Montserrat** (Black) e **Playfair Display** (Black).
- [ ] Baixar 2–3 músicas tensas sem letra para `assets/musicas/` (YouTube Audio Library / Pixabay Music) e efeitos `whoosh.mp3` e `impacto.mp3` para `assets/efeitos/` (Pixabay).
- [ ] Testar o Gemini pelo navegador: gerar 1 imagem com o prompt de estilo (seção 6), baixar e conferir tamanho/proporção e marca d'água.
- [ ] Rodar o exemplo completo `projetos/exemplo-maracanazo` (imagens + narração + prévia + final) e ajustar o estilo até o usuário gostar. **Este é o vídeo piloto.**
- [ ] Definir @ do canal (`marca`) e atualizar no roteiro de exemplo.

## 5. Narração (ElevenLabs)

- Modelo padrão: `eleven_multilingual_v2` (bom em português). Configurável por `modelo_elevenlabs`.
- Endpoint `with-timestamps`: devolve o áudio + tempo de cada caractere → o script transforma em tempo por palavra para as legendas sincronizadas.
- Cada cena é um arquivo; o script manda o texto da cena anterior/seguinte (`previous_text`/`next_text`) para a entonação não "reiniciar" a cada cena.
- Ajuste fino em `ajustes_elevenlabs` no roteiro.json: `stability` (0.5; menor = mais emoção), `similarity_boost` (0.75), `style` (0.15), `speed` (1.0; 0.9–1.1).
- Custo: cobrado por caractere do plano da ElevenLabs. Um vídeo de 60s ≈ 900–1100 caracteres. Refazer só as cenas alteradas (`--cenas 3 5`) economiza créditos.
- ⚠️ A integração foi testada com resposta simulada, **ainda não contra a API real** — validar na primeira sessão.

## 6. Imagens (Gemini Pro pelo navegador)

Fluxo que o Claude executa no navegador:

1. Abrir `gemini.google.com` (conta do usuário, já logada).
2. Iniciar **uma conversa por vídeo** (ajuda a manter estilo consistente entre as cenas).
3. Para cada cena, enviar o prompt = **descrição da cena** + **prompt de estilo** abaixo, pedindo explicitamente **formato vertical 9:16**.
4. Baixar a imagem em tamanho máximo e mover da pasta Downloads para `projetos/<slug>/imagens/NN.png` (NN = número da cena).
5. Conferir: proporção vertical, sem texto/logos errados, sem rosto realista de jogador real identificável, marca d'água (se houver o ícone do Gemini num canto, garantir que a cena corte/cubra ou recortar).

Prompt de estilo do canal (manter igual em todos os vídeos):

```
Fotografia documental de arquivo dos anos 1950, preto e branco, granulação de filme,
iluminação dramática em claro-escuro, cinematográfica, atmosfera tensa e melancólica,
composição vertical 9:16, sem texto, sem logotipos.
```

Variações: época colorida (1970–90) → "foto colorida desbotada dos anos 1980, filme Kodachrome"; mistério → "neblina, silhueta, contra-luz, estádio vazio à noite".

Fotos reais de arquivo (credibilidade) complementam a IA: Wikimedia Commons, Nationaal Archief (CC0), Arquivo Nacional, Hemeroteca da Biblioteca Nacional. Registrar a origem em `projetos/<slug>/creditos.txt`.

Futuro (se quiser automatizar 100%): API do Gemini (Google AI Studio) com chave própria — é cobrada separadamente da assinatura Gemini Pro.

## 7. Edição (ffmpeg) — já pronto

`ferramentas/montar_video.py` — detalhes na skill `edicao-documentario`. Resumo do que já funciona (testado):
Ken Burns em fotos, clipes de vídeo, filtros `documentario`/`arquivo`/`pb`, enquadramento `encaixar` (foto horizontal com fundo desfocado), 8 tipos de transição sincronizados com a narração, legendas palavra a palavra, textos de tela, @ do canal, música com ducking, efeitos por cena, grão de filme, prévia rápida com cache, capa.jpg.

## 8. Regras do canal

1. **Fatos checados** e fontes no roteiro.json (`fontes`). Erro factual vira chacota nos comentários.
2. **Direitos autorais**: nada de transmissão de TV, lances de jogos recentes, fotos de agência (Getty/AP/Reuters), logotipos oficiais.
3. **IA**: marcar o vídeo como conteúdo gerado por IA no TikTok. Não gerar rosto realista de jogador vivo.
4. **Tragédias** (Superga, Chapecoense, Heysel…): tom respeitoso, sem detalhes gráficos.
5. **Consistência**: mesma voz, mesmo estilo de imagem, mesma legenda, mesma música-tema em todos os vídeos.
6. **Primeiros 3 segundos**: gancho falado + imagem mais forte + texto na tela.

## 9. Roadmap

- **Fase 1 — Piloto** (próxima sessão): ambiente local pronto, voz escolhida, vídeo do Maracanazo finalizado e aprovado pelo usuário.
- **Fase 2 — Primeiros 10 vídeos**: 1 por dia, ajustando estilo a partir do retorno (retenção, comentários). Lista de pautas inicial na skill `roteiro-futebol`.
- **Fase 3 — Escala**: séries ("Copas esquecidas #1…"), lote de roteiros por semana, automação das imagens (API) se o navegador ficar lento, planilha/registro de vídeos postados e métricas.

## 10. Decisões e histórico

| Data | Decisão |
|---|---|
| 2026-10-21 | Formato: documentário narrado, 45–75s, curiosidades/história do futebol. |
| 2026-10-21 | Pipeline em código (Python + ffmpeg) com skills do Claude Code; um projeto por pasta. |
| 2026-10-21 | Voz: ElevenLabs (principal) + edge-tts (reserva). Imagens: Gemini Pro pelo navegador + fotos de arquivo. |
| 2026-10-21 | Produção passa a rodar no computador do usuário (acesso a navegador e arquivos locais). |
