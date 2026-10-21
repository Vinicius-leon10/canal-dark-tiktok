#!/usr/bin/env python3
"""Gera a narração de cada cena do roteiro, com o tempo de cada palavra (para as legendas).

Motores:
  elevenlabs  voz principal do canal (precisa de ELEVENLABS_API_KEY no ambiente)
  edge        reserva grátis (edge-tts, vozes neurais da Microsoft, sem chave)
Por padrão usa elevenlabs se a chave existir; senão, edge. Force com "motor" no roteiro.json ou --motor.

Uso:
    python ferramentas/narrar.py projetos/<slug>
    python ferramentas/narrar.py projetos/<slug> --cenas 3 5     # refaz só as cenas 3 e 5
    python ferramentas/narrar.py projetos/<slug> --motor edge
    python ferramentas/narrar.py --vozes elevenlabs              # lista vozes da sua conta ElevenLabs
    python ferramentas/narrar.py --vozes edge                    # lista vozes pt-BR do edge-tts

Lê  projetos/<slug>/roteiro.json
Gera projetos/<slug>/saida/audio/cena_XX.mp3
     projetos/<slug>/saida/narracao.json  (duração e tempo de cada palavra, usado nas legendas)
"""
import argparse
import asyncio
import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

URL_ELEVENLABS = "https://api.elevenlabs.io/v1"
MODELO_ELEVENLABS = "eleven_multilingual_v2"
AJUSTES_ELEVENLABS = {"stability": 0.5, "similarity_boost": 0.75, "style": 0.15, "use_speaker_boost": True}

VOZ_EDGE = "pt-BR-AntonioNeural"
VELOCIDADE_EDGE = "+5%"
TOM_EDGE = "-2Hz"


def duracao_audio(caminho: Path) -> float:
    saida = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(caminho)],
        capture_output=True, text=True, check=True,
    )
    return float(saida.stdout.strip())


# ---------------------------------------------------------------- ElevenLabs

def chave_elevenlabs():
    chave = os.environ.get("ELEVENLABS_API_KEY")
    if not chave:
        sys.exit("defina a variável de ambiente ELEVENLABS_API_KEY (ou use --motor edge)")
    return chave


def chamar_elevenlabs(caminho, corpo=None):
    pedido = urllib.request.Request(
        URL_ELEVENLABS + caminho,
        data=json.dumps(corpo).encode() if corpo is not None else None,
        headers={"xi-api-key": chave_elevenlabs(), "Content-Type": "application/json"},
        method="POST" if corpo is not None else "GET",
    )
    try:
        with urllib.request.urlopen(pedido, timeout=120) as resposta:
            return json.loads(resposta.read())
    except urllib.error.HTTPError as erro:
        sys.exit(f"ElevenLabs respondeu {erro.code}: {erro.read().decode(errors='replace')[:500]}")


def palavras_de_caracteres(alinhamento):
    """Junta os tempos por caractere da ElevenLabs em tempos por palavra."""
    palavras, atual = [], None
    for letra, inicio, fim in zip(alinhamento["characters"],
                                  alinhamento["character_start_times_seconds"],
                                  alinhamento["character_end_times_seconds"]):
        if letra.isspace():
            if atual:
                palavras.append(atual)
            atual = None
            continue
        if atual is None:
            atual = {"texto": "", "inicio": round(inicio, 3), "fim": round(fim, 3)}
        atual["texto"] += letra
        atual["fim"] = round(fim, 3)
    if atual:
        palavras.append(atual)
    return palavras


def narrar_elevenlabs(texto, config, destino: Path, texto_anterior="", texto_seguinte=""):
    voz = config.get("voz_elevenlabs") or os.environ.get("ELEVENLABS_VOICE_ID")
    if not voz:
        sys.exit("defina \"voz_elevenlabs\" (voice_id) no roteiro.json ou ELEVENLABS_VOICE_ID. "
                 "Liste as vozes com: python ferramentas/narrar.py --vozes elevenlabs")
    ajustes = {**AJUSTES_ELEVENLABS, **config.get("ajustes_elevenlabs", {})}
    corpo = {
        "text": texto,
        "model_id": config.get("modelo_elevenlabs", MODELO_ELEVENLABS),
        "voice_settings": ajustes,
        # contexto das cenas vizinhas: mantém a entonação contínua entre os arquivos
        "previous_text": texto_anterior,
        "next_text": texto_seguinte,
    }
    resposta = chamar_elevenlabs(f"/text-to-speech/{voz}/with-timestamps?output_format=mp3_44100_128", corpo)
    destino.write_bytes(base64.b64decode(resposta["audio_base64"]))
    alinhamento = resposta.get("alignment") or resposta.get("normalized_alignment")
    return palavras_de_caracteres(alinhamento) if alinhamento else []


