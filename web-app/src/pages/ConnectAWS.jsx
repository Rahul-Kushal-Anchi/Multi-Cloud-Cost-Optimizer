import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

export default function ConnectAWS() {
  const navigate = useNavigate();
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);
  const [hasConnection, setHasConnection] = useState(false);
  const [formData, setFormData] = useState({
    aws_role_arn: '',
    external_id: '',
    cur_bucket: '',
    cur_prefix: 'cur/',
    athena_workgroup: 'primary',
    athena_db: '',
    athena_table: '',
    athena_results_bucket: '',
    athena_results_prefix: 'athena-results/',
    region: 'us-east-1'
  });

  const token = localStorage.getItem('token');

  async function checkConnection() {
    try {
      const response = await fetch('/api/tenants/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      setHasConnection(data.tenant?.hasConnection || false);
      if (data.tenant?.hasConnection) {
        toast.success('AWS connection already configured');
      }
    } catch (error) {
      console.error('Failed to check connection:', error);
    }
  }

  useEffect(() => {
    // Check if already connected
    checkConnection();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleChange(e) {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setErr(null);
    setSaved(false);
    setLoading(true);

    try {
      const response = await fetch('/api/tenants/connect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error('Failed to save connection');
      }

      setSaved(true);
      setHasConnection(true);
      toast.success('AWS connection saved successfully!');
      
      // Navigate to dashboard
      setTimeout(() => navigate('/dashboard'), 1500);
    } catch (error) {
      setErr(error.message);
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  }

  if (hasConnection) {
    return (
      <div style={{ maxWidth: 720, margin: '40px auto', padding: 24 }}>
        <div style={{ background: '#d1fae5', padding: 20, borderRadius: 8, marginBottom: 20 }}>
          <h3 style={{ color: '#065f46', marginBottom: 10 }}>✅ AWS Connection Configured</h3>
          <p style={{ color: '#047857' }}>Your AWS billing connection is already set up. You can start viewing your costs.</p>
        </div>
        <button
          onClick={() => navigate('/dashboard')}
          style={{
            padding: '12px 24px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: 6,
            fontSize: 16,
            cursor: 'pointer'
          }}
        >
          Go to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div style={{
      maxWidth: 720,
      margin: '40px auto',
      background: '#fff',
      padding: 24,
      borderRadius: 12,
      boxShadow: '0 2px 12px rgba(0,0,0,0.08)'
    }}>
      <h2 style={{ marginBottom: 20 }}>Connect AWS Billing</h2>

      <div style={{ background: '#eff6ff', padding: 15, borderRadius: 8, marginBottom: 20 }}>
        <h4 style={{ marginBottom: 10 }}>Setup Instructions:</h4>
        <ol style={{ marginLeft: 20 }}>
          <li style={{ marginBottom: 10 }}>Deploy our CloudFormation stack in your AWS account (read-only role)</li>
          <li style={{ marginBottom: 10 }}>Get the Role ARN and External ID from the stack outputs</li>
          <li>Enter your AWS billing connection details below</li>
        </ol>
      </div>

      {err && (
        <div style={{ color: 'crimson', padding: 10, background: '#fee', borderRadius: 5, marginBottom: 15 }}>
          {String(err)}
        </div>
      )}

      {saved && (
        <div style={{ color: 'green', padding: 10, background: '#efe', borderRadius: 5, marginBottom: 15 }}>
          Saved! Redirecting to dashboard...
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {Object.keys(formData).map(key => (
          <div key={key} style={{ marginBottom: 15 }}>
            <label style={{ display: 'block', marginBottom: 5 }}>
              {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </label>
            <input
              type="text"
              name={key}
              value={formData[key]}
              onChange={handleChange}
              required
              placeholder={`Enter ${key}`}
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #ccc',
                borderRadius: 6,
                fontSize: 14
              }}
            />
          </div>
        ))}

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
          {loading ? 'Saving...' : 'Save Connection'}
        </button>
      </form>
    </div>
  );
}


