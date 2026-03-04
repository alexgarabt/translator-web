import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { useDebouncedTranslation } from "@/hooks/use-debounced-translation";
import { LanguageLabel } from "./language-label";

export function TranslatorPanel() {
  const [text, setText] = useState("");
  const { translation, isLoading, error } = useDebouncedTranslation(text);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-4xl">
      <Card className="p-4">
        <LanguageLabel language="English" code="EN" />
        <Textarea
          placeholder="Type English text..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="min-h-[200px] resize-none border-0 shadow-none focus-visible:ring-0 text-lg"
        />
        <div className="text-sm text-muted-foreground mt-2 text-right">
          {text.length}/500
        </div>
      </Card>

      <Card className="p-4">
        <div className="flex items-center justify-between">
          <LanguageLabel language="Spanish" code="ES" />
          {isLoading && (
            <Badge variant="secondary" className="animate-pulse">
              Translating...
            </Badge>
          )}
        </div>
        <div className="min-h-[200px] text-lg pt-2 whitespace-pre-wrap">
          {error ? (
            <span className="text-destructive">{error}</span>
          ) : (
            translation || (
              <span className="text-muted-foreground">Translation</span>
            )
          )}
        </div>
      </Card>
    </div>
  );
}
