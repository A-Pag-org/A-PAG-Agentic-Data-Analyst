'use client';
import React from 'react';
import { Heading, List, ListItem, ListIcon, useColorModeValue, Card, CardBody } from '@chakra-ui/react';
import { CheckCircleIcon } from '@chakra-ui/icons';
import type { VisualizationConfig } from './VisualizationRenderer';

export const VizInsights: React.FC<{ insights: VisualizationConfig['metadata']['insights'] }> = ({ insights }) => {
  const cardBg = useColorModeValue('yellow.50', 'yellow.900');
  
  if (!insights || insights.length === 0) {
    return null;
  }

  return (
    <Card 
      w="full" 
      mt={6}
      bg={cardBg}
      borderLeft="4px solid"
      borderColor="brand.500"
      className="fade-in"
    >
      <CardBody>
        <Heading size="md" mb={4} fontWeight="600">
          💡 Key Insights
        </Heading>
        <List spacing={3}>
          {insights.map((insight, index) => (
            <ListItem 
              key={index} 
              display="flex" 
              alignItems="start"
              fontSize="sm"
              lineHeight="1.6"
            >
              <ListIcon 
                as={CheckCircleIcon} 
                color="brand.500" 
                mt={0.5}
                boxSize={5}
              />
              {insight}
            </ListItem>
          ))}
        </List>
      </CardBody>
    </Card>
  );
};
