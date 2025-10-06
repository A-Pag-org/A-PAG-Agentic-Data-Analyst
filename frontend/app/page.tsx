import { Box, Heading, Stack, Text } from "@chakra-ui/react";
import dynamic from 'next/dynamic';
const Counter = dynamic(() => import('@/components/Counter'), { loading: () => null });

export default function Home() {
  return (
    <Box px={6} py={10}>
      <Stack spacing={4}>
        <Heading size="lg">Dashboard</Heading>
        <Text>Welcome to your app!</Text>
        <Counter />
      </Stack>
    </Box>
  );
}
