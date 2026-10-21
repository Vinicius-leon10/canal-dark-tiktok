---
name: narracao-documentario
description: Gera a voz do narrador (TTS neural grátis, edge-tts) de cada cena do roteiro.json de um vídeo do canal de futebol, com tempos palavra a palavra para as legendas. Use quando o usuário pedir narração, voz, locução, áudio, trocar a voz, deixar a voz mais lenta/rápida/grave, ou regravar cenas.
---

# Narração estilo documentário

A ferramenta é `ferramentas/narrar.py` (usa `edge-tts`, vozes neurais da Microsoft, sem custo e sem chave de API — precisa de internet).

## Rodar

```bash
pip install -r requirements.txt                         # uma vez
python ferramentas/narrar.py projetos/<slug>            # narra todas as cenas
python ferramentas/narrar.py projetos/<slug> --cenas 2 7  # refaz só essas cenas
python ferramentas/narrar.py --vozes                    # lista vozes pt-BR / pt-PT
```

Gera `saida/audio/cena_XX.mp3` e `saida/narracao.json` (duração + tempo de cada palavra). O `montar_video.py` usa esse arquivo para sincronizar imagens e legendas, então **sempre que mudar o texto de uma cena, renarre essa cena**.

## Escolha da voz (campo `voz` no roteiro.json)

| Voz | Quando usar |
|---|---|
| `pt-BR-AntonioNeural` | **Padrão do canal.** Masculina, grave, séria — tom documentário. |
| `pt-BR-FranciscaNeural` | Feminina, clara. Bom para séries alternativas. |
| `pt-BR-ThalitaMultilingualNeural` | Feminina, mais expressiva. |

Mantenha **a mesma voz em todos os vídeos**: a voz vira a identidade do canal dark.

## Ajuste fino

No roteiro.json (vale para o vídeo todo) ou dentro de uma cena (só para ela):
- `velocidade`: `"+5%"` é o padrão. Documentário tenso: `"+0%"` a `"+5%"`. Lista rápida de fatos: `"+10%"` a `"+15%"`. Nunca acima de `+20%`.
- `tom`: `"-2Hz"` padrão (um pouco mais grave). Até `"-6Hz"` para mais sombrio; abaixo disso fica robótico.

Ritmo pela pontuação do texto:
- `.` pausa média, `...` pausa longa de suspense, `,` respiro curto.
- Para uma pausa dramática antes da revelação, termine a cena anterior com `...` e aumente `"pausa": 0.6` nessa cena (pausa é o silêncio depois da fala, em segundos; padrão 0.25).
- Pronúncia errada de nome estrangeiro: escreva foneticamente na `narracao` (ex.: "Guíguia" para Ghiggia). Atenção: a legenda mostra o texto como foi escrito, então a grafia fonética aparece na tela — só vale a pena quando a pronúncia estiver muito ruim.

## Conferir

Depois de narrar, mostre ao usuário a duração de cada cena e o total. Se passar de ~75s, sugira cortar frases na escalada (nunca no gancho nem na revelação). Se uma cena ficou com mais de 8s, sugira dividi-la em duas (com dois visuais).

## Sem internet / voz própria

Se o usuário gravar a própria voz ou usar outro TTS (ElevenLabs etc.), salve um arquivo por cena em `saida/audio/cena_XX.mp3` e crie `saida/narracao.json` com `{"1": {"audio": "saida/audio/cena_01.mp3", "duracao": 4.2, "texto": "...", "palavras": []}}`. Com `palavras` vazio, o montador distribui as legendas pelo tamanho das palavras (sincronia aproximada).
