import { Box, Button, Heading, Stack, Text } from "@chakra-ui/react";
import Link from "next/link";

export default function Home() {
  return (
    <Box px={6} py={10}>
      <Stack spacing={4}>
        <Heading size="lg">Welcome</Heading>
        <Text>Next.js + Chakra UI + Supabase + Zustand scaffold.</Text>
        <Stack direction={{ base: "column", sm: "row" }}>
          <Button as={Link} href="/login" colorScheme="teal">
            Login
          </Button>
          <Button as={Link} href="/dashboard" variant="outline">
            Dashboard
          </Button>
        </Stack>
      </Stack>
    </Box>
  );
}
