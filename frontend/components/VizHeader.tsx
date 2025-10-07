'use client';
import React from 'react';
import { Box, Heading, Text, Stack, useColorModeValue } from '@chakra-ui/react';
import type { VisualizationConfig } from './VisualizationRenderer';

export const VizHeader: React.FC<{ config: VisualizationConfig }> = ({ config }) => {
  const { title, description } = config.metadata;
  const descColor = useColorModeValue('gray.600', 'gray.400');
  
  return (
    <Box w="full" mb={6} className="fade-in">
      <Stack spacing={2}>
        <Heading 
          size="lg" 
          fontWeight="700"
          letterSpacing="-0.01em"
        >
          {title}
        </Heading>
        {description ? (
          <Text 
            color={descColor}
            fontSize="md"
            lineHeight="1.6"
          >
            {description}
          </Text>
        ) : null}
      </Stack>
    </Box>
  );
};
