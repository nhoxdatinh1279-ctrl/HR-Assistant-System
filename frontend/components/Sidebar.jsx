// components/Sidebar.jsx
import { FileText, Zap, AlertCircle } from 'lucide-react';

export default function Sidebar({ onClearChat, hasMessages, language = 'en' }) {

    const sidebarConfig = {
        en: {
            systemStatus: 'System Status',
            apiConnected: 'API Connected',
            vectorDbReady: 'Vector DB Ready',
            quickActions: 'Quick Actions',
            commonQuestions: 'Common Questions',
            companyPolicies: 'Company Policies',
            tips: 'Tips',
            tipsList: [
                '• Ask about leave balance directly',
                '• Query pay dates and salary info',
                '• Ask about company policies',
                '• Get contact info for HR'
            ],
            clearChat: 'Clear Chat History'
        },
        vi: {
            systemStatus: 'Trạng Thái Hệ Thống',
            apiConnected: 'API Đã Kết Nối',
            vectorDbReady: 'Vector DB Sẵn Sàng',
            quickActions: 'Thao Tác Nhanh',
            commonQuestions: 'Câu Hỏi Thường Gặp',
            companyPolicies: 'Chính Sách Công Ty',
            tips: 'Mẹo',
            tipsList: [
                '• Hỏi về số ngày nghỉ phép còn lại',
                '• Hỏi về ngày lương và thông tin lương',
                '• Hỏi về chính sách công ty',
                '• Nhận thông tin liên hệ HR'
            ],
            clearChat: 'Xóa Lịch Sử Chat'
        }
    };

    const config = sidebarConfig[language];
    return (
        <div className="w-64 bg-white border-l border-gray-200 p-6 flex flex-col">
            <div className="space-y-6 flex-1">
                {/* System Status */}
                <div>
                    <h3 className="font-semibold text-gray-800 text-sm mb-3">{config.systemStatus}</h3>
                    <div className="space-y-2">
                        <div className="flex items-center gap-2 text-sm">
                            <div className="w-2 h-2 rounded-full bg-green-500"></div>
                            <span className="text-gray-700">{config.apiConnected}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                            <div className="w-2 h-2 rounded-full bg-green-500"></div>
                            <span className="text-gray-700">{config.vectorDbReady}</span>
                        </div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div>
                    <h3 className="font-semibold text-gray-800 text-sm mb-3">{config.quickActions}</h3>
                    <div className="space-y-2">
                        <button className="w-full text-left text-sm p-2 rounded hover:bg-gray-100 flex items-center gap-2 text-gray-700">
                            <Zap size={16} />
                            <span>{config.commonQuestions}</span>
                        </button>
                        <button className="w-full text-left text-sm p-2 rounded hover:bg-gray-100 flex items-center gap-2 text-gray-700">
                            <FileText size={16} />
                            <span>{config.companyPolicies}</span>
                        </button>
                    </div>
                </div>

                {/* Tips */}
                <div>
                    <h3 className="font-semibold text-gray-800 text-sm mb-3 flex items-center gap-2">
                        <AlertCircle size={16} />
                        {config.tips}
                    </h3>
                    <ul className="text-xs text-gray-600 space-y-2">
                        {config.tipsList.map((tip, index) => (
                            <li key={index}>{tip}</li>
                        ))}
                    </ul>
                </div>
            </div>

            {/* Clear Chat Button */}
            <button
                onClick={onClearChat}
                disabled={!hasMessages}
                className="w-full px-4 py-2 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium transition-colors"
            >
                {config.clearChat}
            </button>
        </div>
    );
}
