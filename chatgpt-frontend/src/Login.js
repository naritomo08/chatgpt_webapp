import React, { useState } from 'react';
import axios from 'axios';

function Login({ setLoggedIn }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState(''); // メッセージ用の状態を追加

    const handleSubmit = async (event) => {
        event.preventDefault();
    
        try {
            const response = await axios.post('http://localhost:3100/login', { username, password }, { withCredentials: true });
            
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
        <div>
            <h1>Login</h1>
            {message && <p>{message}</p>} {/* メッセージ表示 */}
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Username:</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label>Password:</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit">Login</button>
            </form>
        </div>
    );
}

export default Login;