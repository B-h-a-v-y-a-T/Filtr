import React, { useEffect } from 'react';
import { CheckCircle, XCircle, AlertTriangle, Info } from 'lucide-react';
import './ToastMessage.css';

const ToastMessage = ({ type = 'info', message, onClose, duration = 3000 }) => {
    useEffect(() => {
        if (duration) {
            const timer = setTimeout(onClose, duration);
            return () => clearTimeout(timer);
        }
    }, [duration, onClose]);

    const icons = {
        success: <CheckCircle size={20} />,
        error: <XCircle size={20} />,
        warning: <AlertTriangle size={20} />,
        info: <Info size={20} />
    };

    return (
        <div className={`toast-message toast-${type}`}>
            <span className="toast-icon">{icons[type]}</span>
            <span className="toast-text">{message}</span>
            <button className="toast-close" onClick={onClose}>×</button>
        </div>
    );
};

export default ToastMessage;
