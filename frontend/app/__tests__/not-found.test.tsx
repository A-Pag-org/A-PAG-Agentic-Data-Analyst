import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ChakraProvider, extendTheme } from '@chakra-ui/react';
import NotFound from '../not-found';

// Mock Next.js navigation
const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

// Create a test theme with brand colors
const testTheme = extendTheme({
  colors: {
    brand: {
      50: '#fef8e7',
      100: '#fce9b3',
      200: '#f9da80',
      300: '#f7cb4d',
      400: '#f5bc1a',
      500: '#f59e0b',
      600: '#c47d08',
      700: '#925c06',
      800: '#613b04',
      900: '#301a02',
    },
  },
});

// Helper function to render with Chakra UI provider
const renderWithChakra = (component: React.ReactElement) => {
  return render(
    <ChakraProvider theme={testTheme}>
      {component}
    </ChakraProvider>
  );
};

describe('NotFound Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the 404 heading', () => {
    renderWithChakra(<NotFound />);
    const heading = screen.getByRole('heading', { name: '404', level: 1 });
    expect(heading).toBeInTheDocument();
  });

  it('renders the "Page Not Found" heading', () => {
    renderWithChakra(<NotFound />);
    const heading = screen.getByRole('heading', { name: 'Page Not Found', level: 2 });
    expect(heading).toBeInTheDocument();
  });

  it('renders the description text', () => {
    renderWithChakra(<NotFound />);
    const description = screen.getByText(/The page you're looking for doesn't exist or has been moved/i);
    expect(description).toBeInTheDocument();
  });

  it('renders the "Go Back Home" button', () => {
    renderWithChakra(<NotFound />);
    const button = screen.getByRole('button', { name: /Go Back Home/i });
    expect(button).toBeInTheDocument();
  });

  it('navigates to home page when button is clicked', () => {
    renderWithChakra(<NotFound />);
    const button = screen.getByRole('button', { name: /Go Back Home/i });
    fireEvent.click(button);
    expect(mockPush).toHaveBeenCalledWith('/');
  });

  it('has correct structure with Container and VStack', () => {
    const { container } = renderWithChakra(<NotFound />);
    expect(container.querySelector('.chakra-container')).toBeInTheDocument();
    expect(container.querySelector('.chakra-stack')).toBeInTheDocument();
  });
});
