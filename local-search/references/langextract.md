# LangExtract: grounded structured extraction

Use this optional stage after `rg`, `rga`, or QMD has located canonical text and
the user needs a repeatable list of fields, entities, values, claims, or
relations. LangExtract maps retained extractions to source character intervals;
this makes the result a useful review locator, not evidence by itself.

## Safe route

1. Define a small schema and exact-text examples. Ask for verbatim extractions;
   do not ask the model to infer missing values.
2. Pass only the bounded canonical text needed for the task, not a whole corpus
   by default.
3. For restricted material, use a local model provider. This may be Ollama or
   an existing localhost OpenAI-compatible server such as `llama-server` or
   `ds4-server`. Do not call a cloud model unless the user explicitly authorizes
   that named provider and source scope.
4. Retain only items with a non-empty `char_interval`; reject ungrounded results.
5. Write JSONL/HTML output to a local disposable results location, exclude it
   from indexes and synced corpus folders, and reopen every adopted source span
   in the canonical file.

## Local environment

Install in the task's Python environment:

```bash
python -m pip install langextract
```

LangExtract can use Ollama at `http://localhost:11434`; model installation and
service startup are machine-level decisions. Its cloud providers require
credentials and are not a default for local or restricted collections.

### Existing OpenAI-compatible local servers

If the project already serves a local GGUF through an OpenAI-compatible `/v1`
endpoint, use the OpenAI provider with an explicit `ModelConfig`. A placeholder
API key is sufficient for a localhost server; do not put a real cloud key in
restricted workflows.

```python
from langextract.factory import ModelConfig

config = ModelConfig(
    model_id="local-model-id",
    provider="openai",
    provider_kwargs={
        "api_key": "local",
        "base_url": "http://127.0.0.1:8080/v1",
        "temperature": 0.0,
        "max_workers": 1,
        "max_output_tokens": 1024,
    },
)
```

For llama-server/Qwen, disable reasoning while extracting structured JSON (for
example, `--reasoning off`) and normally use `fence_output=False`. For
DwarfStar/DeepSeek, use the `deepseek-chat` non-thinking alias when available;
if the model emits fenced JSON, set `fence_output=True`. Confirm the exact
behavior with a bounded smoke test before adopting a larger extraction run.

## Result discipline

- Keep the prompt, examples, model identifier, input file hash, and extraction
  timestamp next to the output.
- Treat generated attributes as hypotheses unless each value is directly
  grounded and independently verified in context.
- Cite the canonical original, never the LangExtract JSONL, HTML visualization,
  staged text, or an embedding/index artifact.
