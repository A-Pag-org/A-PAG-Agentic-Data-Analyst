'use client';

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Box, useColorModeValue } from '@chakra-ui/react';

type SplitPaneProps = {
  left: React.ReactNode;
  right: React.ReactNode;
  minLeft?: number;
  minRight?: number;
  defaultLeft?: number;
  storageKey?: string;
  height?: string | number;
  handleAriaLabel?: string;
};

// A11y-friendly, responsive, resizable horizontal split pane.
// - Desktop: draggable handle, keyboard-resizable, persisted width
// - Mobile (≤ 768px): stacks vertically, handle hidden
export default function SplitPane({
  left,
  right,
  minLeft = 320,
  minRight = 480,
  defaultLeft = 420,
  storageKey = 'splitpane-left-width',
  height = 'calc(100vh - 92px)',
  handleAriaLabel = 'Resize panels',
}: SplitPaneProps) {
  const [leftWidth, setLeftWidth] = useState<number>(defaultLeft);
  const [isDragging, setIsDragging] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const startXRef = useRef<number>(0);
  const startWidthRef = useRef<number>(defaultLeft);

  // Colors that adapt to color mode
  const handleBg = useColorModeValue('rgba(245, 158, 11, 0.08)', 'rgba(245, 158, 11, 0.18)');
  const handleHoverBg = useColorModeValue('rgba(245, 158, 11, 0.18)', 'rgba(245, 158, 11, 0.28)');
  const glow = useColorModeValue('0 0 0 2px rgba(245, 158, 11, 0.15)', '0 0 0 2px rgba(245, 158, 11, 0.25)');

  // Initialize from storage and watch viewport
  useEffect(() => {
    const saved = typeof window !== 'undefined' ? window.localStorage.getItem(storageKey) : null;
    const initial = saved ? Number(saved) : defaultLeft;
    setLeftWidth(Number.isFinite(initial) ? initial : defaultLeft);

    const onResize = () => {
      const mobile = window.innerWidth <= 768;
      setIsMobile(mobile);
      if (!mobile) {
        const containerWidth = containerRef.current?.clientWidth ?? window.innerWidth;
        const maxLeft = containerWidth - minRight;
        setLeftWidth((w) => Math.min(Math.max(w, minLeft), Math.max(maxLeft, minLeft)));
      }
    };
    onResize();
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, [defaultLeft, minLeft, minRight, storageKey]);

  const clampWidth = useCallback((proposed: number) => {
    const containerWidth = containerRef.current?.clientWidth ?? window.innerWidth;
    const maxLeft = containerWidth - minRight;
    return Math.min(Math.max(proposed, minLeft), Math.max(maxLeft, minLeft));
  }, [minLeft, minRight]);

  const startDragging = useCallback((clientX: number) => {
    setIsDragging(true);
    startXRef.current = clientX;
    startWidthRef.current = leftWidth;
    document.body.style.userSelect = 'none';
    document.body.style.cursor = 'col-resize';
  }, [leftWidth]);

  const onMouseDown = (e: React.MouseEvent) => {
    if (isMobile) return;
    startDragging(e.clientX);
  };

  const onTouchStart = (e: React.TouchEvent) => {
    if (isMobile) return;
    const touch = e.touches[0];
    if (touch) startDragging(touch.clientX);
  };

  useEffect(() => {
    if (!isDragging) return;

    const onMove = (clientX: number) => {
      const delta = clientX - startXRef.current;
      setLeftWidth(clampWidth(startWidthRef.current + delta));
    };

    const handleMouseMove = (e: MouseEvent) => onMove(e.clientX);
    const handleTouchMove = (e: TouchEvent) => {
      if (e.touches[0]) onMove(e.touches[0].clientX);
    };
    const stopDragging = () => {
      setIsDragging(false);
      document.body.style.userSelect = '';
      document.body.style.cursor = '';
      try {
        window.localStorage.setItem(storageKey, String(leftWidth));
      } catch {}
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('touchmove', handleTouchMove, { passive: false });
    window.addEventListener('mouseup', stopDragging);
    window.addEventListener('touchend', stopDragging);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      // Narrow the type by casting to EventListener to avoid any
      window.removeEventListener('touchmove', handleTouchMove as unknown as EventListener);
      window.removeEventListener('mouseup', stopDragging);
      window.removeEventListener('touchend', stopDragging);
    };
  }, [isDragging, clampWidth, leftWidth, storageKey]);

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (isMobile) return;
    const step = e.shiftKey ? 32 : 16;
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      setLeftWidth((w) => clampWidth(w - step));
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      setLeftWidth((w) => clampWidth(w + step));
    } else if (e.key.toLowerCase() === 'r' || e.key === 'Enter') {
      e.preventDefault();
      const containerWidth = containerRef.current?.clientWidth ?? window.innerWidth;
      setLeftWidth(clampWidth(Math.round(containerWidth * 0.38)));
    }
  };

  const onDoubleClick = () => {
    if (isMobile) return;
    const containerWidth = containerRef.current?.clientWidth ?? window.innerWidth;
    const snapPoints = [0.32, 0.42, 0.55];
    const current = leftWidth / containerWidth;
    const nextIdx = snapPoints.findIndex((p) => p - current > 0.05);
    const next = snapPoints[(nextIdx === -1 ? 0 : nextIdx)];
    setLeftWidth(clampWidth(Math.round(containerWidth * next)));
  };

  const styles = useMemo(() => ({
    handleBase: {
      background: handleBg,
      borderRadius: '12px',
      transition: 'background 0.2s, box-shadow 0.2s, transform 0.1s',
      boxShadow: isDragging ? glow : undefined,
      backdropFilter: 'blur(12px) saturate(140%)',
    } as React.CSSProperties,
  }), [handleBg, glow, isDragging]);

  return (
    <Box
      ref={containerRef}
      position="relative"
      display="flex"
      flexDirection={isMobile ? 'column' : 'row'}
      width="100%"
      height={height}
      px={{ base: 0, md: 0 }}
      py={{ base: 0, md: 0 }}
      gap={{ base: 3, md: 4 }}
    >
      {/* Left panel */}
      <Box
        flex={isMobile ? '0 0 auto' : '0 0 auto'}
        width={isMobile ? '100%' : `${leftWidth}px`}
        minW={isMobile ? undefined : `${minLeft}px`}
        height={isMobile ? 'auto' : '100%'}
        overflow="hidden"
      >
        {left}
      </Box>

      {/* Handle (hidden on mobile) */}
      {!isMobile && (
        <Box
          role="separator"
          aria-label={handleAriaLabel}
          aria-orientation="vertical"
          tabIndex={0}
          onKeyDown={onKeyDown}
          onMouseDown={onMouseDown}
          onTouchStart={onTouchStart}
          onDoubleClick={onDoubleClick}
          cursor="col-resize"
          width="12px"
          height="100%"
          alignSelf="stretch"
          display="flex"
          alignItems="center"
          justifyContent="center"
          _hover={{ background: handleHoverBg }}
          style={styles.handleBase}
        >
          {/* Handle grip */}
          <Box
            width="4px"
            height="40px"
            borderRadius="full"
            bgGradient="linear(to-b, brand.400, brand.600)"
            boxShadow="0 6px 16px -6px rgba(245, 158, 11, 0.5)"
          />
        </Box>
      )}

      {/* Right panel */}
      <Box
        flex="1 1 0"
        minW={isMobile ? undefined : `${minRight}px`}
        height={isMobile ? 'auto' : '100%'}
        overflow="hidden"
      >
        {right}
      </Box>
    </Box>
  );
}
