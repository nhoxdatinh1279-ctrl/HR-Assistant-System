// pages/index.jsx
import { useState, useCallback } from 'react';
import axios from 'axios';
import ChatBox from '../components/ChatBox';
import InputBar from '../components/InputBar';
import Sidebar from '../components/Sidebar';
import CVUpload from '../components/CVUpload';
import { Globe, Languages, FileText } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [language, setLanguage] = useState('en'); // 'en' for English, 'vi' for Vietnamese
    const [showCVUpload, setShowCVUpload] = useState(false);
    const [selectedPosition, setSelectedPosition] = useState(null);

    const sendMessage = useCallback(async (userMessage) => {
        // Add user message to chat
        const newMessage = {
            role: 'user',
            content: userMessage,
        };
        setMessages((prev) => [...prev, newMessage]);
        setIsLoading(true);
        setError(null);

        try {
            // Send to backend
            const response = await axios.post(`${API_URL}/api/chat`, {
                message: userMessage,
                language: language,
            });

            const { answer, source_documents } = response.data;
            console.log('Backend response:', answer);

            // Check if it's a CV position list response
            const isPositionList = answer.includes('DANH SÁCH CÁC VỊ TRÍ') ||
                answer.includes('AVAILABLE POSITIONS');

            console.log('Is position list?', isPositionList);

            if (isPositionList) {
                // This is position list - show upload UI
                setShowCVUpload(true);
                console.log('CV Upload UI should show now');
            }

            // Check if it's a CV evaluation response
            const isEvaluation = answer.includes('KẾT QUẢ ĐÁNH GIÁ') ||
                answer.includes('CV EVALUATION');

            // Check if response contains position recommendations
            const positionMatch = answer.match(/(?:Position|Vị Trí):\s*(\w[\w\s]*?)(?:\n|$)/);
            if (positionMatch) {
                setSelectedPosition(positionMatch[1].trim());
            }

            // Add bot response
            const botMessage = {
                role: 'bot',
                content: answer,
                sources: source_documents || [],
            };
            setMessages((prev) => [...prev, botMessage]);
        } catch (err) {
            console.error('Error:', err);
            const errorMessage = {
                role: 'bot',
                content: `Sorry, I encountered an error: ${err.response?.data?.detail || err.message}. Please try again.`,
            };
            setMessages((prev) => [...prev, errorMessage]);
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    }, [language]);

    const clearChat = useCallback(() => {
        setMessages([]);
        setError(null);
        setShowCVUpload(false);
        setSelectedPosition(null);
    }, []);

    const handlePositionSelect = useCallback((position) => {
        console.log('Position selected:', position.name);
        setSelectedPosition(position.name);
    }, []);

    const handleCVSubmit = useCallback(async (fileContent, fileName) => {
        // Add user message indicating CV submission
        const userMessage = {
            role: 'user',
            content: `📎 Submitted CV: ${fileName}\n\nContent:\n${fileContent.substring(0, 500)}...`,
        };
        setMessages((prev) => [...prev, userMessage]);
        setIsLoading(true);

        try {
            // Prepare message with CV content and position
            let evaluationMessage = `Evaluate my CV for positions: ${fileContent}`;

            // Include selected position in message for backend to detect
            if (selectedPosition) {
                evaluationMessage = `Evaluate my CV specifically for ${selectedPosition} position:\n${fileContent}`;
                console.log('Selected position:', selectedPosition);
            } else {
                console.log('WARNING: No position selected!');
            }

            // Send CV to backend for evaluation
            const response = await axios.post(`${API_URL}/api/chat`, {
                message: evaluationMessage,
                language: language,
            });

            const { answer } = response.data;

            const botMessage = {
                role: 'bot',
                content: answer,
            };
            setMessages((prev) => [...prev, botMessage]);
            setShowCVUpload(false);
        } catch (err) {
            console.error('Error:', err);
            const errorMessage = {
                role: 'bot',
                content: language === 'en'
                    ? `Error evaluating CV: ${err.message}`
                    : `Lỗi đánh giá CV: ${err.message}`,
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    }, [language, selectedPosition]);

    const toggleLanguage = useCallback(() => {
        setLanguage(prev => prev === 'en' ? 'vi' : 'en');
    }, []);

    const languageConfig = {
        en: {
            title: 'Internal HR Assistant',
            subtitle: 'Ask me about policies, benefits, leave, and more',
            inputPlaceholder: 'Type your HR question here...',
        },
        vi: {
            title: 'Trợ Lý HR Nội Bộ',
            subtitle: 'Hỏi tôi về chính sách, phúc lợi, nghỉ phép và nhiều hơn nữa',
            inputPlaceholder: 'Nhập câu hỏi HR của bạn ở đây...',
        }
    };

    return (
        <div className="flex h-screen bg-white">
            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col">
                {/* Header */}
                <div className="border-b border-gray-200 bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 shadow">
                    <div className="flex justify-between items-center">
                        <div>
                            <h1 className="text-2xl font-bold">{languageConfig[language].title}</h1>
                            <p className="text-sm opacity-90">{languageConfig[language].subtitle}</p>
                        </div>

                        {/* Language Toggle Button */}
                        <button
                            onClick={toggleLanguage}
                            className="flex items-center space-x-2 bg-white/20 hover:bg-white/30 px-3 py-2 rounded-lg transition-colors duration-200"
                            title={language === 'en' ? 'Switch to Vietnamese' : 'Chuyển sang Tiếng Anh'}
                        >
                            <Languages size={20} />
                            <span className="font-medium">
                                {language === 'en' ? 'EN' : 'VI'}
                            </span>
                            <Globe size={16} />
                        </button>
                    </div>
                </div>

                {/* Chat Area */}
                <ChatBox messages={messages} isLoading={isLoading} />

                {/* CV Upload Component */}
                {showCVUpload && (
                    <div className="border-t border-gray-200 bg-gray-50 p-4">
                        <CVUpload
                            onCVSubmit={handleCVSubmit}
                            onPositionSelect={handlePositionSelect}
                            language={language}
                        />
                    </div>
                )}

                {/* Input Area */}
                <InputBar
                    onSendMessage={sendMessage}
                    isLoading={isLoading}
                    placeholder={languageConfig[language].inputPlaceholder}
                    language={language}
                />
            </div>

            {/* Sidebar */}
            <Sidebar onClearChat={clearChat} hasMessages={messages.length > 0} language={language} />
        </div>
    );
}
