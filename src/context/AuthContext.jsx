import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext(null);

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check for active session on mount (from localStorage)
        try {
            const savedSession = localStorage.getItem('filtr_session');
            if (savedSession) {
                const session = JSON.parse(savedSession);
                if (session.user && session.expiry && new Date(session.expiry) > new Date()) {
                    setUser(session.user);
                } else {
                    localStorage.removeItem('filtr_session');
                }
            }
        } catch (err) {
            console.error("Failed to restore session:", err);
            localStorage.removeItem('filtr_session');
        } finally {
            setLoading(false);
        }
    }, []);

    const login = async (email, password) => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();
            
            if (data.success && data.user) {
                // Don't set user yet - wait for 2FA verification
                // The Login component will call setUser after 2FA is complete
                return { success: true, user: data.user };
            } else {
                return { success: false, error: data.error || 'Login failed' };
            }
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, error: 'Unable to connect to server. Please try again.' };
        }
    };

    const completeLogin = (userData) => {
        // Called after 2FA verification is complete
        const session = {
            user: userData,
            expiry: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // 24h
        };
        localStorage.setItem('filtr_session', JSON.stringify(session));
        setUser(userData);
    };

    const signup = async (name, email, password) => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/signup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name, email, password }),
            });

            const data = await response.json();
            
            if (data.success && data.user) {
                // Auto login after signup
                const session = {
                    user: data.user,
                    expiry: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
                };
                localStorage.setItem('filtr_session', JSON.stringify(session));
                setUser(data.user);
                return { success: true };
            } else {
                return { success: false, error: data.error || 'Registration failed' };
            }
        } catch (error) {
            console.error('Signup error:', error);
            return { success: false, error: 'Unable to connect to server. Please try again.' };
        }
    };

    const logout = () => {
        localStorage.removeItem('filtr_session');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, setUser, login, signup, logout, loading, completeLogin }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
