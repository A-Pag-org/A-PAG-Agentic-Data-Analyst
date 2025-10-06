'use client';

import NextLink from 'next/link';
import {
  Box,
  Flex,
  HStack,
  IconButton,
  Spacer,
  Text,
  useColorMode,
  useColorModeValue,
} from '@chakra-ui/react';
import { MoonIcon, SunIcon } from '@chakra-ui/icons';

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

export default function Navbar() {
  return (
    <Box as="header" borderBottomWidth="1px" px={4} py={3} bg={useColorModeValue('white', 'gray.900')} boxShadow="sm">
      <Flex align="center" gap={3}>
        <Text fontWeight="bold" fontSize="xl">
          <NextLink href="/">📊 AI Data Analytics</NextLink>
        </Text>
        <Spacer />
        <HStack spacing={2}>
          <ColorModeToggle />
        </HStack>
      </Flex>
    </Box>
  );
}
