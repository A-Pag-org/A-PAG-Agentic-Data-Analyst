'use client';
import React, { useMemo } from 'react';
import { Box } from '@chakra-ui/react';
import { VizHeader } from './VizHeader';
import { VizRenderer } from './VizRenderer';
import { VizInsights } from './VizInsights';
import { generateVisualizationConfig } from '@/lib/visualization/generateVisualizationConfig';

export const VisualizationEngine: React.FC<{ data: unknown; query?: string }> = ({ data, query }) => {
  const vizConfig = useMemo(() => generateVisualizationConfig(data, query), [data, query]);

  return (
    <Box w="full">
      <VizHeader config={vizConfig} />
      <VizRenderer config={vizConfig} />
      <VizInsights insights={vizConfig.metadata.insights} />
    </Box>
  );
};
