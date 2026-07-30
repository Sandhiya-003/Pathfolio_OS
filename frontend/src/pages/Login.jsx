// frontend/src/pages/Login.jsx
import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import ParticleCanvas from '../components/ParticleCanvas';
import { useAuth } from '../context/AuthContext';
import { ApiError } from '../lib/api';
import AuthTopNav from '../components/AuthTopNav';

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [formData, setFormData] = useState({
    identifier: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(formData.identifier.trim(), formData.password);
      navigate(location.state?.from || '/', { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleOAuth = (provider) => {
    const apiRoot = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/api\/?$/, '');
    window.location.href = `${apiRoot}/auth/${provider}`;
  };

  return (
    <div className="w-screen h-screen bg-[#080a0f] flex items-center justify-center p-4 md:p-8 font-sans-clean overflow-hidden">
      <div className="w-full h-full max-w-[1600px] max-h-[900px] bg-[#0d111a] rounded-3xl border border-slate-800/80 shadow-2xl overflow-hidden grid grid-cols-1 md:grid-cols-12">

        <div className="md:col-span-7 relative bg-[#090c13] p-10 md:p-16 flex flex-col justify-between overflow-hidden">
          <ParticleCanvas />

          <div className="relative z-10 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-3.5 h-3.5 bg-amber-500 transform rotate-45 shadow-sm shadow-amber-500/50"></div>
              <span className="text-2xl font-bold tracking-wider text-amber-500 font-brand">
                Pathfolio
              </span>
            </div>
          </div>

          <div className="relative z-10 my-auto py-8">
            <span className="text-xs uppercase tracking-[0.25em] text-amber-500/80 font-medium">
              THE DIGITAL VAULT
            </span>
            <h1 className="text-5xl lg:text-7xl font-serif-title text-slate-100 mt-4 font-normal leading-[1.1]">
              Archive Your <br />
              <span className="italic font-serif-title text-amber-500">Evolution.</span>
            </h1>
            <p className="text-slate-400 text-base mt-6 max-w-lg leading-relaxed font-light">
              Ingest every achievement, track your entire career journey, and own your digital identity with Pathfolio's proprietary identity architecture.
            </p>
          </div>

          <div className="relative z-10 text-xs text-slate-500 tracking-wide">
            © 2026 Pathfolio — Your Digital Identity OS
          </div>
        </div>

        <div className="md:col-span-5 p-10 md:p-16 flex flex-col justify-between bg-[#111622] border-l border-slate-800/50">

         <AuthTopNav />

          <div className="my-auto max-w-md w-full mx-auto">
            <h2 className="text-3xl font-serif-title text-slate-100 font-medium tracking-tight">
              Initiate Protocol
            </h2>
            <p className="text-xs text-slate-400 mt-2 font-light">
              Enter your credentials to access your secure node.
            </p>

            {error && (
              <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 text-red-400 text-xs rounded-xl">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="mt-8 space-y-5">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-2">
                  Email or Username
                </label>
                <input
                  type="text"
                  name="identifier"
                  value={formData.identifier}
                  onChange={handleChange}
                  placeholder="alexander@archive.io or @athorne"
                  className="w-full bg-[#090c13] border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-amber-500/80 transition-all"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-2">
                  Vault Key
                </label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="••••••••••••"
                  className="w-full bg-[#090c13] border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-amber-500/80 transition-all"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold py-3.5 rounded-xl text-xs uppercase tracking-widest transition-all shadow-lg shadow-amber-500/10 mt-4 disabled:opacity-50"
              >
                {loading ? 'Authenticating...' : 'Access Vault'}
              </button>
            </form>

            <div className="relative my-8 flex items-center justify-center">
              <div className="border-t border-slate-800 w-full"></div>
              <span className="bg-[#111622] px-3 text-[10px] text-slate-500 uppercase tracking-widest absolute">
                Or Sign In With
              </span>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => handleOAuth('google')}
                type="button"
                className="flex items-center justify-center gap-2.5 bg-[#090c13] border border-slate-800 hover:border-slate-700 text-slate-300 py-3 rounded-xl text-xs transition-all"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24">
                  <path fill="#EA4335" d="M12 5c1.6 0 3 .6 4.1 1.6l3.1-3.1C17.3 1.8 14.8 1 12 1 7.5 1 3.7 3.6 1.9 7.3l3.7 2.9C6.5 7.2 9 5 12 5z"/>
                  <path fill="#4285F4" d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.5h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.8z"/>
                  <path fill="#FBBC05" d="M5.6 14.8c-.2-.7-.4-1.5-.4-2.3s.2-1.6.4-2.3L1.9 7.3C.7 9.7 0 12.3 0 15s.7 5.3 1.9 7.7l3.7-2.9c-.3-.8-.5-1.6-.5-2.3z"/>
                  <path fill="#34A853" d="M12 23c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3 0-5.5-2.2-6.4-5.2L1.9 16C3.7 19.7 7.5 22.3 12 23z"/>
                </svg>
                Google
              </button>

              <button
                onClick={() => handleOAuth('github')}
                type="button"
                className="flex items-center justify-center gap-2.5 bg-[#090c13] border border-slate-800 hover:border-slate-700 text-slate-300 py-3 rounded-xl text-xs transition-all"
              >
                <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                  <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
                </svg>
                GitHub
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between text-xs text-slate-500 pt-6 border-t border-slate-800/40">
            <span>Don't have an account?</span>
            <Link to="/signup" className="text-amber-500 hover:underline font-medium">
              Create Account
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Login;