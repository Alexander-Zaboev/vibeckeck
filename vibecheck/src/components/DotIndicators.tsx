interface DotIndicatorsProps {
  total: number;
  current: number;
}

export default function DotIndicators({ total, current }: DotIndicatorsProps) {
  return (
    <div className="flex gap-2 justify-center mt-10">
      {Array.from({ length: total }).map((_, idx) => {
        const isActive = idx === current;
        const isPast = idx < current;
        return (
          <div
            key={idx}
            className={`h-2 rounded-full transition-all duration-200 ${
              isActive
                ? "w-8 bg-gradient-sunset"
                : isPast
                ? "w-5 bg-primary/60"
                : "w-2 bg-muted-foreground/40"
            }`}
          />
        );
      })}
    </div>
  );
}
