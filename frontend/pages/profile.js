import Head from "next/head";
import Layout from "../components/Layout";
import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function ProfilePage() {
  const [bundle, setBundle] = useState(null);

  useEffect(() => {
    api.getProfile().then(setBundle).catch(() => {});
  }, []);

  return (
    <>
      <Head><title>Profile</title></Head>
      <div>
        <h1 className="page-title">Career Profile</h1>
        <p className="page-sub">Structured data that powers all dynamic resume variants.</p>

        <div className="card" style={{ marginBottom: 16 }}>
          <h2 className="section-title">Personal</h2>
          <pre className="ai-output">{JSON.stringify(bundle?.profile || {}, null, 2)}</pre>
        </div>

        <div className="grid-2">
          <div className="card">
            <h2 className="section-title">Education</h2>
            <pre className="ai-output">{JSON.stringify(bundle?.education || [], null, 2)}</pre>
          </div>
          <div className="card">
            <h2 className="section-title">Projects</h2>
            <pre className="ai-output">{JSON.stringify(bundle?.projects || [], null, 2)}</pre>
          </div>
        </div>
      </div>
    </>
  );
}

ProfilePage.getLayout = (page) => <Layout>{page}</Layout>;
