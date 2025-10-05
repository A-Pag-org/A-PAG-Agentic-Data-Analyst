'use client';

import NextLink from 'next/link';
import { useRouter } from 'next/navigation';
import {
  Box,
  Flex,
  HStack,
  IconButton,
  Button,
  Spacer,
  Text,
  useColorMode,
  useColorModeValue,
} from '@chakra-ui/react';
import { MoonIcon, SunIcon } from '@chakra-ui/icons';
import { getSupabaseClient } from '@/lib/supabase/client';

type NavbarProps = {
  userEmail: string | null;
};

function ColorModeToggle() {
  const { colorMode, toggleColorMode } = useColorMode();
  return (
    <IconButton
      aria-label="Toggle color mode"
      icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
      onClick={toggleColorMode}
      variant="ghost"
    />
  );
}

export default function Navbar({ userEmail }: NavbarProps) {
  const router = useRouter();

  const handleLogout = async () => {
    try {
      const supabase = getSupabaseClient();
      await supabase.auth.signOut();
      router.push('/');
    } catch {
      router.push('/');
    }
  };

  return (
    <Box as="header" borderBottomWidth="1px" px={4} py={2} bg={useColorModeValue('gray.50', 'gray.900')}>
      <Flex align="center" gap={3}>
        <Text fontWeight="bold">
          <NextLink href="/">App</NextLink>
        </Text>
        <Spacer />
        <HStack spacing={2}>
          <ColorModeToggle />
          {userEmail ? (
            <>
              <Text fontSize="sm">{userEmail}</Text>
              <Button size="sm" as={NextLink} href="/dashboard">
                Dashboard
              </Button>
              <Button size="sm" onClick={handleLogout}>
                Logout
              </Button>
            </>
          ) : (
            <Button size="sm" as={NextLink} href="/login">
              Login
            </Button>
          )}
        </HStack>
      </Flex>
    </Box>
  );
}
