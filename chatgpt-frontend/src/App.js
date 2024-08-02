import React, { useState, useEffect } from 'react';
import Login from './Login';
import QuestionForm from './QuestionForm';

function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [config, setConfig] = useState({ apiBaseUrl: '', timeZone: '' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // ローカルストレージからログイン状態を復元
    const savedLoggedInState = localStorage.getItem('loggedIn');
    if (savedLoggedInState) {
      setLoggedIn(JSON.parse(savedLoggedInState));
    }

    // バックエンドから設定を取得
    fetch('http://localhost:3100/config')
      .then((response) => response.json())
      .then((data) => {
        setConfig(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error('Error loading config:', error);
        setError('設定の読み込みに失敗しました。');
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    // ログイン状態をローカルストレージに保存
    localStorage.setItem('loggedIn', JSON.stringify(loggedIn));
  }, [loggedIn]);

  if (loading) {
    return <div>ローディング中...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div>
      {loggedIn ? (
        <QuestionForm apiBaseUrl={config.apiBaseUrl} />
      ) : (
        <Login setLoggedIn={setLoggedIn} apiBaseUrl={config.apiBaseUrl} />
      )}
    </div>
  );
}

export default App;