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

## Ajustes de estilo

Prompts ficam em `config.example.json` (`prompt_padrao` e `prompts_por_nome`, chave =
nome da vista após `RENDER_`). `control_strength` mais alto = mais fiel à geometria.
