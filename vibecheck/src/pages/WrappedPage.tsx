import { useMemo, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import WrappedSlide from "@/components/WrappedSlide";
import DotIndicators from "@/components/DotIndicators";
import { readProfile } from "@/lib/api";
import type { AlgoProfile, WrappedSlideData } from "@/types/vibe";

const formatter = new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 });

function topEntry(record?: Record<string, number>) {
  if (!record) return null;
  return Object.entries(record).sort((a, b) => b[1] - a[1])[0] ?? null;
}

function buildSlides(profile: AlgoProfile | null): WrappedSlideData[] {
  if (!profile) return [];
  const slides: WrappedSlideData[] = [
    {
      label: "signals analyzed",
      value: profile.counts.items.toLocaleString(),
      detail: "Reddit posts/comments plus YouTube subscriptions piped through FastAPI.",
    },
  ];

  const rawTopic = topEntry(profile.topic_raw);
  if (rawTopic) {
    slides.push({
      label: "raw obsession",
      value: rawTopic[0],
      detail: `${formatter.format(rawTopic[1] * 100)}% of your feed coverage lives here.`,
    });
  }

  const weightedTopic = topEntry(profile.topic_weighted);
  if (weightedTopic) {
    slides.push({
      label: "algorithm boost",
      value: weightedTopic[0],
      detail: `${formatter.format(weightedTopic[1] * 100)}% of high-engagement attention piles onto this topic.`,
    });
  }

  const tone = topEntry(profile.tone_raw);
  if (tone) {
    slides.push({
      label: "tone of voice",
      value: tone[0],
      detail: `${formatter.format(tone[1] * 100)}% of your items carry this energy.`,
    });
  }

  const reinforced = profile.evidence.most_reinforced?.[0];
  if (reinforced) {
    slides.push({
      label: "reinforced source",
      value: reinforced.source,
      detail: `${reinforced.platform} • ${reinforced.topic} • ${reinforced.tone}`,
    });
  }

  slides.push({
    label: "diversity",
    value: formatter.format(profile.diversity.topic_entropy),
    detail: `${formatter.format(profile.diversity.top5_source_share * 100)}% of impressions come from top 5 sources.`,
  });

  return slides;
}

export default function WrappedPage() {
  const stored = readProfile();
  const profile = stored?.profile ?? null;
  const slides = useMemo(() => buildSlides(profile), [profile]);
  const [index, setIndex] = useState(0);
  const navigate = useNavigate();

  if (!profile || slides.length === 0) {
    return <Navigate to="/" replace />;
  }

  const next = () => {
    if (index >= slides.length - 1) {
      navigate("/dashboard");
    } else {
      setIndex((prev) => prev + 1);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-24" onClick={next}>
      <AnimatePresence mode="wait">
        <WrappedSlide key={slides[index].label} slide={slides[index]} />
      </AnimatePresence>
      <DotIndicators total={slides.length} current={index} />
      <button
        className="mt-8 text-sm text-muted-foreground underline"
        onClick={(event) => {
          event.stopPropagation();
          navigate("/dashboard");
        }}
      >
        Skip to Dashboard
      </button>
    </div>
  );
}
