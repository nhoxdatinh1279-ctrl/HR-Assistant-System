import React, { useState } from 'react';
import { Upload, File, X, ChevronDown } from 'lucide-react';

export default function CVUpload({ onCVSubmit, language = 'en', selectedPosition = null, onPositionSelect = null }) {
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [dragActive, setDragActive] = useState(false);
    const [chosenPosition, setChosenPosition] = useState(selectedPosition || null);
    const [showPositions, setShowPositions] = useState(false);

    const positions = [
        { id: 'python_developer', name: 'Python Developer', icon: '🐍' },
        { id: 'java_developer', name: 'Java Developer', icon: '☕' },
        { id: 'ai_ml_engineer', name: 'AI/ML Engineer', icon: '🤖' },
        { id: 'frontend_developer', name: 'Frontend Developer', icon: '🎨' },
        { id: 'devops_engineer', name: 'DevOps Engineer', icon: '🔧' },
        { id: 'full_stack_developer', name: 'Full Stack Developer', icon: '🚀' },
        { id: 'data_engineer', name: 'Data Engineer', icon: '📊' },
        { id: 'qa_engineer', name: 'QA Engineer', icon: '✅' },
    ];

    const messages = {
        en: {
            title: 'Upload CV',
            subtitle: 'Drag and drop your CV or click to select',
            acceptedFormats: 'Accepted: PDF, DOC, DOCX, TXT',
            uploadButton: 'Choose File',
            submitButton: 'Evaluate CV',
            cancel: 'Cancel',
            selectPosition: 'Select Position',
            selectPositionPlaceholder: 'Choose a position to evaluate for...',
            noPositionWarning: '⚠️ Please select a position first'
        },
        vi: {
            title: 'Upload CV',
            subtitle: 'Kéo thả hoặc click để chọn file CV',
            acceptedFormats: 'Chấp nhận: PDF, DOC, DOCX, TXT',
            uploadButton: 'Chọn File',
            submitButton: 'Đánh Giá CV',
            cancel: 'Hủy',
            selectPosition: 'Chọn Vị Trí',
            selectPositionPlaceholder: 'Chọn vị trí để đánh giá...',
            noPositionWarning: '⚠️ Vui lòng chọn vị trí trước'
        }
    };

    const t = messages[language] || messages['en'];

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            setSelectedFile(files[0]);
        }
    };

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files.length > 0) {
            setSelectedFile(e.target.files[0]);
        }
    };

    const handlePositionSelect = (position) => {
        setChosenPosition(position.name);
        setShowPositions(false);
        if (onPositionSelect) {
            onPositionSelect(position);
        }
    };

    const handleSubmit = async () => {
        if (!selectedFile || !chosenPosition) return;

        setUploading(true);

        try {
            const reader = new FileReader();
            reader.onload = (e) => {
                const content = e.target.result;
                // Extract base64 content (remove data:...;base64, prefix if present)
                const base64Content = content.includes(',') ? content.split(',')[1] : content;
                
                // Create message with proper format: "Evaluate my CV for [position] | filename | base64_content"
                const positionName = chosenPosition.toLowerCase().replace(/\s+/g, '_');
                const fileName = selectedFile.name;
                const message = `Evaluate my CV for ${chosenPosition} | ${fileName} | ${base64Content}`;
                
                console.log(`[CV] Position: ${chosenPosition}, File: ${fileName}`);
                console.log(`[CV] Base64 size: ${base64Content.length} bytes`);
                
                onCVSubmit(message, fileName);
                setSelectedFile(null);
                setChosenPosition(null);
            };
            // Read file as data URL (which includes base64 encoding)
            reader.readAsDataURL(selectedFile);
        } catch (error) {
            console.error('Error reading file:', error);
        } finally {
            setUploading(false);
        }
    };

    const handleCancel = () => {
        setSelectedFile(null);
    };

    return (
        <div className="w-full max-w-2xl mx-auto p-4">
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border-2 border-dashed border-blue-300 p-6">
                {/* Title */}
                <div className="text-center mb-6">
                    <Upload size={32} className="mx-auto text-blue-600 mb-2" />
                    <h3 className="text-lg font-semibold text-gray-800">{t.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">{t.subtitle}</p>
                </div>

                {/* Position Selector */}
                <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">{t.selectPosition}</label>
                    <div className="relative">
                        <button
                            onClick={() => setShowPositions(!showPositions)}
                            className="w-full px-4 py-3 bg-white border-2 border-gray-300 rounded-lg text-left flex items-center justify-between hover:border-blue-400 transition-colors"
                        >
                            <span className={chosenPosition ? 'text-gray-800' : 'text-gray-500'}>
                                {chosenPosition || t.selectPositionPlaceholder}
                            </span>
                            <ChevronDown size={20} className={`text-gray-400 transition-transform ${showPositions ? 'rotate-180' : ''}`} />
                        </button>

                        {/* Dropdown */}
                        {showPositions && (
                            <div className="absolute top-full left-0 right-0 mt-2 bg-white border-2 border-gray-300 rounded-lg shadow-lg z-10 max-h-64 overflow-y-auto">
                                {positions.map((pos) => (
                                    <button
                                        key={pos.id}
                                        onClick={() => handlePositionSelect(pos)}
                                        className="w-full px-4 py-3 text-left hover:bg-blue-50 border-b border-gray-200 last:border-b-0 flex items-center gap-2 transition-colors"
                                    >
                                        <span className="text-xl">{pos.icon}</span>
                                        <span className="text-gray-800">{pos.name}</span>
                                        {chosenPosition === pos.name && (
                                            <span className="ml-auto text-blue-600">✓</span>
                                        )}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Upload Area */}
                <div
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${dragActive
                        ? 'border-blue-500 bg-blue-100'
                        : 'border-gray-300 bg-gray-50 hover:border-blue-400'
                        }`}
                >
                    <input
                        type="file"
                        onChange={handleFileChange}
                        accept=".pdf,.doc,.docx,.txt"
                        className="hidden"
                        id="cvInput"
                    />
                    <label htmlFor="cvInput" className="cursor-pointer">
                        {selectedFile ? (
                            <div className="flex items-center justify-center gap-2">
                                <File size={20} className="text-green-600" />
                                <span className="text-sm font-medium text-green-600">{selectedFile.name}</span>
                            </div>
                        ) : (
                            <div>
                                <p className="text-gray-700 font-medium mb-1">{t.uploadButton}</p>
                                <p className="text-xs text-gray-500">{t.acceptedFormats}</p>
                            </div>
                        )}
                    </label>
                </div>

                {/* Supported Formats */}
                <p className="text-xs text-gray-500 text-center mt-3">{t.acceptedFormats}</p>

                {/* Warning if no position selected */}
                {selectedFile && !chosenPosition && (
                    <div className="mt-4 p-3 bg-yellow-50 border-l-4 border-yellow-400 text-yellow-800 text-sm">
                        {t.noPositionWarning}
                    </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-2 mt-4">
                    {selectedFile && (
                        <button
                            onClick={handleCancel}
                            disabled={uploading}
                            className="flex-1 px-4 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 disabled:opacity-50 transition-colors text-sm font-medium flex items-center justify-center gap-2"
                        >
                            <X size={16} />
                            {t.cancel}
                        </button>
                    )}
                    <button
                        onClick={handleSubmit}
                        disabled={!selectedFile || !chosenPosition || uploading}
                        className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors text-sm font-medium flex items-center justify-center gap-2"
                    >
                        {uploading ? (
                            <>
                                <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                                Uploading...
                            </>
                        ) : (
                            <>
                                <Upload size={16} />
                                {t.submitButton}
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}
