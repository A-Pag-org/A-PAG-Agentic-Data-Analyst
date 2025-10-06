"use client";

import { useState } from 'react';
import { Box, Button, Checkbox, FormControl, FormLabel, HStack, Input, Kbd, Stack, Text } from '@chakra-ui/react';
import { analyzeQuery } from '@/lib/api';
import { getSupabaseClient } from '@/lib/supabase/client';

export type QueryResult = Awaited<ReturnType<typeof analyzeQuery>>;

export default function QueryInterface(props: {
  onResult: (result: QueryResult) => void;
}) {
  const [query, setQuery] = useState("");
  const [visualize, setVisualize] = useState(true);
  const [forecast, setForecast] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const suggestions = [
    "What are the top 5 categories by sales?",
    "Show trend of orders by month",
    "Which regions have highest revenue?",
  ];

  const run = async () => {
    setLoading(true);
    setError(null);
    try {
      const supabase = getSupabaseClient();
      const { data } = await supabase.auth.getUser();
      const userId = data.user?.id;
      if (!userId) throw new Error('Not signed in');
      const res = await analyzeQuery({ userId, query, visualize, forecast });
      props.onResult(res);
    } catch (e: any) {
      setError(e?.message || 'Failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Stack spacing={3}>
        <FormControl>
          <FormLabel>Ask a question</FormLabel>
          <Input
            placeholder="Ask in natural language..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                run();
              }
            }}
          />
          <Text mt={1} fontSize="sm" color="gray.500">
            Press <Kbd>Ctrl</Kbd>+<Kbd>Enter</Kbd> to run
          </Text>
        </FormControl>
        <HStack>
          <Checkbox isChecked={visualize} onChange={(e) => setVisualize(e.target.checked)}>Visualize</Checkbox>
          <Checkbox isChecked={forecast} onChange={(e) => setForecast(e.target.checked)}>Forecast</Checkbox>
        </HStack>
        <HStack wrap="wrap" gap={2}>
          {suggestions.map((s) => (
            <Button key={s} size="sm" variant="ghost" onClick={() => setQuery(s)}>
              {s}
            </Button>
          ))}
        </HStack>
        <Button onClick={run} isLoading={loading} colorScheme="teal" isDisabled={!query.trim()}>
          Run
        </Button>
        {error && (
          <Text color="red.500" fontSize="sm">{error}</Text>
        )}
      </Stack>
    </Box>
  );
}
