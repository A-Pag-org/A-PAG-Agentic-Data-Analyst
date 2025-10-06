import { createClient } from '@/lib/supabase/server';
import { Box, Divider, Heading, Stack, Text } from '@chakra-ui/react';
import DashboardOverview from '@/components/DashboardOverview';
import QuerySection from '@/components/QuerySection';
import Counter from '@/components/Counter';

export default async function DashboardPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  return (
    <Box px={6} py={10}>
      <Stack spacing={6}>
        <Heading size="lg">Dashboard</Heading>
        {user ? <Text>Signed in as {user.email}</Text> : <Text>Not signed in</Text>}

        <DashboardOverview />

        <Divider />

        <QuerySection />

        <Counter />
      </Stack>
    </Box>
  );
}

//
