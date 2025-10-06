'use client';
import React from 'react';
import { Box, Heading, List, ListItem, ListIcon } from '@chakra-ui/react';
import { CheckCircleIcon } from '@chakra-ui/icons';
import type { VisualizationConfig } from './VisualizationRenderer';

export const VizInsights: React.FC<{ insights: VisualizationConfig['metadata']['insights'] }> = ({ insights }) => {
  if (!insights || insights.length === 0) {
    return null;
  }

  return (
    <Box w="full" mt={4}>
      <Heading size="sm" mb={2}>Insights</Heading>
      <List spacing={1}>
        {insights.map((insight, index) => (
          <ListItem key={index} display="flex" alignItems="start">
            <ListIcon as={CheckCircleIcon} color="green.400" />
            {insight}
          </ListItem>
        ))}
      </List>
    </Box>
  );
};
