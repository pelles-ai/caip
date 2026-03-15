import {useEffect, useRef, useState} from 'react';

function useCountUp(target, duration = 1200) {
  const [value, setValue] = useState(0);
  const ref = useRef(null);
  const hasAnimated = useRef(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasAnimated.current) {
          hasAnimated.current = true;
          const start = performance.now();

          function animate(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            // ease-out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            setValue(Math.round(eased * target));
            if (progress < 1) {
              requestAnimationFrame(animate);
            }
          }

          requestAnimationFrame(animate);
          observer.unobserve(el);
        }
      },
      {threshold: 0.3},
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [target, duration]);

  return {ref, value};
}

const stats = [
  {target: 18, label: 'Task Types', suffix: ''},
  {target: 6, label: 'Data Schemas', suffix: ''},
  {target: 16, label: 'CSI Divisions', suffix: ''},
  {target: 100, label: 'A2A Compatible', suffix: '%'},
];

export default function CountUpStats() {
  return (
    <section className="stats-section">
      <div className="container">
        <div className="stats-row">
          {stats.map((s) => (
            <StatItem key={s.label} {...s} />
          ))}
        </div>
      </div>
    </section>
  );
}

function StatItem({target, label, suffix}) {
  const {ref, value} = useCountUp(target);
  return (
    <div className="stat" ref={ref}>
      <div className="stat__value">
        {value}
        {suffix}
      </div>
      <div className="stat__label">{label}</div>
    </div>
  );
}
