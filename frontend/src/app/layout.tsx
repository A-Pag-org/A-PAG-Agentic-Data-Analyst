import { Providers } from './providers';
import { Inter } from 'next/font/google';
import type { Metadata } from 'next';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'RAG Data Analyst',
  description: 'Advanced RAG-powered data analysis platform with agentic AI workflows',
  keywords: ['data analysis', 'RAG', 'AI', 'analytics', 'forecasting'],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}