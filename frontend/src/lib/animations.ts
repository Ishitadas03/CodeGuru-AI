import { gsap } from "gsap";

export const fadeSlideUp = (element: any, delay = 0) => {
  if (!element) return;
  return gsap.fromTo(
    element,
    { y: 30, opacity: 0 },
    { y: 0, opacity: 1, duration: 0.6, ease: "power2.out", delay }
  );
};

export const staggerChildren = (parent: any, stagger = 0.08) => {
  if (!parent || !parent.children) return;
  return gsap.fromTo(
    parent.children,
    { y: 20, opacity: 0 },
    { y: 0, opacity: 1, stagger, duration: 0.5, ease: "power2.out" }
  );
};

export const countUp = (element: HTMLElement | null, end: number, duration = 1.5) => {
  if (!element) return;
  const obj = { val: 0 };
  return gsap.to(obj, {
    val: end,
    duration,
    ease: "power2.out",
    onUpdate: function () {
      element.textContent = Math.round(obj.val).toString();
    },
  });
};

export const magneticHover = (element: HTMLElement | null) => {
  if (!element) return () => {};

  const onMouseMove = (e: MouseEvent) => {
    const rect = element.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;

    // Pull the button towards mouse cursor slightly (max 15px travel)
    gsap.to(element, {
      x: x * 0.35,
      y: y * 0.35,
      duration: 0.3,
      ease: "power2.out",
    });
  };

  const onMouseLeave = () => {
    // Return button to center
    gsap.to(element, {
      x: 0,
      y: 0,
      duration: 0.5,
      ease: "elastic.out(1, 0.3)",
    });
  };

  element.addEventListener("mousemove", onMouseMove);
  element.addEventListener("mouseleave", onMouseLeave);

  // Return cleanup function
  return () => {
    element.removeEventListener("mousemove", onMouseMove);
    element.removeEventListener("mouseleave", onMouseLeave);
  };
};

export const textScramble = (element: HTMLElement | null, finalText: string, duration = 1.5) => {
  if (!element) return;
  const chars = "!<>-_\\/[]{}—=+*^?#________";
  const length = finalText.length;
  let frame = 0;
  const queue: Array<{ from: string; to: string; start: number; end: number; char?: string }> = [];

  for (let i = 0; i < length; i++) {
    const from = element.textContent?.[i] || "";
    const to = finalText[i];
    const start = Math.floor(Math.random() * 40);
    const end = start + Math.floor(Math.random() * 40);
    queue.push({ from, to, start, end });
  }

  let resolve: () => void;
  const promise = new Promise<void>((r) => (resolve = r));

  const update = () => {
    let output = "";
    let complete = 0;

    for (let i = 0, n = queue.length; i < n; i++) {
      let { from, to, start, end, char } = queue[i];
      if (frame >= end) {
        complete++;
        output += to;
      } else if (frame >= start) {
        if (!char || Math.random() < 0.28) {
          char = chars[Math.floor(Math.random() * chars.length)];
          queue[i].char = char;
        }
        output += `<span class="text-aether-teal font-mono">${char}</span>`;
      } else {
        output += from;
      }
    }

    element.innerHTML = output;

    if (complete === queue.length) {
      resolve();
    } else {
      frame++;
      requestAnimationFrame(update);
    }
  };

  update();
  return promise;
};

export const pageEnter = (selector = ".page-content") => {
  return gsap.fromTo(
    selector,
    { scale: 1.03, opacity: 0 },
    { scale: 1, opacity: 1, duration: 0.4, ease: "power2.out" }
  );
};

export const pageExit = (selector = ".page-content") => {
  return gsap.to(selector, {
    scale: 0.97,
    opacity: 0,
    duration: 0.3,
    ease: "power2.in",
  });
};
