import { TranslatorPanel } from "@/components/translator-panel";

function App() {
  return (
    <main className="min-h-screen bg-background flex flex-col items-center justify-center p-6">
      <h1 className="text-3xl font-bold mb-2">LSTM Translator</h1>
      <p className="text-muted-foreground mb-8">
        English to Spanish — powered by a custom seq2seq model
      </p>
      <TranslatorPanel />
      <footer className="mt-8 text-sm text-muted-foreground">
        <a
          href="https://github.com/alexgarabt/lstm-translator"
          className="underline hover:text-foreground"
          target="_blank"
          rel="noopener noreferrer"
        >
          Model on GitHub
        </a>
        {" · "}
        <a
          href="https://huggingface.co/alexgara/lstm-en-es-translator"
          className="underline hover:text-foreground"
          target="_blank"
          rel="noopener noreferrer"
        >
          Weights on HuggingFace
        </a>
      </footer>
    </main>
  );
}

export default App;
