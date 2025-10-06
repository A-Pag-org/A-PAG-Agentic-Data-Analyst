import { useMemo } from 'react';
import { Accordion, AccordionButton, AccordionIcon, AccordionItem, AccordionPanel, Box, Code, Divider, Heading, Stack, Text } from '@chakra-ui/react';
import type { AgentAnalyzeResponse } from '@/lib/api';

export default function ResultsDisplay({ result }: { result: AgentAnalyzeResponse | null }) {
  const has = useMemo(() => ({
    answer: Boolean(result?.answer),
    explanation: Boolean(result?.explanation),
    sources: (result?.sources?.length || 0) > 0,
    forecast: Boolean(result?.forecast),
    viz: Boolean(result?.visualization_spec),
  }), [result]);

  if (!result) return null;

  return (
    <Box>
      {has.answer && (
        <Box mb={3}>
          <Heading size="md">Answer</Heading>
          <Text mt={1}>{result!.answer}</Text>
        </Box>
      )}

      <Accordion allowMultiple defaultIndex={[0]} borderWidth="1px" borderRadius="md">
        {has.explanation && (
          <AccordionItem>
            <h2>
              <AccordionButton>
                <Box as="span" flex='1' textAlign='left'>Explanation</Box>
                <AccordionIcon />
              </AccordionButton>
            </h2>
            <AccordionPanel pb={4}>
              <Text whiteSpace="pre-wrap">{result!.explanation}</Text>
            </AccordionPanel>
          </AccordionItem>
        )}

        {has.sources && (
          <AccordionItem>
            <h2>
              <AccordionButton>
                <Box as="span" flex='1' textAlign='left'>Sources</Box>
                <AccordionIcon />
              </AccordionButton>
            </h2>
            <AccordionPanel pb={4}>
              <Stack spacing={2}>
                {result!.sources.map((s, idx) => (
                  <Box key={idx}>
                    <Text fontSize="sm" color="gray.500">Score: {s.score ?? 'n/a'}</Text>
                    <Text>{s.text}</Text>
                    {s.metadata && (
                      <Code mt={1} fontSize="xs" whiteSpace="pre-wrap">{JSON.stringify(s.metadata, null, 2)}</Code>
                    )}
                    {idx < (result!.sources.length - 1) && <Divider mt={2} />}
                  </Box>
                ))}
              </Stack>
            </AccordionPanel>
          </AccordionItem>
        )}

        {has.forecast && (
          <AccordionItem>
            <h2>
              <AccordionButton>
                <Box as="span" flex='1' textAlign='left'>Forecast</Box>
                <AccordionIcon />
              </AccordionButton>
            </h2>
            <AccordionPanel pb={4}>
              <Text whiteSpace="pre-wrap">{result!.forecast}</Text>
            </AccordionPanel>
          </AccordionItem>
        )}
      </Accordion>
    </Box>
  );
}
