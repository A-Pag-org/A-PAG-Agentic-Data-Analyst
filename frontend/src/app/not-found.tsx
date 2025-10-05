'use client';

import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  VStack,
  Icon,
} from '@chakra-ui/react';
import { FiHome, FiAlertCircle } from 'react-icons/fi';
import { useRouter } from 'next/navigation';

export default function NotFound() {
  const router = useRouter();

  return (
    <Container maxW="container.md" py={20}>
      <VStack spacing={8} align="center" textAlign="center">
        <Icon as={FiAlertCircle} boxSize={20} color="red.500" />
        <Heading size="2xl">404 - Page Not Found</Heading>
        <Text fontSize="lg" color="gray.600">
          Sorry, the page you&apos;re looking for doesn&apos;t exist or has been moved.
        </Text>
        <Box>
          <Button
            leftIcon={<FiHome />}
            colorScheme="blue"
            size="lg"
            onClick={() => router.push('/')}
          >
            Go to Home
          </Button>
        </Box>
      </VStack>
    </Container>
  );
}