def listar_vozes_elevenlabs():
    for voz in chamar_elevenlabs("/voices")["voices"]:
        rotulos = ", ".join(f"{v}" for v in (voz.get("labels") or {}).values())
        print(f'{voz["voice_id"]:24} {voz["name"]:28} {rotulos}')


# ---------------------------------------------------------------- edge-tts

def importar_edge():
    try:
        import edge_tts
    except ImportError:
        sys.exit("edge-tts não instalado. Rode: pip install -r requirements.txt")
    return edge_tts


async def narrar_edge(texto, config, destino: Path):
    edge_tts = importar_edge()
    comunicador = edge_tts.Communicate(
        texto, config.get("voz", VOZ_EDGE), rate=config.get("velocidade", VELOCIDADE_EDGE),
        pitch=config.get("tom", TOM_EDGE), boundary="WordBoundary",
    )
    palavras = []
    with open(destino, "wb") as arquivo:
        async for pedaco in comunicador.stream():
            if pedaco["type"] == "audio":
                arquivo.write(pedaco["data"])
            elif pedaco["type"] == "WordBoundary":
                inicio = pedaco["offset"] / 10_000_000
                palavras.append({
                    "texto": pedaco["text"],
                    "inicio": round(inicio, 3),
                    "fim": round(inicio + pedaco["duration"] / 10_000_000, 3),
                })
    return palavras


async def listar_vozes_edge():
    for voz in await importar_edge().list_voices():
        if voz["Locale"].startswith("pt-"):
            print(f'{voz["ShortName"]:28} {voz["Gender"]}')


# ---------------------------------------------------------------- principal

async def principal(args):
    if args.vozes:
        if args.vozes == "elevenlabs":
            listar_vozes_elevenlabs()
        else:
            await listar_vozes_edge()
        return

    projeto = Path(args.projeto)
    roteiro = json.loads((projeto / "roteiro.json").read_text(encoding="utf-8"))
    motor_padrao = args.motor or roteiro.get("motor") or ("elevenlabs" if os.environ.get("ELEVENLABS_API_KEY") else "edge")

    pasta_audio = projeto / "saida" / "audio"
    pasta_audio.mkdir(parents=True, exist_ok=True)
    arquivo_narracao = projeto / "saida" / "narracao.json"
    narracao = {}
    if arquivo_narracao.exists():
        narracao = json.loads(arquivo_narracao.read_text(encoding="utf-8"))

    cenas = roteiro["cenas"]
    for numero, cena in enumerate(cenas, start=1):
        if args.cenas and numero not in args.cenas:
            continue
        config = {**roteiro, **cena}
        motor = args.motor or cena.get("motor") or motor_padrao
        destino = pasta_audio / f"cena_{numero:02d}.mp3"
        texto = cena["narracao"].strip()
        if motor == "elevenlabs":
            anterior = cenas[numero - 2]["narracao"] if numero > 1 else ""
            seguinte = cenas[numero]["narracao"] if numero < len(cenas) else ""
            palavras = narrar_elevenlabs(texto, config, destino, anterior, seguinte)
        elif motor == "edge":
            palavras = await narrar_edge(texto, config, destino)
        else:
            sys.exit(f"motor desconhecido: {motor} (use elevenlabs ou edge)")
        duracao = duracao_audio(destino)
        narracao[str(numero)] = {
            "audio": str(destino.relative_to(projeto)),
            "duracao": round(duracao, 3),
            "texto": texto,
            "motor": motor,
            "palavras": palavras,
        }
        print(f"cena {numero:02d} [{motor}]: {duracao:5.2f}s  {texto[:60]}")

    arquivo_narracao.write_text(json.dumps(narracao, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(item["duracao"] for item in narracao.values())
    print(f"\nnarração total: {total:.1f}s -> {arquivo_narracao}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("projeto", nargs="?", help="pasta do projeto (contém roteiro.json)")
    parser.add_argument("--cenas", type=int, nargs="+", help="números das cenas a regerar")
    parser.add_argument("--motor", choices=["elevenlabs", "edge"], help="força o motor de voz")
    parser.add_argument("--vozes", choices=["elevenlabs", "edge"], help="lista as vozes disponíveis")
    args = parser.parse_args()
    if not args.vozes and not args.projeto:
        parser.error("informe a pasta do projeto")
    asyncio.run(principal(args))
