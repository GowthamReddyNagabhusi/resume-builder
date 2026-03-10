import { useEffect } from "react";
import { useRouter } from "next/router";
import { getToken } from "../lib/api";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const token = getToken();
    router.replace(token ? "/dashboard" : "/login");
  }, [router]);

  return null;
}
