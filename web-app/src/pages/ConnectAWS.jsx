import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import costAPI from '../services/api';

export default function ConnectAWS() {
  const navigate = useNavigate();
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);
  const [hasConnection, setHasConnection] = useState(false);
  const [curBucketOptional, setCurBucketOptional] = useState(false);
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

  useEffect(() => {
    // Check if already connected
    checkConnection();
  }, []);

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

      if (data.tenant?.aws_configuration) {
        setFormData((prev) => ({
          ...prev,
          ...data.tenant.aws_configuration
        }));
      }
    } catch (error) {
      console.error('Error checking connection:', error);
    }
  }

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
      const payload = {
        aws_role_arn: formData.aws_role_arn,
        external_id: formData.external_id,
        region: formData.region,
      };

      if (!curBucketOptional || formData.cur_bucket) {
        payload.cur_bucket = formData.cur_bucket;
      }
      if (formData.cur_prefix) payload.cur_prefix = formData.cur_prefix;
      if (formData.athena_workgroup) payload.athena_workgroup = formData.athena_workgroup;
      if (formData.athena_db) payload.athena_db = formData.athena_db;
      if (formData.athena_table) payload.athena_table = formData.athena_table;
      if (formData.athena_results_bucket) payload.athena_results_bucket = formData.athena_results_bucket;
      if (formData.athena_results_prefix) payload.athena_results_prefix = formData.athena_results_prefix;

      await costAPI.post('/tenants/connect', payload);

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

  const inputClasses = "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors";

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

      <div className="bg-blue-50 border border-blue-100 rounded-lg p-5 mb-6">
        <h4 className="text-sm font-semibold text-blue-700 mb-3">Setup Instructions</h4>
        <ol className="list-decimal list-inside text-sm text-blue-800 space-y-2">
          <li>Click <strong>Launch Stack</strong> to deploy our CloudFormation template in your AWS account (read-only access only).</li>
          <li>After the stack finishes, copy the <strong>RoleArn</strong> and <strong>ExternalId</strong> from the stack outputs.</li>
          <li>Paste them below, choose your CUR bucket/region if different, and save the connection.</li>
        </ol>
        <a
          href="https://console.aws.amazon.com/cloudformation/home#/stacks/create/template?templateURL=https://YOUR-S3-BUCKET/cur-onboarding-template.yaml"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center mt-4 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md shadow hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Launch AWS CloudFormation Stack
        </a>
      </div>

      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
        <h4 className="text-sm font-semibold text-gray-700 mb-2">Default values</h4>
        <p className="text-xs text-gray-600">
          If you use our CloudFormation template, the following defaults are created automatically:
        </p>
        <ul className="list-disc list-inside text-xs text-gray-600 space-y-1 mt-2">
          <li>CUR prefix: <code>cur/</code></li>
          <li>Athena workgroup: <code>primary</code></li>
          <li>Athena results prefix: <code>athena-results/</code></li>
          <li>Region: <code>us-east-1</code></li>
        </ul>
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
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">AWS Role ARN*</label>
            <input
              type="text"
              name="aws_role_arn"
              value={formData.aws_role_arn}
              onChange={handleChange}
              required
              placeholder="arn:aws:iam::123456789012:role/CostOptimizerAccess"
              className={inputClasses}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">External ID*</label>
            <input
              type="text"
              name="external_id"
              value={formData.external_id}
              onChange={handleChange}
              required
              placeholder="Copy from CloudFormation outputs"
              className={inputClasses}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Region*</label>
            <input
              type="text"
              name="region"
              value={formData.region}
              onChange={handleChange}
              required
              placeholder="us-east-1"
              className={inputClasses}
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              CUR Bucket
              <span className="text-xs text-gray-500 ml-2">(leave blank if CloudFormation created this)</span>
            </label>
            <input
              type="text"
              name="cur_bucket"
              value={formData.cur_bucket}
              onChange={handleChange}
              disabled={curBucketOptional}
              placeholder="my-cur-bucket"
              className={`${inputClasses} ${curBucketOptional ? 'bg-gray-100 cursor-not-allowed' : ''}`}
            />
            <div className="mt-2 flex items-center text-xs text-gray-600">
              <input
                id="skip-cur-bucket"
                type="checkbox"
                checked={curBucketOptional}
                onChange={(event) => setCurBucketOptional(event.target.checked)}
                className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="skip-cur-bucket" className="ml-2">
                Use the default bucket created by the CloudFormation template
              </label>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">CUR Prefix</label>
            <input
              type="text"
              name="cur_prefix"
              value={formData.cur_prefix}
              onChange={handleChange}
              className={inputClasses}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Athena Workgroup</label>
            <input
              type="text"
              name="athena_workgroup"
              value={formData.athena_workgroup}
              onChange={handleChange}
              className={inputClasses}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Athena Database</label>
            <input
              type="text"
              name="athena_db"
              value={formData.athena_db}
              onChange={handleChange}
              className={inputClasses}
              placeholder="Optional – leave blank if default"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Athena Table</label>
            <input
              type="text"
              name="athena_table"
              value={formData.athena_table}
              onChange={handleChange}
              className={inputClasses}
              placeholder="Optional – leave blank if default"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Athena Results Bucket</label>
            <input
              type="text"
              name="athena_results_bucket"
              value={formData.athena_results_bucket}
              onChange={handleChange}
              className={inputClasses}
              placeholder="Optional – leave blank if default"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Athena Results Prefix</label>
            <input
              type="text"
              name="athena_results_prefix"
              value={formData.athena_results_prefix}
              onChange={handleChange}
              className={inputClasses}
            />
          </div>
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
          {loading ? 'Saving...' : 'Save Connection'}
        </button>
      </form>
    </div>
  );
}


