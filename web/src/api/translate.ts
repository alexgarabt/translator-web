export interface TranslateRequest {
  text: string;
  method?: "greedy" | "beam";
  beam_width?: number;
}

export interface TranslateResponse {
  translation: string;
  method: string;
  source_language: string;
  target_language: string;
}

export async function translateText(
  request: TranslateRequest,
  signal?: AbortSignal,
): Promise<TranslateResponse> {
  const response = await fetch("/api/translate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    signal,
  });
  if (!response.ok) {
    throw new Error(`Translation failed: ${response.status}`);
  }
  return response.json();
}
