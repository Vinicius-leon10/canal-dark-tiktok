#!/usr/bin/env python3
"""Gera a narração de cada cena do roteiro com edge-tts (vozes neurais grátis da Microsoft).

Uso:
    python ferramentas/narrar.py projetos/<slug>
    python ferramentas/narrar.py projetos/<slug> --cenas 3 5   # refaz só as cenas 3 e 5
    python ferramentas/narrar.py --vozes                       # lista vozes pt-BR

Lê  projetos/<slug>/roteiro.json
Gera projetos/<slug>/saida/audio/cena_XX.mp3
     projetos/<slug>/saida/narracao.json  (duração e tempo de cada palavra, usado nas legendas)
"""
import argparse
import asyncio
import json
import subprocess
import sys
from pathlib import Path

try:
    import edge_tts
except ImportError:
    sys.exit("edge-tts não instalado. Rode: pip install -r requirements.txt")

VOZ_PADRAO = "pt-BR-AntonioNeural"
VELOCIDADE_PADRAO = "+5%"
TOM_PADRAO = "-2Hz"


def duracao_audio(caminho: Path) -> float:
    saida = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(caminho)],
        capture_output=True, text=True, check=True,
    )
    return float(saida.stdout.strip())


async def narrar_cena(texto, voz, velocidade, tom, destino: Path):
    comunicador = edge_tts.Communicate(texto, voz, rate=velocidade, pitch=tom, boundary="WordBoundary")
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


async def listar_vozes():
    for voz in await edge_tts.list_voices():
        if voz["Locale"].startswith("pt-"):
            print(f'{voz["ShortName"]:28} {voz["Gender"]}')


async def principal(args):
    if args.vozes:
        await listar_vozes()
        return

    projeto = Path(args.projeto)
    roteiro = json.loads((projeto / "roteiro.json").read_text(encoding="utf-8"))
    voz = roteiro.get("voz", VOZ_PADRAO)
    velocidade = roteiro.get("velocidade", VELOCIDADE_PADRAO)
    tom = roteiro.get("tom", TOM_PADRAO)

    pasta_audio = projeto / "saida" / "audio"
    pasta_audio.mkdir(parents=True, exist_ok=True)
    arquivo_narracao = projeto / "saida" / "narracao.json"
    narracao = {}
    if arquivo_narracao.exists():
        narracao = json.loads(arquivo_narracao.read_text(encoding="utf-8"))

    for numero, cena in enumerate(roteiro["cenas"], start=1):
        if args.cenas and numero not in args.cenas:
            continue
        destino = pasta_audio / f"cena_{numero:02d}.mp3"
        texto = cena["narracao"].strip()
        palavras = await narrar_cena(
            texto, cena.get("voz", voz), cena.get("velocidade", velocidade), cena.get("tom", tom), destino
        )
        duracao = duracao_audio(destino)
        narracao[str(numero)] = {
            "audio": str(destino.relative_to(projeto)),
            "duracao": round(duracao, 3),
            "texto": texto,
            "palavras": palavras,
        }
        print(f"cena {numero:02d}: {duracao:5.2f}s  {texto[:60]}")

    arquivo_narracao.write_text(json.dumps(narracao, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(item["duracao"] for item in narracao.values())
    print(f"\nnarração total: {total:.1f}s -> {arquivo_narracao}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("projeto", nargs="?", help="pasta do projeto (contém roteiro.json)")
    parser.add_argument("--cenas", type=int, nargs="+", help="números das cenas a regerar")
    parser.add_argument("--vozes", action="store_true", help="lista as vozes em português")
    args = parser.parse_args()
    if not args.vozes and not args.projeto:
        parser.error("informe a pasta do projeto")
    asyncio.run(principal(args))
