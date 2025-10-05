'use client';

import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  VStack,
  Icon,
  Code,
} from '@chakra-ui/react';
import { FiRefreshCw, FiAlertTriangle } from 'react-icons/fi';
import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Application error:', error);
  }, [error]);

  return (
    <Container maxW="container.md" py={20}>
      <VStack spacing={8} align="center" textAlign="center">
        <Icon as={FiAlertTriangle} boxSize={20} color="orange.500" />
        <Heading size="2xl">Something went wrong!</Heading>
        <Text fontSize="lg" color="gray.600">
          We&apos;re sorry, but something unexpected happened. Please try again.
        </Text>
        {error.digest && (
          <Code fontSize="sm" p={4} borderRadius="md" colorScheme="red">
            Error ID: {error.digest}
          </Code>
        )}
        <Box>
          <Button
            leftIcon={<FiRefreshCw />}
            colorScheme="blue"
            size="lg"
            onClick={reset}
          >
            Try Again
          </Button>
        </Box>
      </VStack>
    </Container>
  );
}