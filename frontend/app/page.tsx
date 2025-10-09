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
  useColorModeValue,
} from '@chakra-ui/react';
import { VisualizationEngine } from '@/components/VisualizationEngine';
import SplitPane from '@/components/SplitPane';

interface AnalysisResult {
  answer?: string;
  visualization_data?: unknown;
  forecast_data?: unknown;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [userId, setUserId] = useState('demo-user');
  const [query, setQuery] = useState('');
  const [visualize, setVisualize] = useState(true);
  const [forecast, setForecast] = useState(false);
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
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
      // Proxy through Next.js API route to avoid CORS and localhost issues
      const response = await fetch('/api/ingest/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        let detail: any = undefined;
        try {
          detail = await response.json();
        } catch {}
        const message =
          (detail && (detail.error || detail.detail?.error || detail.detail)) ||
          `Upload failed with status ${response.status}`;
        throw new Error(typeof message === 'string' ? message : JSON.stringify(message));
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

  const tabBg = useColorModeValue('white', 'gray.800');
  // gradientText not needed on this page
  const checkboxBg = useColorModeValue('gray.50', 'whiteAlpha.50');
  const infoBg = useColorModeValue('yellow.50', 'yellow.900');
  const cardBg = useColorModeValue('gray.50', 'whiteAlpha.50');
  const successBg = useColorModeValue('green.50', 'green.900');
  const fileButtonBg = useColorModeValue('gray.100', 'whiteAlpha.200');
  const fileButtonHoverBg = useColorModeValue('gray.200', 'whiteAlpha.300');
  const stepBg = useColorModeValue('gray.50', 'whiteAlpha.50');

  return (
    <Box className="fade-in" minH="100vh">
      <Container maxW="1400px" py={{ base: 6, md: 12 }}>
        <VStack spacing={8} align="stretch">
          <Tabs colorScheme="brand" variant="enclosed" className="scale-in">
            <TabList 
              borderBottom="none" 
              gap={2}
              flexWrap="wrap"
              bg={tabBg}
              p={2}
              borderRadius="16px"
              boxShadow="sm"
            >
              <Tab
                fontSize={{ base: 'sm', md: 'md' }}
                fontWeight="500"
                borderRadius="12px"
                _selected={{
                  bg: 'brand.500',
                  color: 'white',
                  boxShadow: '0 4px 12px -2px rgba(245, 158, 11, 0.4)',
                }}
                transition="all 0.2s"
              >
                📊 Analyze
              </Tab>
              <Tab
                fontSize={{ base: 'sm', md: 'md' }}
                fontWeight="500"
                borderRadius="12px"
                _selected={{
                  bg: 'brand.500',
                  color: 'white',
                  boxShadow: '0 4px 12px -2px rgba(245, 158, 11, 0.4)',
                }}
                transition="all 0.2s"
              >
                📁 Upload
              </Tab>
              <Tab
                fontSize={{ base: 'sm', md: 'md' }}
                fontWeight="500"
                borderRadius="12px"
                _selected={{
                  bg: 'brand.500',
                  color: 'white',
                  boxShadow: '0 4px 12px -2px rgba(245, 158, 11, 0.4)',
                }}
                transition="all 0.2s"
              >
                📖 Guide
              </Tab>
            </TabList>

          <TabPanels pt={6}>
            {/* Analyze Tab */}
            <TabPanel px={0}>
              <SplitPane
                minLeft={300}
                minRight={520}
                defaultLeft={420}
                storageKey="analyze-split-left"
                left={
                  <Box height="100%" overflow="auto">
                    <Card height="100%">
                      <CardBody p={{ base: 5, md: 6 }}>
                        <form onSubmit={handleAnalyze}>
                          <VStack spacing={6} align="stretch">
                            <FormControl isRequired>
                              <FormLabel fontWeight="500" mb={3}>User ID</FormLabel>
                              <Input
                                value={userId}
                                onChange={(e) => setUserId(e.target.value)}
                                placeholder="Enter your user ID"
                                size="lg"
                                fontSize="md"
                                border="1px solid"
                                borderColor="gray.300"
                                _dark={{ borderColor: 'gray.600' }}
                              />
                            </FormControl>

                            <FormControl isRequired>
                              <FormLabel fontWeight="500" mb={3}>Your Question</FormLabel>
                              <Textarea
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder="e.g., What are the sales trends for the last quarter?"
                                rows={8}
                                fontSize="md"
                                resize="vertical"
                                border="1px solid"
                                borderColor="gray.300"
                                _dark={{ borderColor: 'gray.600' }}
                              />
                            </FormControl>

                            <Stack 
                              direction={{ base: 'column', md: 'row' }} 
                              spacing={4}
                              p={4}
                              bg={checkboxBg}
                              borderRadius="12px"
                            >
                              <Checkbox
                                isChecked={visualize}
                                onChange={(e) => setVisualize(e.target.checked)}
                                colorScheme="brand"
                                size="lg"
                              >
                                <Text fontSize="sm" fontWeight="500">Generate Visualizations</Text>
                              </Checkbox>
                              <Checkbox
                                isChecked={forecast}
                                onChange={(e) => setForecast(e.target.checked)}
                                colorScheme="brand"
                                size="lg"
                              >
                                <Text fontSize="sm" fontWeight="500">Include Forecasting</Text>
                              </Checkbox>
                            </Stack>

                            <Button
                              type="submit"
                              colorScheme="brand"
                              size="lg"
                              height="56px"
                              fontSize="md"
                              fontWeight="600"
                              isLoading={loading}
                              loadingText="Analyzing..."
                              mt={2}
                              w="full"
                            >
                              Analyze Data
                            </Button>
                          </VStack>
                        </form>
                      </CardBody>
                    </Card>
                  </Box>
                }
                right={
                  <Box height="100%" overflow="auto">
                    {loading ? (
                      <Card>
                        <CardBody>
                          <Box textAlign="center" py={16} className="fade-in">
                            <Spinner 
                              size="xl" 
                              color="brand.500"
                              thickness="4px"
                              speed="0.8s"
                            />
                            <Text mt={6} fontSize="md" color="gray.600" _dark={{ color: 'gray.400' }}>
                              Analyzing your data with AI...
                            </Text>
                          </Box>
                        </CardBody>
                      </Card>
                    ) : analysisResult ? (
                      <Box className="fade-in">
                        {analysisResult.answer ? (
                          <Alert 
                            status="info" 
                            mb={6}
                            borderRadius="12px"
                            bg={infoBg}
                            borderLeft="4px solid"
                            borderColor="brand.500"
                          >
                            <AlertIcon color="brand.500" />
                            <Box>
                              <AlertTitle fontWeight="600">Answer</AlertTitle>
                              <AlertDescription fontSize="md" mt={1}>{analysisResult.answer}</AlertDescription>
                            </Box>
                          </Alert>
                        ) : null}

                        {analysisResult.visualization_data ? (
                          <VisualizationEngine
                            data={analysisResult.visualization_data}
                            query={query}
                          />
                        ) : null}

                        {analysisResult.forecast_data ? (
                          <Box mt={6}>
                            <Heading size="sm" mb={4} fontWeight="600">
                              Forecast Results
                            </Heading>
                            <Card bg={cardBg}>
                              <CardBody>
                                <pre style={{ 
                                  overflow: 'auto', 
                                  fontSize: '13px',
                                  fontFamily: 'var(--font-geist-mono), monospace',
                                  lineHeight: '1.6'
                                }}>
                                  {JSON.stringify(analysisResult.forecast_data, null, 2)}
                                </pre>
                              </CardBody>
                            </Card>
                          </Box>
                        ) : null}
                      </Box>
                    ) : (
                      <Card className="fade-in" bgGradient="linear(to-br, brand.50, white)" _dark={{ bg: 'rgba(26, 32, 44, 0.6)' }}>
                        <CardBody>
                          <VStack spacing={4} align="stretch" py={6}>
                            <Heading size="md" fontWeight="700">
                              Start by asking a question
                            </Heading>
                            <Text color="gray.600" _dark={{ color: 'gray.400' }}>
                              Enter your question on the left to generate insights and visualizations.
                            </Text>
                            <VStack align="stretch" spacing={2} pl={1}>
                              <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>• What are the top 5 products by revenue?</Text>
                              <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>• Show me sales trends over the last 6 months</Text>
                              <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>• Compare Q1 and Q2 performance</Text>
                            </VStack>
                          </VStack>
                        </CardBody>
                      </Card>
                    )}
                  </Box>
                }
              />
            </TabPanel>

            {/* Upload Tab */}
            <TabPanel px={0}>
              <Card>
                <CardBody p={{ base: 6, md: 8 }}>
                  <form onSubmit={handleFileUpload}>
                    <VStack spacing={6} align="stretch">
                      <Alert 
                        status="info" 
                        borderRadius="12px"
                        bg={infoBg}
                        borderLeft="4px solid"
                        borderColor="brand.500"
                      >
                        <AlertIcon color="brand.500" />
                        <Text fontSize="sm" fontWeight="500">
                          Upload CSV, Excel, or JSON files to analyze your data
                        </Text>
                      </Alert>

                      <FormControl isRequired>
                        <FormLabel fontWeight="500" mb={3}>User ID</FormLabel>
                        <Input
                          value={userId}
                          onChange={(e) => setUserId(e.target.value)}
                          placeholder="Enter your user ID"
                          size="lg"
                          fontSize="md"
                          border="1px solid"
                          borderColor="gray.300"
                          _dark={{ borderColor: 'gray.600' }}
                        />
                      </FormControl>

                      <FormControl isRequired>
                        <FormLabel fontWeight="500" mb={3}>Select File</FormLabel>
                        <Input
                          type="file"
                          accept=".csv,.xlsx,.xls,.json"
                          onChange={(e) => setFile(e.target.files?.[0] || null)}
                          p={3}
                          size="lg"
                          fontSize="sm"
                          border="1px solid"
                          borderColor="gray.300"
                          _dark={{ borderColor: 'gray.600' }}
                          sx={{
                            '::file-selector-button': {
                              height: '36px',
                              marginRight: '12px',
                              borderRadius: '8px',
                              border: 'none',
                              bg: fileButtonBg,
                              fontWeight: '500',
                              fontSize: 'sm',
                              cursor: 'pointer',
                              transition: 'all 0.2s',
                              _hover: {
                                bg: fileButtonHoverBg,
                              },
                            },
                          }}
                        />
                      </FormControl>

                      <Button
                        type="submit"
                        colorScheme="brand"
                        size="lg"
                        height="56px"
                        fontSize="md"
                        fontWeight="600"
                        isLoading={uploadLoading}
                        loadingText="Uploading..."
                        mt={2}
                      >
                        Upload Data
                      </Button>
                    </VStack>
                  </form>
                </CardBody>
              </Card>
            </TabPanel>

            {/* Guide Tab */}
            <TabPanel px={0}>
              <Card>
                <CardBody p={{ base: 6, md: 8 }}>
                  <VStack spacing={6} align="stretch">
                    <Heading size="lg" fontWeight="700" mb={2}>
                      📚 How to Use This App
                    </Heading>
                    
                    <Box 
                      p={6} 
                      bg={stepBg}
                      borderRadius="16px"
                      borderLeft="4px solid"
                      borderColor="brand.500"
                    >
                      <Heading size="md" mb={3} fontWeight="600">Step 1: Upload Your Data</Heading>
                      <Text fontSize="md" color="gray.700" _dark={{ color: 'gray.300' }} lineHeight="1.7">
                        Go to the &ldquo;Upload&rdquo; tab and upload your CSV, Excel, or JSON file.
                        The system will process and index your data for analysis.
                      </Text>
                    </Box>

                    <Box 
                      p={6} 
                      bg={stepBg}
                      borderRadius="16px"
                      borderLeft="4px solid"
                      borderColor="brand.500"
                    >
                      <Heading size="md" mb={3} fontWeight="600">Step 2: Ask Questions</Heading>
                      <Text fontSize="md" color="gray.700" _dark={{ color: 'gray.300' }} mb={3} lineHeight="1.7">
                        Switch to the &ldquo;Analyze&rdquo; tab and ask questions about your data in natural language.
                      </Text>
                      <Text fontSize="sm" fontWeight="600" mb={2}>Examples:</Text>
                      <VStack align="stretch" spacing={2} pl={4}>
                        <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                          • What are the top 5 products by revenue?
                        </Text>
                        <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                          • Show me sales trends over the last 6 months
                        </Text>
                        <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                          • Which customers have the highest lifetime value?
                        </Text>
                        <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                          • Compare Q1 and Q2 performance
                        </Text>
                      </VStack>
                    </Box>

                    <Box 
                      p={6} 
                      bg={stepBg}
                      borderRadius="16px"
                      borderLeft="4px solid"
                      borderColor="brand.500"
                    >
                      <Heading size="md" mb={3} fontWeight="600">Step 3: Get Insights</Heading>
                      <Text fontSize="md" color="gray.700" _dark={{ color: 'gray.300' }} mb={3} lineHeight="1.7">
                        The AI will analyze your data and provide:
                      </Text>
                      <VStack align="stretch" spacing={2} pl={4}>
                        <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                          ✅ Natural language answers
                        </Text>
                        <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                          📊 Interactive visualizations
                        </Text>
                        <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                          📈 Forecasts (when enabled)
                        </Text>
                        <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                          💡 Data insights
                        </Text>
                      </VStack>
                    </Box>

                    <Box 
                      p={6} 
                      bg={stepBg}
                      borderRadius="16px"
                      borderLeft="4px solid"
                      borderColor="brand.500"
                    >
                      <Heading size="md" mb={3} fontWeight="600">Step 4: Export Results</Heading>
                      <Text fontSize="md" color="gray.700" _dark={{ color: 'gray.300' }} lineHeight="1.7">
                        Use the visualization export options to download charts and reports.
                      </Text>
                    </Box>

                    <Alert 
                      status="success" 
                      borderRadius="16px"
                      bg={successBg}
                      borderLeft="4px solid"
                      borderColor="green.500"
                    >
                      <AlertIcon color="green.500" />
                      <Box>
                        <AlertTitle fontWeight="600" fontSize="md">Pro Tip!</AlertTitle>
                        <AlertDescription fontSize="sm" mt={1}>
                          Enable &ldquo;Generate Visualizations&rdquo; for charts and graphs, and &ldquo;Include Forecasting&rdquo; 
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
    </Box>
  );
}
