import { useState } from 'react';
import axios from 'axios';
import { MessageSquare, Send, FileText, Loader2 } from 'lucide-react';

export default function ChatAssistant() {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState<{ role: 'user' | 'ai', content: string }[]>([]);
    const [loading, setLoading] = useState(false);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMsg = input;
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setInput('');
        setLoading(true);

        try {
            const res = await axios.post('http://localhost:8000/api/v1/chat', { message: userMsg });
            setMessages(prev => [...prev, { role: 'ai', content: res.data.reply }]);
        } catch (err) {
            setMessages(prev => [...prev, { role: 'ai', content: "Error connecting to AI." }]);
        } finally {
            setLoading(false);
        }
    };

    const downloadReport = async (content: string) => {
        try {
            const response = await axios.post('http://localhost:8000/api/v1/generate-report',
                { message: content },
                { responseType: 'blob' }
            );
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'clinical_report.pdf');
            document.body.appendChild(link);
            link.click();
        } catch (e) {
            console.error("PDF Error", e);
        }
    };

    return (
        <div className="flex flex-col h-[600px] bg-white rounded-lg shadow-lg border border-gray-200">
            <div className="p-4 border-b bg-ge-blue text-white rounded-t-lg flex items-center">
                <MessageSquare className="w-5 h-5 mr-2" />
                <h2 className="font-semibold">AI Clinical Assistant</h2>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((m, i) => (
                    <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] p-3 rounded-lg text-sm ${m.role === 'user' ? 'bg-blue-100 text-blue-900' : 'bg-gray-100 text-gray-800'
                            }`}>
                            <p className="whitespace-pre-wrap">{m.content}</p>
                            {m.role === 'ai' && (
                                <button
                                    onClick={() => downloadReport(m.content)}
                                    className="mt-2 text-xs flex items-center text-ge-blue hover:underline"
                                >
                                    <FileText className="w-3 h-3 mr-1" /> Save as PDF Report
                                </button>
                            )}
                        </div>
                    </div>
                ))}
                {loading && <Loader2 className="w-5 h-5 animate-spin text-gray-400" />}
            </div>

            <div className="p-4 border-t flex">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Ask about a device (e.g. 'Status of WEARABLE-003?')"
                    className="flex-1 border rounded-l-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ge-blue"
                />
                <button
                    onClick={sendMessage}
                    disabled={loading}
                    className="bg-ge-blue text-white px-4 py-2 rounded-r-md hover:bg-blue-700 disabled:opacity-50"
                >
                    <Send className="w-4 h-4" />
                </button>
            </div>
        </div>
    );
}