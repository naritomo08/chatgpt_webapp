function showLoading() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('result').style.display = 'none';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function submitQuestion(event) {
    event.preventDefault();
    showLoading();

    const formData = new FormData(document.getElementById('question-form'));
    fetch('/ask', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        showResult(data.question, data.answer);
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
    });
}

function clearQuestion() {
    document.getElementById('question').value = '';
}

function showResult(question, answer) {
    const chatHistoryDiv = document.getElementById('chat-history');

    // ユーザーの質問を表示
    const userCard = document.createElement('div');
    userCard.className = 'card mt-2';
    userCard.innerHTML = `
        <div class="card-header"><strong>ユーザー:</strong></div>
        <div class="card-body"><p>${question}</p></div>
    `;
    chatHistoryDiv.appendChild(userCard);

    // アシスタントの回答を表示
    const assistantCard = document.createElement('div');
    assistantCard.className = 'card mt-2';
    assistantCard.innerHTML = `
        <div class="card-header"><strong>アシスタント:</strong></div>
        <div class="card-body"><p>${answer}</p></div>
    `;
    chatHistoryDiv.appendChild(assistantCard);

    // 最新の結果にスクロール
    chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;
}