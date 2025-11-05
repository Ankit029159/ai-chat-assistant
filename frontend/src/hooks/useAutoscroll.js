import { useEffect, useRef } from 'react';

function useAutoscroll(containerRef, items) {
  const isUserScrollingRef = useRef(false);
  const scrollTimeoutRef = useRef(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const onScroll = () => {
      const scrollBottom = container.scrollHeight - container.scrollTop - container.clientHeight;
      if (scrollBottom > 50) {
        isUserScrollingRef.current = true;
        if (scrollTimeoutRef.current) clearTimeout(scrollTimeoutRef.current);
        scrollTimeoutRef.current = setTimeout(() => {
          isUserScrollingRef.current = false;
        }, 1000);
      } else {
        isUserScrollingRef.current = false;
      }
    };

    container.addEventListener('scroll', onScroll);
    return () => {
      container.removeEventListener('scroll', onScroll);
      if (scrollTimeoutRef.current) clearTimeout(scrollTimeoutRef.current);
    };
  }, [containerRef]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    if (isUserScrollingRef.current) return;

    // Smooth scroll to bottom
    const scrollToBottom = () => {
      container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
    };

    scrollToBottom();
  }, [items, containerRef]);
}

export default useAutoscroll;
