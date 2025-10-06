import { useEffect, useState } from 'react';
import { Box, Heading, SimpleGrid, Stat, StatLabel, StatNumber, Text, Spinner, Alert, AlertIcon } from '@chakra-ui/react';
import { getSupabaseClient } from '@/lib/supabase/client';

export default function DashboardOverview() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<{ datasets: number; rows: number } | null>(null);

  useEffect(() => {
    const run = async () => {
      try {
        const supabase = getSupabaseClient();
        // Count datasets (original files) for current user
        const { count: datasetCount, error: err1 } = await supabase
          .from('original_data')
          .select('id', { count: 'exact', head: true });
        if (err1) throw err1;

        // Count total chunks rows
        const { count: rowsCount, error: err2 } = await supabase
          .from('data_chunks')
          .select('id', { count: 'exact', head: true });
        if (err2) throw err2;

        setStats({ datasets: datasetCount || 0, rows: rowsCount || 0 });
      } catch (e: any) {
        setError(e?.message || 'Failed to load');
      } finally {
        setLoading(false);
      }
    };
    run();
  }, []);

  if (loading) return <Spinner />;
  if (error) return (
    <Alert status="error">
      <AlertIcon />
      {error}
    </Alert>
  );

  return (
    <Box>
      <Heading size="md" mb={4}>Overview</Heading>
      <SimpleGrid columns={{ base: 1, sm: 2 }} spacing={4}>
        <Stat borderWidth="1px" borderRadius="md" p={4}>
          <StatLabel>Datasets</StatLabel>
          <StatNumber>{stats?.datasets ?? 0}</StatNumber>
        </Stat>
        <Stat borderWidth="1px" borderRadius="md" p={4}>
          <StatLabel>Total Rows Indexed</StatLabel>
          <StatNumber>{stats?.rows ?? 0}</StatNumber>
        </Stat>
      </SimpleGrid>
      {(!stats || (stats.datasets === 0 && stats.rows === 0)) && (
        <Text mt={4} color="gray.500">No data yet. Upload via API to get started.</Text>
      )}
    </Box>
  );
}
