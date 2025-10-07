'use client';

import NextLink from 'next/link';
import Image from 'next/image';
import {
  Box,
  Flex,
  HStack,
  IconButton,
  Text,
  useColorMode,
  useColorModeValue,
} from '@chakra-ui/react';
import { MoonIcon, SunIcon } from '@chakra-ui/icons';

function ColorModeToggle() {
  const { colorMode, toggleColorMode } = useColorMode();
  const iconBg = useColorModeValue('gray.100', 'whiteAlpha.100');
  const iconHoverBg = useColorModeValue('gray.200', 'whiteAlpha.200');
  
  return (
    <IconButton
      aria-label="Toggle color mode"
      icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
      onClick={toggleColorMode}
      variant="ghost"
      size="md"
      bg={iconBg}
      _hover={{
        bg: iconHoverBg,
        transform: 'rotate(15deg)',
      }}
      transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
      borderRadius="full"
    />
  );
}

export default function Navbar() {
  const bgColor = useColorModeValue('rgba(255, 255, 255, 0.8)', 'rgba(10, 10, 10, 0.8)');
  const borderColor = useColorModeValue('rgba(0, 0, 0, 0.06)', 'rgba(255, 255, 255, 0.06)');
  
  return (
    <Box
      as="header"
      position="sticky"
      top={0}
      zIndex={100}
      bg={bgColor}
      borderBottom="1px solid"
      borderColor={borderColor}
      px={{ base: 4, md: 8 }}
      py={4}
      transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
      className="fade-in"
      sx={{
        backdropFilter: 'blur(20px) saturate(180%)',
        WebkitBackdropFilter: 'blur(20px) saturate(180%)',
      }}
    >
      <Flex align="center" justify="space-between" maxW="1400px" mx="auto">
        <NextLink href="/">
          <Box 
            cursor="pointer"
            transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
            _hover={{
              transform: 'translateY(-2px)',
            }}
          >
            <Image
              src="https://a-pag.org/wp-content/uploads/2022/08/APAG-final-logo-1.png"
              alt="A-PAG Logo"
              width={120}
              height={45}
              style={{ objectFit: 'contain' }}
            />
          </Box>
        </NextLink>
        <HStack spacing={2} justify="flex-end">
          <ColorModeToggle />
        </HStack>
      </Flex>
    </Box>
  );
}
