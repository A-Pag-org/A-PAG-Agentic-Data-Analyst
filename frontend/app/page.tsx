'use client';

import { useState } from 'react';
import {
  Box,
  Button,
  Container,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Stack,
  Textarea,
  VStack,
  Text,
  useToast,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Card,
  CardBody,
  Checkbox,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react';
import { VisualizationEngine } from '@/components/VisualizationEngine';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [userId, setUserId] = useState('demo-user');
  const [query, setQuery] = useState('');
  const [visualize, setVisualize] = useState(true);
  const [forecast, setForecast] = useState(false);
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const toast = useToast();

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !userId) {
      toast({
        title: 'Missing Information',
        description: 'Please select a file and enter a user ID',
        status: 'warning',
        duration: 3000,
      });
      return;
    }

    setUploadLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/v1/ingest/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();
      toast({
        title: 'Upload Successful',
        description: `File uploaded successfully. ${result.chunks_created || 0} chunks created.`,
        status: 'success',
        duration: 5000,
      });
      setFile(null);
    } catch (error) {
      toast({
        title: 'Upload Failed',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 5000,
      });
    } finally {
      setUploadLoading(false);
    }
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query || !userId) {
      toast({
        title: 'Missing Information',
        description: 'Please enter a query and user ID',
        status: 'warning',
        duration: 3000,
      });
      return;
    }

    setLoading(true);
    setAnalysisResult(null);

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          query,
          visualize,
          forecast,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Analysis failed');
      }

      const result = await response.json();
      setAnalysisResult(result);
      toast({
        title: 'Analysis Complete',
        description: 'Your data has been analyzed successfully',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Analysis Failed',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 5000,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={6} align="stretch">
        <Box>
          <Heading size="xl" mb={2}>
            AI-Powered Data Analytics Platform
          </Heading>
          <Text color="gray.600">
            Upload your data, ask questions, and get intelligent insights with visualizations
          </Text>
        </Box>

        <Tabs colorScheme="blue" variant="enclosed">
          <TabList>
            <Tab>📊 Analyze Data</Tab>
            <Tab>📁 Upload Data</Tab>
            <Tab>📖 Guide</Tab>
          </TabList>

          <TabPanels>
            {/* Analyze Tab */}
            <TabPanel>
              <Card>
                <CardBody>
                  <form onSubmit={handleAnalyze}>
                    <VStack spacing={4} align="stretch">
                      <FormControl isRequired>
                        <FormLabel>User ID</FormLabel>
                        <Input
                          value={userId}
                          onChange={(e) => setUserId(e.target.value)}
                          placeholder="Enter your user ID"
                        />
                      </FormControl>

                      <FormControl isRequired>
                        <FormLabel>Your Question</FormLabel>
                        <Textarea
                          value={query}
                          onChange={(e) => setQuery(e.target.value)}
                          placeholder="e.g., What are the sales trends for the last quarter?"
                          rows={4}
                        />
                      </FormControl>

                      <Stack direction={{ base: 'column', md: 'row' }} spacing={4}>
                        <Checkbox
                          isChecked={visualize}
                          onChange={(e) => setVisualize(e.target.checked)}
                        >
                          Generate Visualizations
                        </Checkbox>
                        <Checkbox
                          isChecked={forecast}
                          onChange={(e) => setForecast(e.target.checked)}
                        >
                          Include Forecasting
                        </Checkbox>
                      </Stack>

                      <Button
                        type="submit"
                        colorScheme="blue"
                        size="lg"
                        isLoading={loading}
                        loadingText="Analyzing..."
                      >
                        Analyze Data
                      </Button>
                    </VStack>
                  </form>

                  {loading && (
                    <Box mt={6} textAlign="center">
                      <Spinner size="xl" color="blue.500" />
                      <Text mt={4}>Analyzing your data with AI...</Text>
                    </Box>
                  )}

                  {analysisResult && !loading && (
                    <Box mt={6}>
                      <Heading size="md" mb={4}>
                        Analysis Results
                      </Heading>
                      
                      {analysisResult.answer && (
                        <Alert status="info" mb={4}>
                          <AlertIcon />
                          <Box>
                            <AlertTitle>Answer</AlertTitle>
                            <AlertDescription>{analysisResult.answer}</AlertDescription>
                          </Box>
                        </Alert>
                      )}

                      {analysisResult.visualization_data && (
                        <VisualizationEngine
                          data={analysisResult.visualization_data}
                          query={query}
                        />
                      )}

                      {analysisResult.forecast_data && (
                        <Box mt={4}>
                          <Heading size="sm" mb={2}>
                            Forecast Results
                          </Heading>
                          <Card>
                            <CardBody>
                              <pre style={{ overflow: 'auto', fontSize: '14px' }}>
                                {JSON.stringify(analysisResult.forecast_data, null, 2)}
                              </pre>
                            </CardBody>
                          </Card>
                        </Box>
                      )}
                    </Box>
                  )}
                </CardBody>
              </Card>
            </TabPanel>

            {/* Upload Tab */}
            <TabPanel>
              <Card>
                <CardBody>
                  <form onSubmit={handleFileUpload}>
                    <VStack spacing={4} align="stretch">
                      <Alert status="info">
                        <AlertIcon />
                        Upload CSV, Excel, or JSON files to analyze your data
                      </Alert>

                      <FormControl isRequired>
                        <FormLabel>User ID</FormLabel>
                        <Input
                          value={userId}
                          onChange={(e) => setUserId(e.target.value)}
                          placeholder="Enter your user ID"
                        />
                      </FormControl>

                      <FormControl isRequired>
                        <FormLabel>Select File</FormLabel>
                        <Input
                          type="file"
                          accept=".csv,.xlsx,.xls,.json"
                          onChange={(e) => setFile(e.target.files?.[0] || null)}
                          p={1}
                        />
                      </FormControl>

                      <Button
                        type="submit"
                        colorScheme="green"
                        size="lg"
                        isLoading={uploadLoading}
                        loadingText="Uploading..."
                      >
                        Upload Data
                      </Button>
                    </VStack>
                  </form>
                </CardBody>
              </Card>
            </TabPanel>

            {/* Guide Tab */}
            <TabPanel>
              <Card>
                <CardBody>
                  <VStack spacing={4} align="stretch">
                    <Heading size="md">📚 How to Use This App</Heading>
                    
                    <Box>
                      <Heading size="sm" mb={2}>Step 1: Upload Your Data</Heading>
                      <Text>
                        Go to the "Upload Data" tab and upload your CSV, Excel, or JSON file.
                        The system will process and index your data for analysis.
                      </Text>
                    </Box>

                    <Box>
                      <Heading size="sm" mb={2}>Step 2: Ask Questions</Heading>
                      <Text>
                        Switch to the "Analyze Data" tab and ask questions about your data in natural language.
                        Examples:
                      </Text>
                      <Box as="ul" pl={6} mt={2}>
                        <li>What are the top 5 products by revenue?</li>
                        <li>Show me sales trends over the last 6 months</li>
                        <li>Which customers have the highest lifetime value?</li>
                        <li>Compare Q1 and Q2 performance</li>
                      </Box>
                    </Box>

                    <Box>
                      <Heading size="sm" mb={2}>Step 3: Get Insights</Heading>
                      <Text>
                        The AI will analyze your data and provide:
                      </Text>
                      <Box as="ul" pl={6} mt={2}>
                        <li>✅ Natural language answers</li>
                        <li>📊 Interactive visualizations</li>
                        <li>📈 Forecasts (when enabled)</li>
                        <li>💡 Data insights</li>
                      </Box>
                    </Box>

                    <Box>
                      <Heading size="sm" mb={2}>Step 4: Export Results</Heading>
                      <Text>
                        Use the visualization export options to download charts and reports.
                      </Text>
                    </Box>

                    <Alert status="success" mt={4}>
                      <AlertIcon />
                      <Box>
                        <AlertTitle>Pro Tip!</AlertTitle>
                        <AlertDescription>
                          Enable "Generate Visualizations" for charts and graphs, and "Include Forecasting" 
                          for predictive analytics.
                        </AlertDescription>
                      </Box>
                    </Alert>
                  </VStack>
                </CardBody>
              </Card>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </VStack>
    </Container>
  );
}
