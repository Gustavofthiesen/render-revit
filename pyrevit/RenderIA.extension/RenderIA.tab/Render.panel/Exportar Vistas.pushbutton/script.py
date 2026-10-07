# -*- coding: utf-8 -*-
"""Exporta as vistas RENDER_* para a pasta monitorada pelo render_watcher.py."""
__title__ = "Exportar\np/ Render"
__author__ = "RenderIA"

from pyrevit import forms, revit

import render_export

config = render_export.carregar_config()
exportadas = render_export.exportar_vistas(revit.doc, config)

if exportadas:
    forms.alert(
        "{} vista(s) exportada(s) para {}:\n\n{}".format(
            len(exportadas), config["pasta_entrada"], "\n".join(exportadas)
        ),
        title="RenderIA",
    )
else:
    forms.alert(
        "Nenhuma vista com nome iniciando em '{}' foi encontrada.\n"
        "Renomeie as vistas que deseja renderizar (ex.: {}Fachada).".format(
            config["prefixo"], config["prefixo"]
        ),
        title="RenderIA",
    )
