import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';

export default function NotFound() {
  return (
    <Layout title="Page Not Found">
      <main
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
          textAlign: 'center',
          padding: '2rem',
        }}>
        <h1
          style={{
            fontSize: '6rem',
            fontWeight: 800,
            color: 'var(--taco-gold)',
            letterSpacing: '-0.04em',
            marginBottom: '0.5rem',
            lineHeight: 1,
          }}>
          404
        </h1>
        <p
          style={{
            fontSize: '1.5rem',
            fontWeight: 600,
            marginBottom: '0.5rem',
          }}>
          This page wandered off the jobsite.
        </p>
        <p
          style={{
            color: 'var(--taco-text-secondary)',
            marginBottom: '2rem',
            maxWidth: '420px',
          }}>
          The page you're looking for doesn't exist or has been moved. Let's get
          you back on track.
        </p>
        <div style={{display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center'}}>
          <Link
            className="button button--lg button--primary"
            to="/"
            style={{
              background: 'var(--taco-gold)',
              color: 'var(--taco-navy)',
              border: 'none',
              fontWeight: 700,
            }}>
            Back to Home
          </Link>
          <Link
            className="button button--lg button--outline button--secondary"
            to="/docs/intro">
            Read the Docs
          </Link>
        </div>
      </main>
    </Layout>
  );
}
