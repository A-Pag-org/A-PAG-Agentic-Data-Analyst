'use client';

import NextLink from 'next/link';
import Image from 'next/image';
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
      <Flex align="center" justify="space-between">
        <Box width="120px">
          {/* Spacer for left side */}
        </Box>
        <NextLink href="/">
          <HStack spacing={3} cursor="pointer">
            <Image
              src="https://a-pag.org/wp-content/uploads/2022/08/APAG-final-logo-1.png"
              alt="A-PAG Logo"
              width={120}
              height={45}
              style={{ objectFit: 'contain' }}
            />
            <Text fontWeight="bold" fontSize="xl">
              Agentic Data Analyst
            </Text>
          </HStack>
        </NextLink>
        <HStack spacing={2} width="120px" justify="flex-end">
          <ColorModeToggle />
        </HStack>
      </Flex>
    </Box>
  );
}
