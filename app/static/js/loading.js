function showLoading() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('result').style.display = 'none';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function showResult(question, answer) {
    document.getElementById('result-question').innerHTML = question;
    document.getElementById('result-answer').innerHTML = answer;
    document.getElementById('result').style.display = 'block';
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

function submitQuestion(event) {
    event.preventDefault();
    const form = document.getElementById('question-form');
    const formData = new FormData(form);
    document.getElementById('loading').style.display = 'block';
    document.getElementById('result').style.display = 'none';
    fetch('/ask', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('result').style.display = 'block';
        document.getElementById('result-question').innerHTML = data.question;
        document.getElementById('result-answer').innerHTML = data.answer;
    });
}

function clearQuestion() {
    document.getElementById('question').value = '';
}