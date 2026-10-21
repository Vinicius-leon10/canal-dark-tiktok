#!/usr/bin/env python3
"""Monta o vídeo vertical (9:16) estilo documentário a partir do roteiro + narração.

Uso:
    python ferramentas/montar_video.py projetos/<slug>            # vídeo final 1080x1920
    python ferramentas/montar_video.py projetos/<slug> --previa   # rascunho rápido 540x960

Precisa de: roteiro.json, saida/narracao.json (gerado por narrar.py) e as imagens/clipes das cenas.
Gera:       saida/<slug>.mp4 (ou saida/previa.mp4), saida/capa.jpg e saida/legendas.ass

O que ele faz:
  * cada imagem vira uma cena com movimento de câmera (Ken Burns); clipes de vídeo são recortados para 9:16
  * tratamento de cor por cena (documentario / arquivo / pb / nenhum) com granulação e vinheta
  * transições entre cenas sincronizadas com a narração
  * legendas palavra a palavra com destaque na palavra falada + textos de tela (datas, lugares)
  * música de fundo que abaixa sozinha quando o narrador fala (ducking) + efeitos sonoros por cena
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FPS = 30

MOVIMENTOS = {
    # z = zoom, x/y = canto superior esquerdo do recorte; p = progresso 0..1
    "zoom_in": ("1+0.15*{p}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    "zoom_out": ("1.15-0.15*{p}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    "pan_direita": ("1.15", "(iw-iw/zoom)*{p}", "ih/2-(ih/zoom/2)"),
    "pan_esquerda": ("1.15", "(iw-iw/zoom)*(1-{p})", "ih/2-(ih/zoom/2)"),
    "pan_baixo": ("1.15", "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*{p}"),
    "pan_cima": ("1.15", "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*(1-{p})"),
    "estatico": ("1.02+0.03*{p}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
}
ROTACAO_MOVIMENTOS = ["zoom_in", "pan_direita", "zoom_out", "pan_esquerda", "zoom_in", "pan_cima"]

FILTROS = {
    "documentario": "eq=contrast=1.08:saturation=0.82:brightness=-0.02,vignette=PI/5",
    "arquivo": "hue=s=0,colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,"
               "eq=contrast=1.12:saturation=0.55,vignette=PI/4,noise=alls=10:allf=t",
    "pb": "hue=s=0,eq=contrast=1.22:brightness=-0.03,vignette=PI/4",
    "nenhum": "null",
}

TRANSICOES = {"corte": 0.04, "fade": 0.45, "fadeblack": 0.6, "dissolve": 0.45,
              "slideleft": 0.35, "wipeleft": 0.35, "circleopen": 0.5, "zoomin": 0.4}

EXTENSOES_VIDEO = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}


def rodar(comando, cwd=None):
    resultado = subprocess.run(comando, cwd=cwd, capture_output=True, text=True)
    if resultado.returncode != 0:
        print(" ".join(map(str, comando)), file=sys.stderr)
        print(resultado.stderr[-3000:], file=sys.stderr)
        sys.exit("ffmpeg falhou (veja o erro acima)")


def achar_arquivo(caminho, projeto: Path, obrigatorio=True):
    """Procura o arquivo relativo ao projeto e depois à raiz do repositório."""
    if not caminho:
        return None
    for base in (projeto, RAIZ):
        candidato = (base / caminho).resolve()
        if candidato.exists():
            return candidato
    if obrigatorio:
        sys.exit(f"arquivo não encontrado: {caminho}")
    print(f"aviso: {caminho} não encontrado, seguindo sem ele")
    return None


def cor_ass(hex_rgb, alfa="00"):
    hex_rgb = hex_rgb.lstrip("#")
    r, g, b = hex_rgb[0:2], hex_rgb[2:4], hex_rgb[4:6]
    return f"&H{alfa}{b}{g}{r}".upper()


def tempo_ass(segundos):
    segundos = max(0.0, segundos)
    h = int(segundos // 3600)
    m = int(segundos % 3600 // 60)
    s = segundos % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def limpar_ass(texto):
    return texto.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", " ")


# ---------------------------------------------------------------- cenas (vídeo)

def filtro_enquadramento(largura, altura, modo):
    cobrir = (f"scale={largura}:{altura}:force_original_aspect_ratio=increase,"
              f"crop={largura}:{altura},setsar=1")
    if modo != "encaixar":
        return cobrir
    # imagem inteira no centro + a mesma imagem desfocada preenchendo o fundo
    return (f"split[fundo][frente];"
            f"[fundo]{cobrir},boxblur=30:4,eq=brightness=-0.18[fundo2];"
            f"[frente]scale={largura}:{altura}:force_original_aspect_ratio=decrease,setsar=1[frente2];"
            f"[fundo2][frente2]overlay=(W-w)/2:(H-h)/2")


def renderizar_cena(cena, numero, duracao, visual: Path, destino: Path, largura, altura, previa):
    filtro_cor = FILTROS.get(cena.get("filtro", "documentario"))
    if filtro_cor is None:
        sys.exit(f"cena {numero}: filtro desconhecido '{cena['filtro']}'. Opções: {', '.join(FILTROS)}")
    enquadramento = cena.get("enquadramento", "preencher")
    quadros = max(2, round(duracao * FPS))

    if visual.suffix.lower() in EXTENSOES_VIDEO:
        entrada = ["-ss", str(cena.get("inicio_clipe", 0)), "-stream_loop", "-1", "-i", str(visual)]
        grafo = (f"[0:v]{filtro_enquadramento(largura, altura, enquadramento)},fps={FPS},"
                 f"{filtro_cor},format=yuv420p[v]")
    else:
        movimento = cena.get("movimento") or ROTACAO_MOVIMENTOS[(numero - 1) % len(ROTACAO_MOVIMENTOS)]
        if movimento not in MOVIMENTOS:
            sys.exit(f"cena {numero}: movimento desconhecido '{movimento}'. Opções: {', '.join(MOVIMENTOS)}")
        progresso = f"(on/{quadros - 1})"
        z, x, y = (parte.format(p=progresso) for parte in MOVIMENTOS[movimento])
        # trabalha em 2x a resolução final para o movimento não "tremer"
        entrada = ["-i", str(visual)]
        grafo = (f"[0:v]{filtro_enquadramento(largura * 2, altura * 2, enquadramento)},"
                 f"zoompan=z='{z}':x='{x}':y='{y}':d={quadros}:s={largura}x{altura}:fps={FPS},"
                 f"{filtro_cor},format=yuv420p[v]")

    rodar(["ffmpeg", "-y", "-loglevel", "error", *entrada, "-filter_complex", grafo, "-map", "[v]",
           "-t", f"{duracao:.3f}", "-r", str(FPS), "-an", "-c:v", "libx264",
           "-preset", "ultrafast", "-crf", "20" if previa else "16", str(destino)])


def assinatura_cena(*partes):
    return hashlib.sha1(json.dumps(partes, sort_keys=True, default=str).encode()).hexdigest()


# ---------------------------------------------------------------- legendas

def palavras_da_cena(info):
    """Palavras com tempo; se o TTS não mandou os tempos, distribui pelo tamanho das palavras."""
    if info.get("palavras"):
        return info["palavras"]
    textos = info["texto"].split()
    total_letras = sum(len(t) for t in textos) or 1
    cursor, palavras = 0.0, []
    for texto in textos:
        fatia = info["duracao"] * len(texto) / total_letras
        palavras.append({"texto": texto, "inicio": cursor, "fim": cursor + fatia})
        cursor += fatia
    return palavras


def agrupar(palavras, max_palavras, max_letras):
    grupos, atual = [], []
    for palavra in palavras:
        letras = sum(len(p["texto"]) + 1 for p in atual) + len(palavra["texto"])
        pausa = atual and palavra["inicio"] - atual[-1]["fim"] > 0.3
        if atual and (len(atual) >= max_palavras or letras > max_letras or pausa):
            grupos.append(atual)
            atual = []
        atual.append(palavra)
        if palavra["texto"].rstrip()[-1:] in ".!?;:":
            grupos.append(atual)
            atual = []
    if atual:
        grupos.append(atual)
    return grupos


def gerar_ass(roteiro, cenas, destino: Path):
    cfg = {"fonte": "Montserrat Black", "tamanho": 82, "cor": "#FFFFFF", "cor_destaque": "#FFD400",
           "contorno": 6, "altura": 640, "max_palavras": 3, "max_letras": 18, "maiusculas": True,
           "fonte_titulo": "Playfair Display Black", "tamanho_titulo": 74, "altura_titulo": 300}
    cfg.update(roteiro.get("legenda", {}))
    marca = roteiro.get("marca")

    linhas = [
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920",
        "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
        "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Legenda,{cfg['fonte']},{cfg['tamanho']},{cor_ass(cfg['cor'])},{cor_ass(cfg['cor_destaque'])},"
        f"&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,{cfg['contorno']},3,2,90,90,{cfg['altura']},1",
        f"Style: Titulo,{cfg['fonte_titulo']},{cfg['tamanho_titulo']},&H00FFFFFF,&H00FFFFFF,"
        f"&H00000000,&H64000000,-1,0,0,0,100,100,4,0,1,3,4,8,80,80,{cfg['altura_titulo']},1",
        "Style: Marca,DejaVu Sans,34,&H50FFFFFF,&H00FFFFFF,&H00000000,&H00000000,"
        "0,0,0,0,100,100,1,0,1,1,0,9,40,60,120,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    destaque = cor_ass(cfg["cor_destaque"])

    for cena in cenas:
        inicio_cena = cena["inicio"]
        if cena["texto_tela"]:
            fim = inicio_cena + min(cena["duracao"], 3.2)
            texto = limpar_ass(cena["texto_tela"]).upper()
            linhas.append(f"Dialogue: 1,{tempo_ass(inicio_cena + 0.15)},{tempo_ass(fim)},Titulo,,0,0,0,,"
                          f"{{\\fad(350,350)}}{texto}")

        grupos = agrupar(palavras_da_cena(cena["narracao"]), cfg["max_palavras"], cfg["max_letras"])
        for indice_grupo, grupo in enumerate(grupos):
            proximo = grupos[indice_grupo + 1][0]["inicio"] if indice_grupo + 1 < len(grupos) else None
            fim_grupo = grupo[-1]["fim"] + 0.25
            if proximo is not None:
                fim_grupo = min(fim_grupo, proximo)
            fim_grupo = min(fim_grupo, cena["duracao"])
            textos = [limpar_ass(p["texto"]) for p in grupo]
            if cfg["maiusculas"]:
                textos = [t.upper() for t in textos]
            for i, palavra in enumerate(grupo):
                ini = palavra["inicio"]
                fim = grupo[i + 1]["inicio"] if i + 1 < len(grupo) else fim_grupo
                if fim <= ini:
                    continue
                partes = [
                    f"{{\\c{destaque}\\fscx108\\fscy108}}{t}{{\\r}}" if j == i else t
                    for j, t in enumerate(textos)
                ]
                pop = "{\\fscx92\\fscy92\\t(0,80,\\fscx100\\fscy100)}" if i == 0 else ""
                linhas.append(f"Dialogue: 0,{tempo_ass(inicio_cena + ini)},{tempo_ass(inicio_cena + fim)},"
                              f"Legenda,,0,0,0,,{pop}{' '.join(partes)}")

    if marca:
        total = cenas[-1]["inicio"] + cenas[-1]["duracao"]
        linhas.append(f"Dialogue: 2,{tempo_ass(0)},{tempo_ass(total)},Marca,,0,0,0,,{limpar_ass(marca)}")

    destino.write_text("\n".join(linhas) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- montagem final

def principal(args):
    projeto = Path(args.projeto).resolve()
    roteiro = json.loads((projeto / "roteiro.json").read_text(encoding="utf-8"))
    arquivo_narracao = projeto / "saida" / "narracao.json"
    if not arquivo_narracao.exists():
        sys.exit("saida/narracao.json não existe. Rode antes: python ferramentas/narrar.py " + args.projeto)
    narracao = json.loads(arquivo_narracao.read_text(encoding="utf-8"))

    largura, altura = (540, 960) if args.previa else (1080, 1920)
    saida = projeto / "saida"
    temporarios = saida / ("tmp_previa" if args.previa else "tmp")
    temporarios.mkdir(parents=True, exist_ok=True)

    # 1) tempos de cada cena (narração + respiro) e transições
    cenas, inicio = [], 0.0
    for numero, cena in enumerate(roteiro["cenas"], start=1):
        info = narracao.get(str(numero))
        if not info:
            sys.exit(f"cena {numero} sem narração. Rode: python ferramentas/narrar.py {args.projeto} --cenas {numero}")
        duracao = info["duracao"] + float(cena.get("pausa", 0.25))
        cenas.append({"numero": numero, "dados": cena, "narracao": info, "inicio": inicio,
                      "duracao": duracao, "texto_tela": cena.get("texto_tela"),
                      "audio": projeto / info["audio"]})
        inicio += duracao
    total = inicio
    for atual, seguinte in zip(cenas, cenas[1:]):
        tipo = seguinte["dados"].get("transicao", roteiro.get("transicao", "fade"))
        if tipo not in TRANSICOES:
            sys.exit(f"cena {seguinte['numero']}: transição desconhecida '{tipo}'. Opções: {', '.join(TRANSICOES)}")
        atual["saida_transicao"] = (tipo, TRANSICOES[tipo])
    cenas[-1]["saida_transicao"] = None

    # 2) renderiza cada cena (com cache: só refaz o que mudou)
    for cena in cenas:
        visual = achar_arquivo(cena["dados"].get("visual"), projeto)
        if visual is None:
            sys.exit(f"cena {cena['numero']}: falta o campo 'visual' (imagem ou clipe)")
        extra = cena["saida_transicao"][1] if cena["saida_transicao"] else 0.0
        comprimento = cena["duracao"] + extra
        destino = temporarios / f"cena_{cena['numero']:02d}.mp4"
        marca_cache = destino.with_suffix(".hash")
        hash_atual = assinatura_cena(cena["dados"], comprimento, str(visual), visual.stat().st_mtime,
                                     largura, FILTROS, MOVIMENTOS)
        if destino.exists() and marca_cache.exists() and marca_cache.read_text() == hash_atual:
            print(f"cena {cena['numero']:02d}: em cache")
            continue
        print(f"cena {cena['numero']:02d}: renderizando {comprimento:.2f}s ({visual.name})")
        renderizar_cena(cena["dados"], cena["numero"], comprimento, visual, destino, largura, altura, args.previa)
        marca_cache.write_text(hash_atual)

    # 3) legendas
    arquivo_ass = saida / "legendas.ass"
    gerar_ass(roteiro, cenas, arquivo_ass)

    # 4) grafo final: transições + legendas + áudio
    entradas, filtros = [], []
    for cena in cenas:
        entradas += ["-i", str(temporarios / f"cena_{cena['numero']:02d}.mp4")]
    rotulo = "[0:v]"
    for i, cena in enumerate(cenas[:-1]):
        tipo, duracao_t = cena["saida_transicao"]
        proximo = cenas[i + 1]
        novo = f"[x{i}]"
        filtros.append(f"{rotulo}[{i + 1}:v]xfade=transition={tipo if tipo != 'corte' else 'fade'}:"
                       f"duration={duracao_t}:offset={proximo['inicio']:.3f}{novo}")
        rotulo = novo
    pasta_fontes = os.path.relpath(RAIZ / "assets" / "fontes", saida)
    fim_fade = max(0.0, total - 0.6)
    granulacao = int(roteiro.get("granulacao", 6))
    grao = f"noise=alls={granulacao}:allf=t," if granulacao > 0 else ""
    filtros.append(f"{rotulo}{grao}ass=legendas.ass:fontsdir={pasta_fontes},"
                   f"fade=t=out:st={fim_fade:.3f}:d=0.6,format=yuv420p[vfinal]")

    n = len(cenas)
    for i, cena in enumerate(cenas):
        entradas += ["-i", str(cena["audio"])]
        filtros.append(f"[{n + i}:a]aresample=48000,aformat=channel_layouts=stereo,apad,"
                       f"atrim=0:{cena['duracao']:.3f},asetpts=PTS-STARTPTS[a{i}]")
    filtros.append("".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1,"
                   "highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=90,"
                   "loudnorm=I=-15:TP=-1.5:LRA=11,aresample=48000[voz]")
    proxima_entrada = 2 * n
    trilhas = []

    musica = achar_arquivo(roteiro.get("musica"), projeto, obrigatorio=False)
    if musica:
        volume = float(roteiro.get("volume_musica", 0.22))
        entradas += ["-stream_loop", "-1", "-i", str(musica)]
        filtros.append("[voz]asplit=2[voz1][vozsc]")
        filtros.append(f"[{proxima_entrada}:a]aresample=48000,aformat=channel_layouts=stereo,"
                       f"atrim=0:{total:.3f},volume={volume},afade=t=in:d=1.5,"
                       f"afade=t=out:st={max(0, total - 2.5):.3f}:d=2.5[mus]")
        filtros.append("[mus][vozsc]sidechaincompress=threshold=0.04:ratio=6:attack=30:release=500[musduck]")
        trilhas += ["[voz1]", "[musduck]"]
        proxima_entrada += 1
    else:
        trilhas.append("[voz]")

    for cena in cenas:
        efeito = achar_arquivo(cena["dados"].get("efeito"), projeto, obrigatorio=False)
        if not efeito:
            continue
        atraso = int(max(0.0, cena["inicio"] - 0.15) * 1000)
        volume_efeito = float(cena["dados"].get("volume_efeito", 0.6))
        entradas += ["-i", str(efeito)]
        filtros.append(f"[{proxima_entrada}:a]aresample=48000,aformat=channel_layouts=stereo,"
                       f"volume={volume_efeito},adelay={atraso}|{atraso}[ef{proxima_entrada}]")
        trilhas.append(f"[ef{proxima_entrada}]")
        proxima_entrada += 1

    filtros.append("".join(trilhas) + f"amix=inputs={len(trilhas)}:normalize=0:duration=first,"
                   f"alimiter=limit=0.95,afade=t=out:st={fim_fade:.3f}:d=0.6[afinal]")

    nome = "previa.mp4" if args.previa else f"{projeto.name}.mp4"
    destino = saida / nome
    print("montando vídeo final...")
    rodar(["ffmpeg", "-y", "-loglevel", "error", *entradas,
           "-filter_complex", ";".join(filtros), "-map", "[vfinal]", "-map", "[afinal]",
           "-t", f"{total:.3f}", "-r", str(FPS), "-c:v", "libx264",
           "-preset", "veryfast" if args.previa else "medium", "-crf", "26" if args.previa else "19",
           "-profile:v", "high", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", destino.name], cwd=saida)

    rodar(["ffmpeg", "-y", "-loglevel", "error", "-ss", "0.8", "-i", str(destino),
           "-frames:v", "1", "-q:v", "2", str(saida / "capa.jpg")])
    if not args.manter_temporarios and not args.previa:
        shutil.rmtree(temporarios, ignore_errors=True)
    print(f"\npronto: {destino}  ({total:.1f}s, {len(cenas)} cenas)")
    if total > 90:
        print("aviso: passou de 90s — para vídeos dark de curiosidade, 45–75s costuma reter melhor.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("projeto", help="pasta do projeto (contém roteiro.json)")
    parser.add_argument("--previa", action="store_true", help="render rápido em 540x960 para conferir")
    parser.add_argument("--manter-temporarios", action="store_true", help="não apaga as cenas renderizadas")
    principal(parser.parse_args())
