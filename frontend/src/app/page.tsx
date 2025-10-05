'use client';

import {
  Box,
  Container,
  Heading,
  Text,
  VStack,
  Button,
  useColorMode,
  Icon,
  SimpleGrid,
  Card,
  CardBody,
  CardHeader,
} from '@chakra-ui/react';
import { FiDatabase, FiTrendingUp, FiMap, FiZap } from 'react-icons/fi';

export default function Home() {
  const { colorMode, toggleColorMode } = useColorMode();

  const features = [
    {
      icon: FiDatabase,
      title: 'Advanced RAG',
      description: 'Hybrid search with vector and keyword capabilities',
    },
    {
      icon: FiZap,
      title: 'Agentic AI',
      description: 'Multi-step analysis with intelligent workflows',
    },
    {
      icon: FiTrendingUp,
      title: 'Forecasting',
      description: 'Time series analysis with Prophet and scikit-learn',
    },
    {
      icon: FiMap,
      title: 'GIS Mapping',
      description: 'Interactive visualizations with geospatial support',
    },
  ];

  return (
    <Container maxW="container.xl" py={20}>
      <VStack spacing={8} align="stretch">
        <Box textAlign="center">
          <Heading size="2xl" mb={4}>
            RAG Data Analyst
          </Heading>
          <Text fontSize="xl" color="gray.500">
            Advanced AI-powered data analysis platform
          </Text>
          <Button mt={6} onClick={toggleColorMode} size="sm">
            Toggle {colorMode === 'light' ? 'Dark' : 'Light'} Mode
          </Button>
        </Box>

        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} mt={10}>
          {features.map((feature, index) => (
            <Card key={index}>
              <CardHeader>
                <Icon as={feature.icon} boxSize={8} color="blue.500" mb={2} />
                <Heading size="md">{feature.title}</Heading>
              </CardHeader>
              <CardBody>
                <Text color="gray.600">{feature.description}</Text>
              </CardBody>
            </Card>
          ))}
        </SimpleGrid>
      </VStack>
    </Container>
  );
}