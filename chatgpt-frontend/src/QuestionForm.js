import React, { useState } from 'react';
import axios from 'axios';

function QuestionForm() {
    const [question, setQuestion] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');

    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true); // リクエスト開始時にloadingをtrueに設定

        try {
            const response = await fetch('http://localhost:3100/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({ question }),
            });

            const data = await response.json();

            if (data.error) {
                setMessage(data.error); // エラーメッセージを表示
            } else if (data.question && data.answer) {
                setResult(data); // 質問と回答を設定
                setMessage('');
            } else {
                setMessage('Failed to get a valid response.');
            }
        } catch (error) {
            console.error('Error:', error);
            setMessage('An error occurred while fetching data.');
        } finally {
            setLoading(false); // リクエスト終了時にloadingをfalseに設定
        }
    };

    const handleLogout = async () => {
        try {
            await axios.post('http://localhost:3100/logout');
            window.location.reload();
        } catch (error) {
            console.error('Error logging out:', error);
        }
    };

    return (
        <div>
            <h1>ChatGPTに質問する</h1>
            <button onClick={handleLogout}>ログアウト</button>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>質問:</label>
                    <textarea
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        required
                    />
                </div>
                <button type="submit">送信</button>
            </form>
            {loading && <p>回答作成中...</p>} {/* loadingがtrueのときに表示 */}
            {result && (
                <div>
                    <h2>質問:</h2>
                    <p>{result.question}</p>
                    <h2>回答:</h2>
                    <p>{result.answer}</p>
                </div>
            )}
        </div>
    );
}

export default QuestionForm;