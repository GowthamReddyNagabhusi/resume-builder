import Layout from "../components/Layout";
import "../styles/globals.css";
import { useRouter } from "next/router";
import { useEffect } from "react";
import { getToken } from "../lib/api";

export default function App({ Component, pageProps }) {
  const router = useRouter();

  useEffect(() => {
    const publicRoutes = ["/login", "/signup"];
    const token = getToken();
    if (!token && !publicRoutes.includes(router.pathname)) {
      router.replace("/login");
    }
  }, [router]);

  const getLayout = Component.getLayout || ((page) => <Layout>{page}</Layout>);
  return getLayout(<Component {...pageProps} />);
}
