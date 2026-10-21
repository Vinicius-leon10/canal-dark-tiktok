---
name: narracao-documentario
description: Gera a voz do narrador (ElevenLabs; edge-tts como reserva grátis) de cada cena do roteiro.json de um vídeo do canal de futebol, com tempos palavra a palavra para as legendas. Use quando o usuário pedir narração, voz, locução, áudio, trocar a voz, deixar a voz mais lenta/rápida/grave/emocionante, ou regravar cenas.
---

# Narração estilo documentário

A ferramenta é `ferramentas/narrar.py`. Motor principal: **ElevenLabs** (chave `ELEVENLABS_API_KEY` no arquivo `.env` da raiz — modelo em `.env.exemplo` — ou no ambiente). Reserva grátis: **edge-tts** (`--motor edge`, sem chave).

## Rodar

```bash
python ferramentas/narrar.py projetos/<slug>              # narra todas as cenas
python ferramentas/narrar.py projetos/<slug> --cenas 2 7  # refaz só essas cenas (economiza créditos)
python ferramentas/narrar.py projetos/<slug> --motor edge # força a voz grátis
python ferramentas/narrar.py --vozes elevenlabs           # lista as vozes da conta ElevenLabs
python ferramentas/narrar.py --vozes edge                 # lista vozes pt-BR do edge-tts
```

Gera `saida/audio/cena_XX.mp3` e `saida/narracao.json` (duração + tempo de cada palavra). O `montar_video.py` usa esse arquivo para sincronizar imagens e legendas, então **sempre que mudar o texto de uma cena, renarre essa cena**.

Se a chave não estiver definida, peça ao usuário para copiar `.env.exemplo` para `.env` e preencher a chave ele mesmo. Nunca peça a chave no chat e não abra/mostre o `.env`.

## ElevenLabs

Campos no roteiro.json (nível do vídeo; também valem dentro de uma cena):
- `voz_elevenlabs`: voice_id da voz do canal (está registrado em `docs/PLANO.md`). **Mesma voz em todos os vídeos** — ela é a identidade do canal.
- `modelo_elevenlabs`: padrão `eleven_multilingual_v2`.
- `ajustes_elevenlabs`: `stability` (0.5 — menor deixa mais emotivo, maior mais estável), `similarity_boost` (0.75), `style` (0.15 — mais alto = mais dramático, custa estabilidade), `speed` (1.0; use 0.9–1.1).

Escolher a voz: liste com `--vozes elevenlabs`, gere a frase do gancho com 2–3 candidatas (narração masculina, grave, "documentary/narrator/deep") e deixe o usuário escolher ouvindo. Registre a escolha em `docs/PLANO.md`.

O script envia o texto das cenas vizinhas como contexto, então a entonação fica contínua mesmo com um arquivo por cena. Custo ≈ caracteres do roteiro (~1.000 por vídeo de 60s).

## edge-tts (reserva)

Campos: `voz` (padrão `pt-BR-AntonioNeural`), `velocidade` (`"+5%"`), `tom` (`"-2Hz"`, até `"-6Hz"` para mais sombrio).

## Ritmo pela escrita

- `.` pausa média, `...` pausa longa de suspense, `,` respiro curto.
- Pausa dramática antes da revelação: termine a cena anterior com `...` e use `"pausa": 0.6` nela (silêncio depois da fala, em segundos; padrão 0.25).
- Pronúncia errada de nome estrangeiro: escreva foneticamente na `narracao` (ex.: "Guíguia" para Ghiggia). A legenda mostra o texto como foi escrito, então só vale quando a pronúncia estiver muito ruim.

## Conferir

Depois de narrar, mostre a duração de cada cena e o total. Se passar de ~75s, sugira cortar frases na escalada (nunca no gancho nem na revelação). Cena com mais de 8s → sugerir dividir em duas (com dois visuais).

## Voz gravada ou outro TTS

Salve um arquivo por cena em `saida/audio/cena_XX.mp3` e crie `saida/narracao.json` com `{"1": {"audio": "saida/audio/cena_01.mp3", "duracao": 4.2, "texto": "...", "palavras": []}}`. Com `palavras` vazio, o montador distribui as legendas pelo tamanho das palavras (sincronia aproximada).
