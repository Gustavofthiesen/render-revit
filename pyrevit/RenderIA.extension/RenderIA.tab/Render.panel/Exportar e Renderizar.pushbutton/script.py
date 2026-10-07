# -*- coding: utf-8 -*-
"""Exporta as vistas RENDER_* e ja gera os renders com IA (um clique)."""
__title__ = "Exportar e\nRenderizar"
__author__ = "RenderIA"

from pyrevit import forms, revit

import render_export

config = render_export.carregar_config()
exportadas = render_export.exportar_vistas(revit.doc, config)

if exportadas:
    render_export.iniciar_render()
    forms.toast(
        "{} vista(s) exportada(s). O render abre sozinho quando ficar pronto.".format(len(exportadas)),
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
