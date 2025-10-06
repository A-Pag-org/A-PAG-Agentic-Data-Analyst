'use client';
import React from 'react';
import { Box, Heading, Text, Stack } from '@chakra-ui/react';
import type { VisualizationConfig } from './VisualizationRenderer';

export const VizHeader: React.FC<{ config: VisualizationConfig }> = ({ config }) => {
  const { title, description } = config.metadata;
  return (
    <Box w="full" mb={4}>
      <Stack spacing={1}>
        <Heading size="md">{title}</Heading>
        {description ? (
          <Text color="gray.500">{description}</Text>
        ) : null}
      </Stack>
    </Box>
  );
};
