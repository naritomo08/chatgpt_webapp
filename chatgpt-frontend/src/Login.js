import React, { useState } from 'react';
import axios from 'axios';

function Login({ setLoggedIn }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState(''); // メッセージ用の状態を追加

    const apiBaseUrl = process.env.REACT_APP_API_BASE_URL;

    const handleSubmit = async (event) => {
        event.preventDefault();
    
        try {
            const response = await axios.post(`${apiBaseUrl}/login`, { username, password }, { withCredentials: true });
            
            if (response.data.success) {
                setMessage(response.data.message);
                setLoggedIn(true);
            } else {
                setMessage(response.data.message);
            }
        } catch (error) {
            console.error('Login error:', error);
            setMessage('Login failed. Please try again.');
        }
    };

    return (
        <div className="max-w-md mx-auto mt-10 p-6 bg-white shadow-md rounded">
            <h1 className="text-2xl font-bold text-center mb-4">Login</h1>
            {message && <p className="mb-4 text-center text-red-500">{message}</p>} {/* メッセージ表示 */}
            <form onSubmit={handleSubmit}>
                <div className="mb-4">
                    <label className="block text-sm font-medium mb-2">Username:</label>
                    <input
                        type="text"
                        className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                </div>
                <div className="mb-4">
                    <label className="block text-sm font-medium mb-2">Password:</label>
                    <input
                        type="password"
                        className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button
                    type="submit"
                    className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded"
                >
                    Login
                </button>
            </form>
        </div>
    );
}

export default Login;