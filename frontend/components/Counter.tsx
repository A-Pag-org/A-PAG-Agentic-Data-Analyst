'use client';

import { create } from 'zustand';
import { Box, Button, HStack, Text } from '@chakra-ui/react';

type CounterState = {
  value: number;
  increment: () => void;
  decrement: () => void;
};

const useCounterStore = create<CounterState>((set) => ({
  value: 0,
  increment: () => set((s) => ({ value: s.value + 1 })),
  decrement: () => set((s) => ({ value: s.value - 1 })),
}));

export default function Counter() {
  const { value, increment, decrement } = useCounterStore();
  return (
    <HStack>
      <Button onClick={decrement}>-</Button>
      <Box minW="40px" textAlign="center">
        <Text>{value}</Text>
      </Box>
      <Button onClick={increment}>+</Button>
    </HStack>
  );
}
