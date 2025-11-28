import React, { useState } from 'react';
import { Moon, Sun } from 'lucide-react';
import './ThemeSwitcher.css';

const ThemeSwitcher = () => {
    const [theme, setTheme] = useState('dark');

    const toggleTheme = (newTheme) => {
        setTheme(newTheme);
        if (newTheme === 'light') {
            document.documentElement.classList.add('light-mode');
        } else {
            document.documentElement.classList.remove('light-mode');
        }
    };

    return (
        <div className="settings-section glass-panel">
            <h3 className="section-title">Appearance</h3>
            <div className="theme-options">
                <button
                    className={`theme-btn ${theme === 'light' ? 'active' : ''}`}
                    onClick={() => toggleTheme('light')}
                >
                    <Sun size={20} />
                    <span>Light Mode</span>
                </button>
                <button
                    className={`theme-btn ${theme === 'dark' ? 'active' : ''}`}
                    onClick={() => toggleTheme('dark')}
                >
                    <Moon size={20} />
                    <span>Dark Mode</span>
                </button>
            </div>
        </div>
    );
};

export default ThemeSwitcher;
