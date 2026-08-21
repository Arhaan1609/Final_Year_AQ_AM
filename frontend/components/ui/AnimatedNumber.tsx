"use client";

import React, { useEffect, useRef } from "react";
import anime from "animejs";

interface AnimatedNumberProps {
  value: number;
  decimals?: number;
  className?: string;
  prefix?: string;
  suffix?: string;
  duration?: number;
}

export const AnimatedNumber: React.FC<AnimatedNumberProps> = ({
  value,
  decimals = 1,
  className = "",
  prefix = "",
  suffix = "",
  duration = 900,
}) => {
  const spanRef = useRef<HTMLSpanElement>(null);
  const prevValueRef = useRef<number>(value);

  useEffect(() => {
    if (!spanRef.current) return;

    const fromVal = prevValueRef.current;
    const toVal = value;
    prevValueRef.current = value;

    const obj = { val: fromVal };

    const anim = anime({
      targets: obj,
      val: toVal,
      duration: duration,
      easing: "easeOutExpo",
      update: () => {
        if (spanRef.current) {
          spanRef.current.innerHTML = `${prefix}${obj.val.toFixed(decimals)}${suffix}`;
        }
      },
    });

    return () => {
      anim.pause();
    };
  }, [value, decimals, prefix, suffix, duration]);

  return (
    <span
      ref={spanRef}
      className={`tabular-nums font-mono font-semibold tracking-tight ${className}`}
    >
      {prefix}
      {value.toFixed(decimals)}
      {suffix}
    </span>
  );
};
