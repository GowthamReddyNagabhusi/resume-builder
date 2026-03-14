import '@/styles/globals.css';
import Head from 'next/head';
import { AuthProvider } from '@/lib/context/AuthContext';

export default function App({ Component, pageProps }) {
  return (
    <>
      <Head>
        <title>CareerForge — AI-Powered Resume Builder</title>
        <meta name="description" content="Compile structured career data into role-specific, ATS-optimized resumes using AI. The smartest way to build your resume." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <AuthProvider>
        <Component {...pageProps} />
      </AuthProvider>
    </>
  );
}
