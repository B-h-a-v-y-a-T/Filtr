import React from 'react';
import { MessageSquare } from 'lucide-react';
import './ChatBotButton.css';

const ChatBotButton = () => {
    return (
        <button className="chatbot-btn">
            <MessageSquare size={24} />
        </button>
    );
};

export default ChatBotButton;
