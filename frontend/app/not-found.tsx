'use client';

import {
  Box,
  Button,
  Container,
  Heading,
  Text,
  VStack,
  useColorModeValue,
} from '@chakra-ui/react';
import { useRouter } from 'next/navigation';

export default function NotFound() {
  const router = useRouter();
  const bgGradient = useColorModeValue(
    'linear(to-br, yellow.50, orange.50)',
    'linear(to-br, gray.900, gray.800)'
  );
  const headingColor = useColorModeValue('gray.800', 'white');
  const textColor = useColorModeValue('gray.600', 'gray.400');

  return (
    <Box minH="calc(100vh - 64px)" display="flex" alignItems="center" bgGradient={bgGradient}>
      <Container maxW="container.md">
        <VStack spacing={6} textAlign="center" py={12}>
          <Heading
            as="h1"
            size="4xl"
            fontWeight="800"
            color={headingColor}
            mb={2}
          >
            404
          </Heading>
          <Heading
            as="h2"
            size="xl"
            fontWeight="600"
            color={headingColor}
          >
            Page Not Found
          </Heading>
          <Text fontSize="lg" color={textColor} maxW="md">
            The page you&apos;re looking for doesn&apos;t exist or has been moved.
          </Text>
          <Button
            colorScheme="brand"
            size="lg"
            onClick={() => router.push('/')}
            mt={4}
            px={8}
            height="56px"
            fontSize="md"
            fontWeight="600"
          >
            Go Back Home
          </Button>
        </VStack>
      </Container>
    </Box>
  );
}
