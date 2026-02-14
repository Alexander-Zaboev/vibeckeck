import type { WrappedSlideData } from "@/types/vibe";
import { motion } from "framer-motion";

interface WrappedSlideProps {
  slide: WrappedSlideData;
}

export default function WrappedSlide({ slide }: WrappedSlideProps) {
  return (
    <motion.div
      key={slide.label}
      initial={{ opacity: 0, y: 40, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -40, scale: 0.95 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="glass-card p-10 md:p-16 min-h-[340px] flex flex-col justify-center gap-6"
    >
      <p className="uppercase tracking-[0.4em] text-sm text-muted-foreground font-heading">
        {slide.label}
      </p>
      <p className="text-gradient-sunset text-5xl md:text-6xl font-heading animate-fade-in-up">
        {slide.value}
      </p>
      <p className="text-lg text-muted-foreground animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
        {slide.detail}
      </p>
    </motion.div>
  );
}
