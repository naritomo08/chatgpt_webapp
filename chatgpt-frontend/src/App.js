import React, { useState } from 'react';
import Login from './Login';
import QuestionForm from './QuestionForm';

function App() {
  const [loggedIn, setLoggedIn] = useState(false);

  return (
    <div>
      {loggedIn ? (
        <QuestionForm />
      ) : (
        <Login setLoggedIn={setLoggedIn} />
      )}
    </div>
  );
}

export default App;
