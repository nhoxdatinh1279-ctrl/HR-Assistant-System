// components/InputBar.jsx
import { useState } from 'react';
import { Send } from 'lucide-react';

export default function InputBar({ onSendMessage, isLoading, placeholder, language }) {
    const [message, setMessage] = useState('');

    const defaultPlaceholder = language === 'vi'
        ? 'Hỏi tôi về chính sách HR, nghỉ phép, lương bổng, hoặc phúc lợi công ty...'
        : 'Ask me about HR policies, leave, pay, or company benefits...';

    const helpText = language === 'vi'
        ? 'Shift+Enter để xuống dòng • Enter để gửi'
        : 'Shift+Enter for new line • Enter to send';

    const sendTitle = language === 'vi'
        ? 'Gửi tin nhắn (Shift+Enter để xuống dòng)'
        : 'Send message (Shift+Enter for new line)';

    const handleSubmit = (e) => {
        e.preventDefault();
        if (message.trim() && !isLoading) {
            onSendMessage(message);
            setMessage('');
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
            handleSubmit(e);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="border-t border-gray-200 bg-white p-4">
            <div className="flex gap-3">
                <textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={placeholder || defaultPlaceholder}
                    className="flex-1 resize-none rounded-lg border border-gray-300 p-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 text-sm"
                    rows="3"
                    disabled={isLoading}
                />
                <button
                    type="submit"
                    disabled={!message.trim() || isLoading}
                    className="flex items-center justify-center w-12 h-12 rounded-lg bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    title={sendTitle}
                >
                    <Send size={20} />
                </button>
            </div>
            <p className="text-xs text-gray-500 mt-2">{helpText}</p>
        </form>
    );
}
