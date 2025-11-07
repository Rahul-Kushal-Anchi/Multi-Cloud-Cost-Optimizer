import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

export default function Login() {
  const navigate = useNavigate();
  const [mode, setMode] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [company, setCompany] = useState('');
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setErr(null);
    setLoading(true);

    try {
      const path = mode === 'login' ? '/api/auth/login' : '/api/auth/signup';
      const body = mode === 'login' 
        ? { email, password }
        : { email, password, company };

      const response = await fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      // Check if response is JSON
      const contentType = response.headers.get('content-type');
      let data;
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        const text = await response.text();
        throw new Error(`Server returned ${response.status}: ${text.substring(0, 200)}`);
      }

      if (!response.ok) {
        throw new Error(data.detail || data.message || `Authentication failed (${response.status})`);
      }

      // Validate response has required fields
      if (!data.access_token) {
        throw new Error('Invalid response: missing access_token');
      }

      // Store token
      localStorage.setItem('token', data.access_token);
      // Handle tenant_id being null for global_owner
      if (data.tenant_id !== null && data.tenant_id !== undefined) {
        localStorage.setItem('tenant_id', String(data.tenant_id));
      } else {
        localStorage.removeItem('tenant_id');
      }
      localStorage.setItem('user', JSON.stringify({ email: data.email, role: data.role }));

      toast.success(`Successfully ${mode === 'login' ? 'logged in' : 'signed up'}!`);
      
      // Navigate based on role - global_owner goes to dashboard, others to connect
      // Reload the page to refresh auth state in App.js
      if (data.role === 'global_owner') {
        window.location.href = '/dashboard';
      } else {
        window.location.href = '/connect';
      }
    } catch (error) {
      setErr(error.message);
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      maxWidth: 420,
      margin: '60px auto',
      background: '#fff',
      padding: 24,
      borderRadius: 12,
      boxShadow: '0 2px 12px rgba(0,0,0,0.08)'
    }}>
      <h2 style={{ marginBottom: 20 }}>{mode === 'login' ? 'Log in' : 'Sign up'}</h2>
      
      {err && (
        <div style={{ color: 'crimson', padding: 10, background: '#fee', borderRadius: 5, marginBottom: 15 }}>
          {String(err)}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {mode === 'signup' && (
          <div style={{ marginBottom: 15 }}>
            <label style={{ display: 'block', marginBottom: 5 }}>Company Name</label>
            <input
              type="text"
              value={company}
              onChange={e => setCompany(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #ccc',
                borderRadius: 6,
                fontSize: 14
              }}
            />
          </div>
        )}

        <div style={{ marginBottom: 15 }}>
          <label style={{ display: 'block', marginBottom: 5 }}>Email</label>
          <input
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '1px solid #ccc',
              borderRadius: 6,
              fontSize: 14
            }}
          />
        </div>

        <div style={{ marginBottom: 15 }}>
          <label style={{ display: 'block', marginBottom: 5 }}>Password</label>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '1px solid #ccc',
              borderRadius: 6,
              fontSize: 14
            }}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: 12,
            background: loading ? '#ccc' : '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: 6,
            fontSize: 16,
            fontWeight: 600,
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Loading...' : (mode === 'login' ? 'Log in' : 'Create account')}
        </button>
      </form>

      <p style={{ marginTop: 20, textAlign: 'center', color: '#666' }}>
        {mode === 'login' ? (
          <>No account? <button onClick={() => setMode('signup')} style={{ background: 'none', border: 'none', color: '#3b82f6', cursor: 'pointer', textDecoration: 'underline' }}>Sign up</button></>
        ) : (
          <>Have an account? <button onClick={() => setMode('login')} style={{ background: 'none', border: 'none', color: '#3b82f6', cursor: 'pointer', textDecoration: 'underline' }}>Log in</button></>
        )}
      </p>
    </div>
  );
}


