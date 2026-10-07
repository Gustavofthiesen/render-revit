# -*- coding: utf-8 -*-
"""Exporta automaticamente as vistas RENDER_* sempre que o projeto e salvo.

So roda quando "exportar_ao_salvar": true no config.json.
"""
from pyrevit import EXEC_PARAMS

import render_export

config = render_export.carregar_config()
if config.get("exportar_ao_salvar"):
    render_export.exportar_vistas(EXEC_PARAMS.event_args.Document, config)
