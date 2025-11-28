import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { LogIn, AlertCircle, Phone, KeyRound, ArrowLeft, Loader2 } from 'lucide-react';
import { sendOtpAPI, verifyOtpAPI } from '../../services/api';
import './Auth.css';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [phone, setPhone] = useState('');
    const [otp, setOtp] = useState('');
    const [error, setError] = useState('');
    const [step, setStep] = useState('credentials'); // 'credentials' | 'phone' | 'otp'
    const [loading, setLoading] = useState(false);
    const [userData, setUserData] = useState(null);
    const { login, completeLogin } = useAuth();
    const navigate = useNavigate();

    const handleCredentialsSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const result = await login(email, password);
            if (result.success) {
                setUserData(result.user);
                setStep('phone');
            } else {
                setError(result.error);
            }
        } catch (err) {
            setError('Login failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleSendOtp = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            // Format phone number
            let formattedPhone = phone.trim();
            if (!formattedPhone.startsWith('+')) {
                formattedPhone = '+91' + formattedPhone; // Default to India
            }

            const result = await sendOtpAPI(formattedPhone);
            if (result.success) {
                setPhone(formattedPhone);
                setStep('otp');
            } else {
                setError(result.error || 'Failed to send OTP');
            }
        } catch (err) {
            setError('Failed to send OTP. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleVerifyOtp = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const result = await verifyOtpAPI(phone, otp);
            if (result.success && result.verified) {
                // 2FA complete, set user and redirect
                if (userData) {
                    completeLogin(userData);
                }
                navigate('/');
            } else {
                setError(result.error || 'Invalid OTP code');
            }
        } catch (err) {
            setError('Verification failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleSkip2FA = () => {
        // Allow skipping 2FA for development
        if (userData) {
            completeLogin(userData);
        }
        navigate('/');
    };

    const renderCredentialsStep = () => (
        <form onSubmit={handleCredentialsSubmit} className="auth-form">
            <div className="form-group">
                <label>Email Address</label>
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="auth-input"
                    placeholder="name@company.com"
                    disabled={loading}
                />
            </div>

            <div className="form-group">
                <label>Password</label>
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="auth-input"
                    placeholder="••••••••"
                    disabled={loading}
                />
            </div>

            <button type="submit" className="auth-btn" disabled={loading}>
                {loading ? <Loader2 size={18} className="spin" /> : <LogIn size={18} />}
                {loading ? 'Signing In...' : 'Sign In'}
            </button>
        </form>
    );

    const renderPhoneStep = () => (
        <form onSubmit={handleSendOtp} className="auth-form">
            <div className="two-factor-info">
                <Phone size={24} />
                <p>Enter your phone number to receive a verification code</p>
            </div>

            <div className="form-group">
                <label>Phone Number</label>
                <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    required
                    className="auth-input"
                    placeholder="+91 9876543210"
                    disabled={loading}
                />
                <small style={{ opacity: 0.6 }}>Include country code (e.g., +91 for India)</small>
            </div>

            <button type="submit" className="auth-btn" disabled={loading}>
                {loading ? <Loader2 size={18} className="spin" /> : <Phone size={18} />}
                {loading ? 'Sending OTP...' : 'Send OTP'}
            </button>

            <button 
                type="button" 
                className="auth-btn secondary" 
                onClick={handleSkip2FA}
                style={{ marginTop: '10px', background: 'transparent', border: '1px solid rgba(255,255,255,0.2)' }}
            >
                Skip 2FA (Development Only)
            </button>
        </form>
    );

    const renderOtpStep = () => (
        <form onSubmit={handleVerifyOtp} className="auth-form">
            <div className="two-factor-info">
                <KeyRound size={24} />
                <p>Enter the 6-digit code sent to {phone}</p>
            </div>

            <div className="form-group">
                <label>Verification Code</label>
                <input
                    type="text"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    required
                    className="auth-input otp-input"
                    placeholder="000000"
                    maxLength={6}
                    disabled={loading}
                    style={{ letterSpacing: '0.5em', textAlign: 'center', fontSize: '1.5rem' }}
                />
            </div>

            <button type="submit" className="auth-btn" disabled={loading || otp.length !== 6}>
                {loading ? <Loader2 size={18} className="spin" /> : <KeyRound size={18} />}
                {loading ? 'Verifying...' : 'Verify Code'}
            </button>

            <button 
                type="button" 
                className="auth-btn secondary" 
                onClick={() => setStep('phone')}
                style={{ marginTop: '10px', background: 'transparent', border: '1px solid rgba(255,255,255,0.2)' }}
            >
                <ArrowLeft size={16} /> Change Phone Number
            </button>
        </form>
    );

    return (
        <div className="auth-container">
            <div className="auth-card glass-panel">
                <div className="auth-header">
                    <div className="auth-logo">F</div>
                    <h2>{step === 'credentials' ? 'Welcome Back' : 'Two-Factor Authentication'}</h2>
                    <p>
                        {step === 'credentials' && 'Sign in to continue to Filtr'}
                        {step === 'phone' && 'Secure your account with 2FA'}
                        {step === 'otp' && 'Almost there!'}
                    </p>
                </div>

                {error && (
                    <div className="auth-error">
                        <AlertCircle size={16} />
                        <span>{error}</span>
                    </div>
                )}

                {step === 'credentials' && renderCredentialsStep()}
                {step === 'phone' && renderPhoneStep()}
                {step === 'otp' && renderOtpStep()}

                {step === 'credentials' && (
                    <div className="auth-footer">
                        Don't have an account? <Link to="/signup">Sign up</Link>
                    </div>
                )}

                <div style={{ textAlign: 'center', padding: '20px', fontSize: '12px', opacity: 0.6 }}>
                    Made by OptiMl
                </div>
            </div>
        </div>
    );
};

export default Login;
