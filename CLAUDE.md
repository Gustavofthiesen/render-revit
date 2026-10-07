# RenderIA

Gera renders arquitetônicos a partir de vistas exportadas do Revit (veja README.md).
Responda ao usuário em português.

## Quando o usuário pedir para renderizar

1. Imagens de entrada: PNG/JPG com `RENDER_` no nome, em `entrada/`. Se o usuário
   anexou imagens na conversa, copie-as para `entrada/` mantendo `RENDER_` no nome.
2. Confira os pré-requisitos e, se faltar algo, explique como liberar (sem pedir a chave no chat):
   - `echo ${STABILITY_API_KEY:+ok}` precisa imprimir `ok` → senão, cadastrar a variável
     `STABILITY_API_KEY` nas configurações do ambiente.
   - `api.stability.ai` precisa estar liberado em *Allowed domains* do ambiente.
3. Rode:
   ```bash
   pip install -r requirements.txt
   cp -n config.example.json config.json
   python - <<'PY'
   import json; p = "config.json"; c = json.load(open(p, encoding="utf-8"))
   c["pasta_entrada"], c["pasta_saida"] = "entrada", "saida"
   json.dump(c, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
   PY
   python render_watcher.py --config config.json --once
   ```
4. Mostre os renders gerados em `saida/` ao usuário, faça commit de `entrada/` e `saida/`
   e envie para o GitHub.

## Quando o usuário pedir "abra o Revit e gere o render" (computer use)

Só funciona numa conversa com controle do computador do usuário (app Claude desktop
com Computer use ligado). Peça acesso ao Revit e então:
1. Abra o Revit e o projeto indicado pelo usuário (ou o que já estiver aberto).
2. Confirme que as vistas a renderizar têm nome iniciando em `RENDER_`; se o usuário
   pediu uma vista específica, renomeie-a com o prefixo (Navegador de Projeto ▸ Renomear).
3. Na aba **RenderIA**, clique em **Exportar e Renderizar**. Uma janela de terminal
   gera os renders e abre cada imagem pronta (pasta `C:\RenderIA\saida`).
4. Tire um screenshot do render aberto e mostre ao usuário. Se a janela do terminal
   mostrar erro (ex.: falta `STABILITY_API_KEY`), relate a mensagem exata.

## Ajustes de estilo

Prompts ficam em `config.example.json` (`prompt_padrao` e `prompts_por_nome`, chave =
nome da vista após `RENDER_`). `control_strength` mais alto = mais fiel à geometria.
