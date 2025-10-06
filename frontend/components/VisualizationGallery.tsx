"use client";

import { useEffect, useRef } from 'react';
import { Box, Heading, Text } from '@chakra-ui/react';
import embed, { VisualizationSpec } from 'vega-embed';

export default function VisualizationGallery({ spec }: { spec: Record<string, any> | null | undefined }) {
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      if (!ref.current) return;
      // Clear previous
      ref.current.innerHTML = '';
      if (!spec || Object.keys(spec).length === 0) return;
      try {
        const result = await embed(ref.current, spec as VisualizationSpec, { actions: false });
        if (cancelled) result.finalize?.();
      } catch (e) {
        // swallow render errors to avoid breaking page
      }
    };
    run();
    return () => { cancelled = true; };
  }, [spec]);

  if (!spec) return (
    <Text color="gray.500">No visualization available.</Text>
  );

  return (
    <Box>
      <Heading size="md" mb={2}>Visualization</Heading>
      <Box ref={ref} />
    </Box>
  );
}
