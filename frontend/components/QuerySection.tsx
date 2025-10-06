"use client";

import { useState } from 'react';
import { Heading, Stack } from '@chakra-ui/react';
import type { AgentAnalyzeResponse } from '@/lib/api';
import QueryInterface from '@/components/QueryInterface';
import ResultsDisplay from '@/components/ResultsDisplay';
import VisualizationGallery from '@/components/VisualizationGallery';

export default function QuerySection() {
  const [result, setResult] = useState<AgentAnalyzeResponse | null>(null);
  return (
    <Stack spacing={4}>
      <Heading size="md">Query</Heading>
      <QueryInterface onResult={setResult} />
      <ResultsDisplay result={result} />
      <VisualizationGallery spec={result?.visualization_spec || null} />
    </Stack>
  );
}
