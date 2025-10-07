'use client';

import { Box, Button, Heading, Text, VStack, useColorModeValue, Container, Card, CardBody } from '@chakra-ui/react';
import { getSupabaseClient } from '@/lib/supabase/client';

export default function LoginPage() {
  const loginWithGithub = async () => {
    const supabase = getSupabaseClient();
    await supabase.auth.signInWithOAuth({
      provider: 'github',
      options: { redirectTo: `${location.origin}/auth/callback` },
    });
  };

  const gradientText = useColorModeValue(
    'linear(to-r, brand.600, brand.500)',
    'linear(to-r, brand.300, brand.400)'
  );

  return (
    <Box 
      minH="calc(100vh - 80px)" 
      display="flex" 
      alignItems="center" 
      justifyContent="center"
      className="fade-in"
    >
      <Container maxW="md">
        <Card>
          <CardBody p={{ base: 8, md: 12 }}>
            <VStack spacing={8} align="stretch">
              <VStack spacing={3} textAlign="center">
                <Heading 
                  size="xl" 
                  fontWeight="700"
                  bgGradient={gradientText}
                  bgClip="text"
                  letterSpacing="-0.02em"
                >
                  Welcome Back
                </Heading>
                <Text 
                  fontSize="md" 
                  color="gray.600"
                  _dark={{ color: 'gray.400' }}
                >
                  Sign in to access your data analytics platform
                </Text>
              </VStack>
              
              <Button 
                onClick={loginWithGithub}
                colorScheme="brand"
                size="lg"
                height="56px"
                fontSize="md"
                fontWeight="600"
                leftIcon={
                  <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                  </svg>
                }
              >
                Continue with GitHub
              </Button>
              
              <Text 
                fontSize="xs" 
                color="gray.500"
                textAlign="center"
                _dark={{ color: 'gray.500' }}
              >
                By signing in, you agree to our Terms of Service and Privacy Policy
              </Text>
            </VStack>
          </CardBody>
        </Card>
      </Container>
    </Box>
  );
}
