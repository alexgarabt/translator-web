"""Translation service — loads the LSTM model from HuggingFace Hub and provides inference."""

import json
from pathlib import Path

import torch
from huggingface_hub import hf_hub_download

from translator.config import Config
from translator.data.tokenizer import Tokenizer
from translator.models.decoder import Decoder
from translator.models.encoder import Encoder
from translator.models.seq2seq import Seq2Seq

REPO_ID = "alexgara/lstm-en-es-translator"


class TranslatorService:
    """Holds the loaded model and provides translation methods."""

    def __init__(self, device: str, cache_dir: str = "hub_cache"):
        self.device = device
        self.cache_dir = Path(cache_dir)
        self.model: Seq2Seq | None = None
        self.src_tokenizer: Tokenizer | None = None
        self.trg_tokenizer: Tokenizer | None = None

    # -- HuggingFace Hub downloads --

    def _download_hparams(self) -> dict:
        path = hf_hub_download(repo_id=REPO_ID, filename="hparams.json", cache_dir=self.cache_dir)
        with open(path) as f:
            return json.load(f)

    def _download_tokenizers(self) -> tuple[Path, Path]:
        en = hf_hub_download(repo_id=REPO_ID, filename="spm_en.model", cache_dir=self.cache_dir)
        es = hf_hub_download(repo_id=REPO_ID, filename="spm_es.model", cache_dir=self.cache_dir)
        return Path(en), Path(es)

    def _download_checkpoint(self) -> Path:
        return Path(
            hf_hub_download(repo_id=REPO_ID, filename="model.pt", cache_dir=self.cache_dir)
        )

    # -- Model loading --

    def load(self) -> None:
        """Download artifacts from HF Hub and build the model."""
        hparams = self._download_hparams()
        en_path, es_path = self._download_tokenizers()
        checkpoint_path = self._download_checkpoint()

        config = Config(
            embed_dim=hparams["embed_dim"],
            hidden_dim=hparams["hidden_dim"],
            num_layers=hparams["num_layers"],
            device=self.device,
        )

        self.src_tokenizer = Tokenizer(str(en_path))
        self.trg_tokenizer = Tokenizer(str(es_path))

        encoder = Encoder(
            vocab_size=self.src_tokenizer.vocab_size,
            embedded_dim=config.embed_dim,
            hidden_dim=config.hidden_dim,
            num_layers=config.num_layers,
            dropout=0.0,
        )
        decoder = Decoder(
            vocab_size=self.trg_tokenizer.vocab_size,
            embed_dim=config.embed_dim,
            hidden_dim=config.hidden_dim,
            encoder_dim=config.encoder_dim,
            num_layers=config.num_layers,
            dropout=0.0,
        )
        model = Seq2Seq(
            encoder,
            decoder,
            pad_token_id=self.src_tokenizer.pad_id,
            bos_token_id=self.src_tokenizer.bos_id,
            eos_token_id=self.src_tokenizer.eos_id,
        )

        checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
        model.load_state_dict(checkpoint["model_state_dict"])
        model.eval()
        model.to(self.device)
        self.model = model

    # -- Translation methods --

    def translate_greedy(self, text: str, max_len: int = 50) -> str:
        """Greedy decoding — pick the most probable token at each step."""
        assert self.model is not None and self.src_tokenizer and self.trg_tokenizer

        src_ids = self.src_tokenizer.encode(text)
        src = torch.tensor([src_ids], device=self.device)
        src_lengths = torch.tensor([len(src_ids)], device=self.device)
        mask = src != self.src_tokenizer.pad_id

        with torch.no_grad():
            enc_out, (h, c) = self.model.encoder(src, src_lengths)
            h = [h[layer] for layer in range(self.model.decoder.num_layers)]
            c = [c[layer] for layer in range(self.model.decoder.num_layers)]
            context = torch.zeros(1, enc_out.shape[2], device=self.device)
            token = torch.tensor([self.trg_tokenizer.bos_id], device=self.device)
            result = []

            for _ in range(max_len):
                logits, h, c, context, _ = self.model.decoder.forward_step(
                    token, h, c, enc_out, context, mask
                )
                token = logits.argmax(dim=1)
                if token.item() == self.trg_tokenizer.eos_id:
                    break
                result.append(token.item())

        return self.trg_tokenizer.decode(result)

    def translate_beam(self, text: str, beam_width: int = 5) -> str:
        """Beam search decoding — keep B best hypotheses at each step."""
        assert self.model is not None and self.src_tokenizer and self.trg_tokenizer

        src_ids = self.src_tokenizer.encode(text)
        src = torch.tensor([src_ids], device=self.device)
        src_lengths = torch.tensor([len(src_ids)], device=self.device)

        tokens = self.model.beam_search(
            src,
            src_lengths,
            bos_id=self.trg_tokenizer.bos_id,
            eos_id=self.trg_tokenizer.eos_id,
            beam_width=beam_width,
        )
        return self.trg_tokenizer.decode(tokens)

    def translate(self, text: str, method: str = "beam", beam_width: int = 5) -> str:
        """Translate English text to Spanish."""
        if method == "greedy":
            return self.translate_greedy(text)
        return self.translate_beam(text, beam_width)

    @property
    def is_loaded(self) -> bool:
        return self.model is not None
