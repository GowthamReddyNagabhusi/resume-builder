import '@/styles/globals.css';
import { AuthProvider } from '@/lib/context/AuthContext';

export default function App({ Component, pageProps }) {
  return (
    <AuthProvider>
      <Component {...pageProps} />
    </AuthProvider>
  );
}
