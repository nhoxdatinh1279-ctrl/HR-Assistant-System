// components/ChatBox.jsx
import { useEffect, useRef } from 'react';
import { Bot, User } from 'lucide-react';

export default function ChatBox({ messages, isLoading }) {
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    return (
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
            {messages.length === 0 ? (
                <div className="flex items-center justify-center h-full text-gray-400">
                    <div className="text-center">
                        <Bot size={48} className="mx-auto mb-4 opacity-50" />
                        <p className="text-lg font-medium">Welcome to HR Assistant</p>
                        <p className="text-sm mt-2">Ask me anything about HR policies, benefits, and leave</p>
                    </div>
                </div>
            ) : (
                messages.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div className={`flex gap-2 ${
                            // Check if it's a CV evaluation response (contains specific formatting)
                            msg.content.includes('CV EVALUATION RESULT') || msg.content.includes('KẾT QUẢ ĐÁNH GIÁ CV') 
                                ? 'max-w-full' 
                                : 'max-w-md lg:max-w-2xl'
                        } ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                            <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${msg.role === 'user' ? 'bg-blue-500' : 'bg-green-500'
                                }`}>
                                {msg.role === 'user' ? (
                                    <User size={20} className="text-white" />
                                ) : (
                                    <Bot size={20} className="text-white" />
                                )}
                            </div>
                            <div className={`message ${msg.role === 'user' ? 'message-user' : 'message-bot'} ${
                                // Make CV evaluation messages wider
                                msg.content.includes('CV EVALUATION RESULT') || msg.content.includes('KẾT QUẢ ĐÁNH GIÁ CV')
                                    ? 'cv-evaluation-message' 
                                    : ''
                            }`}>
                                <div
                                    className="message-content"
                                    dangerouslySetInnerHTML={{ __html: msg.content }}
                                />
                                {msg.sources && msg.sources.length > 0 && (
                                    <div className="mt-3 pt-3 border-t border-gray-300 space-y-2">
                                        <p className="text-xs font-semibold text-gray-600">Sources:</p>
                                        {msg.sources.map((source, i) => (
                                            <div key={i} className="text-xs bg-gray-100 p-2 rounded">
                                                <p className="font-medium text-gray-700">{source.question}</p>
                                                <p className="text-gray-600 mt-1">{source.content}</p>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                ))
            )}
            {isLoading && (
                <div className="flex justify-start">
                    <div className="flex gap-2">
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-500 flex items-center justify-center">
                            <Bot size={20} className="text-white" />
                        </div>
                        <div className="message message-bot">
                            <div className="loader">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
            <div ref={messagesEndRef} />
        </div>
    );
}
