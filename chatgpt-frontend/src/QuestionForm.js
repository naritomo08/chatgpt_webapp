import React, { useState } from 'react';
import axios from 'axios';

function QuestionForm({ apiBaseUrl }) {
    const [question, setQuestion] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');

    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);

        try {
            const response = await axios.post(`${apiBaseUrl}/ask`, { question }, { withCredentials: true });

            const data = response.data;
            if (data.error) {
                setMessage(data.error);
            } else if (data.question && data.answer) {
                setResult(data);
                setMessage('');
            } else {
                setMessage('Failed to get a valid response.');
            }
        } catch (error) {
            console.error('Error:', error);
            setMessage('An error occurred while fetching data.');
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = async () => {
        try {
            await axios.post(`${apiBaseUrl}/logout`);
            window.location.reload();
        } catch (error) {
            console.error('Error logging out:', error);
        }
    };

    return (
        <div className="max-w-xl mx-auto mt-10 p-4">
            <h1 className="text-2xl font-bold text-center mb-4">ChatGPTに質問する</h1>
            <div className="flex justify-end mb-4">
                <button className="bg-gray-500 hover:bg-gray-600 text-white py-2 px-4 rounded" onClick={handleLogout}>
                    ログアウト
                </button>
            </div>
            <form onSubmit={handleSubmit}>
                <div className="mb-4">
                    <label className="block text-sm font-medium mb-2">質問:</label>
                    <textarea
                        className="form-control w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        required
                    />
                </div>
                <button
                    type="submit"
                    className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded"
                    disabled={loading}
                >
                    送信
                </button>
            </form>
            {loading && <p className="mt-3 text-blue-600">回答作成中...</p>}
            {message && <p className="mt-3 text-red-500">{message}</p>}
            {result && (
                <div className="mt-6">
                    <h2 className="font-bold text-lg">質問:</h2>
                    <div dangerouslySetInnerHTML={{ __html: result.question }} />
                    <h2 className="font-bold text-lg">回答:</h2>
                    <div dangerouslySetInnerHTML={{ __html: result.answer }} />
                </div>
            )}
        </div>
    );
}

export default QuestionForm;