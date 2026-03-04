import { useState, useEffect, useRef } from "react";
import { translateText } from "../api/translate";

interface UseDebouncedTranslationOptions {
  delay?: number;
  method?: "greedy" | "beam";
  beamWidth?: number;
}

interface UseDebouncedTranslationResult {
  translation: string;
  isLoading: boolean;
  error: string | null;
}

export function useDebouncedTranslation(
  text: string,
  options: UseDebouncedTranslationOptions = {},
): UseDebouncedTranslationResult {
  const { delay = 400, method = "beam", beamWidth = 5 } = options;
  const [translation, setTranslation] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    const trimmed = text.trim();
    if (!trimmed) {
      setTranslation("");
      setIsLoading(false);
      setError(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    const timer = setTimeout(async () => {
      abortControllerRef.current?.abort();
      const controller = new AbortController();
      abortControllerRef.current = controller;

      try {
        const result = await translateText(
          { text: trimmed, method, beam_width: beamWidth },
          controller.signal,
        );
        if (!controller.signal.aborted) {
          setTranslation(result.translation);
          setIsLoading(false);
        }
      } catch (err) {
        if (err instanceof DOMException && err.name === "AbortError") return;
        if (!controller.signal.aborted) {
          setError(err instanceof Error ? err.message : "Translation failed");
          setIsLoading(false);
        }
      }
    }, delay);

    return () => clearTimeout(timer);
  }, [text, delay, method, beamWidth]);

  useEffect(() => {
    return () => abortControllerRef.current?.abort();
  }, []);

  return { translation, isLoading, error };
}
