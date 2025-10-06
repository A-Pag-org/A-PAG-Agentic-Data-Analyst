import { createClient } from '@/lib/supabase/server';
import { Box, Heading, Stack, Text } from '@chakra-ui/react';
import dynamic from 'next/dynamic';
const Counter = dynamic(() => import('@/components/Counter'), { loading: () => null });

export default async function DashboardPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  return (
    <Box px={6} py={10}>
      <Stack spacing={4}>
        <Heading size="lg">Dashboard</Heading>
        {user ? (
          <Text>Signed in as {user.email}</Text>
        ) : (
          <Text>Not signed in</Text>
        )}
        <Counter />
      </Stack>
    </Box>
  );
}
