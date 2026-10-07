# RenderIA — render arquitetônico automático a partir do Revit

Clone ou baixe este repositório (ex.: em `C:\render-revit`).

## Como funciona

```text
Revit (vistas RENDER_*)  ──pyRevit──▶  C:\RenderIA\entrada\*.png
                                              │
                                   render_watcher.py (Stability AI)
                                              ▼
                                       C:\RenderIA\saida\*_render.png
```

1. **No Revit**, renomeie as vistas que quer renderizar com o prefixo `RENDER_`
   (ex.: `RENDER_Fachada`, `RENDER_Sala`). Vistas 3D com câmera dão o melhor resultado.
2. **A extensão pyRevit** exporta essas vistas como PNG — pelo botão
   **RenderIA ▸ Exportar p/ Render** ou automaticamente ao salvar o projeto.
3. **O `render_watcher.py`** monitora a pasta, envia cada imagem para a API
   *Control – Structure* da Stability AI (mantém a geometria do projeto e aplica
   materiais, luz e paisagismo) e salva o render na pasta de saída.

> O Claude não gera imagens; por isso o render é feito por uma API de geração de
> imagem (Stability AI). O custo é por imagem gerada — confira em
> https://platform.stability.ai/pricing.

## Instalação (Windows)

1. Instale o [pyRevit](https://github.com/pyrevitlabs/pyRevit/releases).
2. Crie a pasta `C:\RenderIA` e copie `config.example.json` para
   `C:\RenderIA\config.json`.
3. Registre a extensão no pyRevit (troque pelo caminho real desta pasta):
   ```bat
   pyrevit extend ui RenderIA "C:\render-revit\pyrevit\RenderIA.extension"
   ```
   Ou: pyRevit ▸ Settings ▸ *Custom Extension Directories* ▸ adicionar
   `C:\render-revit\pyrevit` e clicar em *Reload*.
4. Instale o Python 3.10+ e as dependências:
   ```bat
   pip install -r requirements.txt
   ```
5. Crie uma chave em https://platform.stability.ai/account/keys e rode:
   ```bat
   setx STABILITY_API_KEY "sk-..."
   python render_watcher.py --config C:\RenderIA\config.json
   ```
   Deixe essa janela aberta: toda imagem nova em `entrada` vira render em `saida`.
   Use `--once` para processar uma vez e sair.

## Um clique só: Exportar e Renderizar

O botão **RenderIA ▸ Exportar e Renderizar** exporta as vistas `RENDER_*`, abre
uma janela que gera os renders e abre cada imagem pronta — não precisa deixar o
`render_watcher.py` rodando. Requer a variável `STABILITY_API_KEY` salva com
`setx` (reinicie o Revit depois) e o repositório em `C:\render-revit`.

## Configuração (`config.json`)

| Campo | O que faz |
|---|---|
| `prefixo` | Nome que marca as vistas a renderizar (padrão `RENDER_`). |
| `pasta_entrada` / `pasta_saida` | Onde o Revit exporta e onde os renders são salvos. |
| `largura_px` | Largura do PNG exportado pelo Revit. |
| `python` | Comando do Python usado pelo botão *Exportar e Renderizar* (padrão `python`). |
| `exportar_ao_salvar` | `true` exporta as vistas automaticamente a cada *Salvar*. |
| `control_strength` | 0–1. Quanto o render respeita a geometria da vista (mais alto = mais fiel). |
| `prompt_padrao` | Descrição do estilo do render usada para todas as vistas. |
| `prompts_por_nome` | Prompt específico por vista: a chave é o nome após o prefixo (`RENDER_Fachada` → `"Fachada"`). |
| `negative_prompt` | O que evitar no render. |

Para usar o config em outro local, defina a variável `RENDERIA_CONFIG`
com o caminho do arquivo (lida pela extensão do Revit).

## Renderizar pelo GitHub (sem PC ligado)

O workflow `.github/workflows/render.yml` roda sozinho: envie os PNGs
`RENDER_*` para a pasta `entrada/` e o GitHub gera os renders em `saida/`.
Antes, cadastre a chave em **Settings ▸ Secrets and variables ▸ Actions ▸
New repository secret** com o nome `STABILITY_API_KEY`.

## Renderizar numa conversa com o Claude

Abra uma sessão do Claude Code com este repositório e peça "renderiza as
imagens novas" — o `CLAUDE.md` explica o processo. O ambiente da sessão
precisa de `api.stability.ai` em *Allowed domains* e da variável
`STABILITY_API_KEY` (menu do ambiente ▸ Edit).

## Dicas para bons renders

- Exporte vistas 3D/perspectiva com estilo visual *Realista* ou *Sombreado* e sombras ligadas.
- Escreva os prompts em inglês e descreva materiais, horário do dia e entorno.
- Se o render "inventar" demais, aumente `control_strength` (ex.: 0.85).
