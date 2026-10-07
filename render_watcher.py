"""Monitora a pasta de exportacao do Revit e gera renders arquitetonicos com IA.

Fluxo:
  1. O Revit (botao/hook do pyRevit) exporta as vistas cujo nome comeca com o
     prefixo configurado (ex.: RENDER_Fachada) como PNG para `pasta_entrada`.
  2. Este script encontra essas imagens, envia para a API "Control - Structure"
     da Stability AI (preserva a geometria da vista e aplica materiais/luz) e
     salva o resultado em `pasta_saida` como <nome>_render.png.

Uso:
  set STABILITY_API_KEY=sk-...
  python render_watcher.py --config C:\\RenderIA\\config.json          # fica monitorando
  python render_watcher.py --config C:\\RenderIA\\config.json --once   # roda uma vez e sai
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

STABILITY_URL = "https://api.stability.ai/v2beta/stable-image/control/structure"
EXTENSOES = {".png", ".jpg", ".jpeg"}

DEFAULTS = {
    "pasta_entrada": "entrada",
    "pasta_saida": "saida",
    "prefixo": "RENDER_",
    "control_strength": 0.75,
    "intervalo_segundos": 5,
    "prompt_padrao": "photorealistic architectural render, natural daylight, realistic materials, high detail",
    "negative_prompt": "cartoon, sketch, blurry, distorted geometry, text, watermark",
    "prompts_por_nome": {},
}


def carregar_config(caminho: Path) -> dict:
    config = dict(DEFAULTS)
    if caminho.exists():
        with caminho.open(encoding="utf-8") as f:
            config.update(json.load(f))
    else:
        print(f"[aviso] {caminho} nao encontrado, usando configuracao padrao.")
    base = caminho.parent
    for chave in ("pasta_entrada", "pasta_saida"):
        pasta = Path(config[chave])
        config[chave] = pasta if pasta.is_absolute() else base / pasta
    return config


def nome_da_vista(arquivo: Path, prefixo: str) -> str | None:
    """Extrai o nome apos o prefixo.

    O Revit nomeia o PNG como "<prefixo do arquivo> - <tipo de vista> - <nome da vista>.png",
    entao procuramos o prefixo em qualquer parte do nome.
    Ex.: "RenderIA - Vista 3D - RENDER_Fachada.png" -> "Fachada".
    """
    stem = arquivo.stem
    pos = stem.upper().find(prefixo.upper())
    if pos < 0:
        return None
    return stem[pos + len(prefixo):].strip() or stem


def arquivo_estavel(arquivo: Path, espera: float = 1.0) -> bool:
    """Evita ler a imagem enquanto o Revit ainda esta gravando."""
    tamanho = arquivo.stat().st_size
    time.sleep(espera)
    return tamanho > 0 and arquivo.stat().st_size == tamanho


def precisa_renderizar(origem: Path, destino: Path) -> bool:
    return not destino.exists() or destino.stat().st_mtime < origem.stat().st_mtime


def renderizar(origem: Path, destino: Path, prompt: str, config: dict, api_key: str) -> None:
    with origem.open("rb") as imagem:
        resposta = requests.post(
            STABILITY_URL,
            headers={"Authorization": f"Bearer {api_key}", "Accept": "image/*"},
            files={"image": imagem},
            data={
                "prompt": prompt,
                "negative_prompt": config["negative_prompt"],
                "control_strength": config["control_strength"],
                "output_format": "png",
            },
            timeout=180,
        )
    if resposta.status_code != 200:
        raise RuntimeError(f"Stability AI retornou {resposta.status_code}: {resposta.text[:500]}")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(resposta.content)


def processar_pasta(config: dict, api_key: str, abrir: bool = False) -> int:
    entrada: Path = config["pasta_entrada"]
    saida: Path = config["pasta_saida"]
    entrada.mkdir(parents=True, exist_ok=True)
    feitos = 0
    for origem in sorted(entrada.iterdir()):
        if origem.suffix.lower() not in EXTENSOES:
            continue
        vista = nome_da_vista(origem, config["prefixo"])
        if vista is None:
            continue
        destino = saida / f"{origem.stem}_render.png"
        if not precisa_renderizar(origem, destino) or not arquivo_estavel(origem):
            continue
        prompt = config["prompts_por_nome"].get(vista, config["prompt_padrao"])
        print(f"[render] {origem.name} -> {destino.name}")
        try:
            renderizar(origem, destino, prompt, config, api_key)
            feitos += 1
            if abrir and hasattr(os, "startfile"):
                os.startfile(destino)
        except (RuntimeError, requests.RequestException) as erro:
            print(f"[erro] {origem.name}: {erro}")
    return feitos


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", default="config.json", help="caminho do config.json")
    parser.add_argument("--once", action="store_true", help="processa a pasta uma vez e sai")
    parser.add_argument("--abrir", action="store_true", help="abre cada render gerado (Windows)")
    args = parser.parse_args()

    api_key = os.environ.get("STABILITY_API_KEY")
    if not api_key:
        print("Defina a variavel de ambiente STABILITY_API_KEY (https://platform.stability.ai/account/keys).")
        return 1

    config = carregar_config(Path(args.config).resolve())
    print(f"Monitorando {config['pasta_entrada']} (prefixo '{config['prefixo']}')")

    if args.once:
        print(f"{processar_pasta(config, api_key, args.abrir)} imagem(ns) renderizada(s).")
        return 0

    try:
        while True:
            processar_pasta(config, api_key, args.abrir)
            time.sleep(config["intervalo_segundos"])
    except KeyboardInterrupt:
        print("Encerrado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
