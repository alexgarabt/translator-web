interface LanguageLabelProps {
  language: string;
  code: string;
}

export function LanguageLabel({ language, code }: LanguageLabelProps) {
  return (
    <div className="flex items-center gap-2 mb-3 pb-2 border-b">
      <span className="font-semibold text-sm uppercase tracking-wide text-muted-foreground">
        {code}
      </span>
      <span className="font-medium">{language}</span>
    </div>
  );
}
