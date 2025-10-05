'use client';

import { Box, Button, Heading, Stack } from '@chakra-ui/react';
import { getSupabaseClient } from '@/lib/supabase/client';

export default function LoginPage() {
  const loginWithGithub = async () => {
    const supabase = getSupabaseClient();
    await supabase.auth.signInWithOAuth({
      provider: 'github',
      options: { redirectTo: `${location.origin}/auth/callback` },
    });
  };

  return (
    <Box px={6} py={10}>
      <Stack spacing={4}>
        <Heading size="md">Login</Heading>
        <Button onClick={loginWithGithub} colorScheme="gray">
          Continue with GitHub
        </Button>
      </Stack>
    </Box>
  );
}
