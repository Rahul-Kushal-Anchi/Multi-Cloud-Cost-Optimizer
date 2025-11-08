import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Cloud, Eye, EyeOff, Loader } from 'lucide-react';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../services/auth';

const Login = () => {
  const [mode, setMode] = useState('login'); // 'login' | 'signup'
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [signupForm, setSignupForm] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    company: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { login, register } = useAuth();

  const switchMode = (nextMode) => {
    setMode(nextMode);
    setError(null);
    setShowPassword(false);
  };

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const result = await login(loginForm.email, loginForm.password);
      if (!result.success) {
        throw new Error(result.error || 'Invalid email or password');
      }

      const role = result.role || 'member';
      toast.success('Login successful!');

      if (role === 'global_owner') {
        navigate('/admin', { replace: true });
      } else {
        navigate('/dashboard', { replace: true });
      }
    } catch (err) {
      const message = err?.message || 'Login failed. Please try again.';
      setError(message);
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignupSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (signupForm.password !== signupForm.confirmPassword) {
      const message = 'Passwords do not match';
      setError(message);
      toast.error(message);
      return;
    }

    setIsLoading(true);
    try {
      const result = await register({
        email: signupForm.email,
        password: signupForm.password,
        company: signupForm.company
      });

      if (!result.success) {
        throw new Error(result.error || 'Signup failed');
      }

      const role = result.role || 'member';
      toast.success('Welcome! Your account is ready.');

      if (role === 'global_owner') {
        navigate('/admin', { replace: true });
      } else {
        navigate('/connect', { replace: true });
      }
    } catch (err) {
      const message = err?.message || 'Signup failed. Please try again.';
      setError(message);
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoginChange = (e) => {
    setLoginForm({
      ...loginForm,
      [e.target.name]: e.target.value
    });
  };

  const handleSignupChange = (e) => {
    setSignupForm({
      ...signupForm,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-md w-full space-y-8"
      >
        <div className="text-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
            className="mx-auto h-16 w-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mb-4"
          >
            <Cloud className="h-8 w-8 text-white" />
          </motion.div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            AWS Cost Optimizer
          </h2>
          <p className="text-gray-600">
            {mode === 'login'
              ? 'Sign in to your account to continue'
              : 'Create your organization account to get started'}
          </p>
          <div className="mt-6 inline-flex rounded-lg bg-gray-200 p-1">
            <button
              onClick={() => switchMode('login')}
              className={`px-4 py-2 text-sm font-medium rounded-md transition ${
                mode === 'login'
                  ? 'bg-white text-blue-600 shadow'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => switchMode('signup')}
              className={`px-4 py-2 text-sm font-medium rounded-md transition ${
                mode === 'signup'
                  ? 'bg-white text-blue-600 shadow'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Create Account
            </button>
          </div>
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-white py-8 px-6 shadow-xl rounded-2xl"
        >
          {mode === 'login' ? (
            <form onSubmit={handleLoginSubmit} className="space-y-6">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email address
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={loginForm.email}
                  onChange={handleLoginChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="Enter your email"
                />
              </div>
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    required
                    value={loginForm.password}
                    onChange={handleLoginChange}
                    className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5 text-gray-400" />
                    ) : (
                      <Eye className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                </div>
              </div>
              <motion.button
                type="submit"
                disabled={isLoading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {isLoading ? (
                  <>
                    <Loader className="animate-spin h-5 w-5 mr-2" />
                    Signing in...
                  </>
                ) : (
                  'Sign in'
                )}
              </motion.button>
            </form>
          ) : (
            <form onSubmit={handleSignupSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Company name</label>
                <input
                  name="company"
                  type="text"
                  required
                  value={signupForm.company}
                  onChange={handleSignupChange}
                  placeholder="Acme Corp"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email address</label>
                <input
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={signupForm.email}
                  onChange={handleSignupChange}
                  placeholder="founder@acme.co"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
                <input
                  name="password"
                  type="password"
                  required
                  value={signupForm.password}
                  onChange={handleSignupChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="Enter a strong password"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Confirm password</label>
                <input
                  name="confirmPassword"
                  type="password"
                  required
                  value={signupForm.confirmPassword}
                  onChange={handleSignupChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="Re-enter your password"
                />
              </div>
              <motion.button
                type="submit"
                disabled={isLoading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {isLoading ? (
                  <>
                    <Loader className="animate-spin h-5 w-5 mr-2" />
                    Creating account...
                  </>
                ) : (
                  'Create account'
                )}
              </motion.button>
            </form>
          )}

          {error && (
            <div className="mt-6 p-3 rounded-md bg-red-50 border border-red-200 text-sm text-red-600">
              {error}
            </div>
          )}

          {mode === 'login' ? (
            <div className="mt-8 text-center text-sm text-gray-600">
              Need an account?{' '}
              <button
                onClick={() => switchMode('signup')}
                className="text-blue-600 hover:text-blue-500 font-medium"
              >
                Create one now
              </button>
            </div>
          ) : (
            <div className="mt-8 text-center text-sm text-gray-600">
              Already registered?{' '}
              <button
                onClick={() => switchMode('login')}
                className="text-blue-600 hover:text-blue-500 font-medium"
              >
                Sign in here
              </button>
            </div>
          )}
        </motion.div>
      </motion.div>
    </div>
  );
};

export default Login;
