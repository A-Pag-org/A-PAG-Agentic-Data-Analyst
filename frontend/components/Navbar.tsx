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
    <Box as="header" borderBottomWidth="1px" px={4} py={2} bg={useColorModeValue('gray.50', 'gray.900')}>
      <Flex align="center" gap={3}>
        <Text fontWeight="bold">
          <NextLink href="/">App</NextLink>
        </Text>
        <Spacer />
        <HStack spacing={2}>
          <ColorModeToggle />
        </HStack>
      </Flex>
    </Box>
  );
}
