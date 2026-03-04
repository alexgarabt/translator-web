# Translator Web

Web application for English-to-Spanish translation using a custom LSTM seq2seq model built from scratch.

https://github.com/user-attachments/assets/ffd9ac47-3138-46a4-876c-34e608d9adec

- **Model code**: [github.com/alexgarabt/lstm-translator](https://github.com/alexgarabt/lstm-translator)
- **Pre-trained weights**: [huggingface.co/alexgara/lstm-en-es-translator](https://huggingface.co/alexgara/lstm-en-es-translator)

## Structure

```
translator-web/
├── lstm-translator/   # Git submodule — LSTM model package
├── api/               # FastAPI backend — loads model, serves /api/translate
└── web/               # React + Tailwind + shadcn/ui frontend
```

- **`api/`** — FastAPI server that downloads the pre-trained model from HuggingFace Hub at startup and exposes a REST endpoint for translation (beam search by default).
- **`web/`** — React frontend with a Google Translate-style UI. Debounces input and calls the API on every new word.
- **`lstm-translator/`** — Git submodule pointing to the [lstm-translator](https://github.com/alexgarabt/lstm-translator) repository. The API imports it as a Python package via `uv`.

## Setup

### Clone with submodule

```bash
git clone --recurse-submodules <repo-url>
cd translator-web
```

### API

```bash
cd api
uv sync
uv run uvicorn api.main:app --port 8000
```

The model (~128 MB) downloads from HuggingFace Hub on first startup and is cached locally.

### Web

```bash
cd web
npm install
npm run dev
```

Opens at `http://localhost:5173`. The Vite dev server proxies `/api/*` requests to the FastAPI backend at port 8000.

## Inference Performance

The model (~31.9M parameters) runs on both CPU and GPU:

| Device | 12 sentences | RAM / VRAM |
|---|---|---|
| CPU (AMD Ryzen AI 9 HX 379) | ~12.8s | ~200 MB RAM |
| GPU (NVIDIA) | ~4.4s | ~150 MB VRAM |

Model weights are stored in float32: 31.9M params x 4 bytes = ~128 MB, plus tokenizers and PyTorch overhead.

No GPU required — the API auto-detects CUDA and falls back to CPU.
