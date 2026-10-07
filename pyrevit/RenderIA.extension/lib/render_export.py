# -*- coding: utf-8 -*-
"""Exporta para PNG as vistas do Revit cujo nome comeca com o prefixo (ex.: RENDER_).

Compativel com IronPython 2.7 (motor padrao do pyRevit) e CPython.
A configuracao fica em C:\\RenderIA\\config.json (mesmo arquivo usado pelo render_watcher.py).
"""
import io
import json
import os

import clr
clr.AddReference("System")
from System.Collections.Generic import List

from Autodesk.Revit.DB import (
    ElementId,
    ExportRange,
    FilteredElementCollector,
    FitDirectionType,
    ImageExportOptions,
    ImageFileType,
    ImageResolution,
    View,
    ZoomFitType,
)

CONFIG_PATH = os.environ.get("RENDERIA_CONFIG", r"C:\RenderIA\config.json")

DEFAULTS = {
    "pasta_entrada": r"C:\RenderIA\entrada",
    "prefixo": "RENDER_",
    "largura_px": 1920,
    "exportar_ao_salvar": False,
}


def carregar_config():
    config = dict(DEFAULTS)
    if os.path.exists(CONFIG_PATH):
        with io.open(CONFIG_PATH, encoding="utf-8") as f:
            config.update(json.load(f))
    pasta = config["pasta_entrada"]
    if not os.path.isabs(pasta):
        pasta = os.path.join(os.path.dirname(CONFIG_PATH), pasta)
    config["pasta_entrada"] = pasta
    return config


def vistas_marcadas(doc, prefixo):
    vistas = []
    for vista in FilteredElementCollector(doc).OfClass(View):
        if vista.IsTemplate or not vista.CanBePrinted:
            continue
        if vista.Name.upper().startswith(prefixo.upper()):
            vistas.append(vista)
    return vistas


def exportar_vistas(doc, config=None):
    """Exporta as vistas marcadas e devolve a lista de nomes exportados."""
    config = config or carregar_config()
    vistas = vistas_marcadas(doc, config["prefixo"])
    if not vistas:
        return []

    pasta = config["pasta_entrada"]
    if not os.path.isdir(pasta):
        os.makedirs(pasta)

    opcoes = ImageExportOptions()
    opcoes.ExportRange = ExportRange.SetOfViews
    opcoes.SetViewsAndSheets(List[ElementId]([v.Id for v in vistas]))
    # O Revit gera "<FilePath> - <tipo de vista> - <nome da vista>.png"
    opcoes.FilePath = os.path.join(pasta, "RenderIA")
    opcoes.ZoomType = ZoomFitType.FitToPage
    opcoes.FitDirection = FitDirectionType.Horizontal
    opcoes.PixelSize = int(config["largura_px"])
    opcoes.ImageResolution = ImageResolution.DPI_150
    opcoes.HLRandWFViewsFileType = ImageFileType.PNG
    opcoes.ShadowViewsFileType = ImageFileType.PNG

    doc.ExportImage(opcoes)
    return [v.Name for v in vistas]
