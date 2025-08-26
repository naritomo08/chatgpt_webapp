// ====== 表示制御ユーティリティ ======
function setVisibleById(id, on) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.toggle('hidden', !on);
}

function setResultVisible(on)  { setVisibleById('result',  on); }
function setLoadingVisible(on) { setVisibleById('loading', on); }

// ====== 画面制御 ======
function showLoading() {
  // 1フレーム挟んでペイントを強制（表示が一瞬で消える時でも視認しやすく）
  requestAnimationFrame(() => {
    setResultVisible(false);
    setLoadingVisible(true);
    // 画面外に出ている可能性に備えて中央へスクロール
    const el = document.getElementById('loading');
    if (el) el.scrollIntoView({ behavior: 'auto', block: 'center' });
  });
}

function hideLoading() {
  setLoadingVisible(false);
}

// ====== 送信フロー ======
function submitQuestion(event) {
  event.preventDefault();
  showLoading();

  const form = document.getElementById('question-form');
  const formData = new FormData(form);
  const t0 = performance.now();

  fetch('/ask', { method: 'POST', body: formData })
    .then(async (response) => {
      if (!response.ok) {
        const text = await response.text().catch(() => '');
        throw new Error(`HTTP ${response.status}: ${text || response.statusText}`);
      }
      return response.json();
    })
    .then((data) => {
      // 結果反映
      showResult(data.question, data.answer);

      // レイテンシ
      const roundtripMs = Math.round(performance.now() - t0);
      const latencyEl = document.getElementById('result-latency');
      if (latencyEl) {
        if (typeof data.latency_s === 'number' && typeof data.latency_ms === 'number') {
          latencyEl.textContent =
            `応答時間: ${data.latency_s.toFixed(3)} 秒（サーバ処理: ${data.latency_ms} ms） / 往復: ${roundtripMs} ms`;
        } else {
          latencyEl.textContent = `往復時間: ${roundtripMs} ms`;
        }
      }

      // 先に result を表示 → その後にローディングを消すとチラ見えが安定
      setResultVisible(true);
      hideLoading();

      const result = document.getElementById('result');
      if (result) result.scrollIntoView({ behavior: 'smooth', block: 'start' });
    })
    .catch((error) => {
      console.error('Error:', error);
      // エラー時もローディングを消して、結果欄にエラー表示（任意）
      hideLoading();
      const qEl = document.getElementById('result-question');
      const aEl = document.getElementById('result-answer');
      if (qEl) qEl.innerHTML = '';
      if (aEl) aEl.textContent = 'エラーが発生しました。もう一度お試しください。';
      setResultVisible(true);
    });
}

// ====== 履歴 & 結果反映 ======
function showResult(questionHTML, answerHTML) {
  const qEl = document.getElementById('result-question');
  const aEl = document.getElementById('result-answer');
  if (qEl) qEl.innerHTML = questionHTML;   // サニタイズ済みHTML前提
  if (aEl) aEl.innerHTML = answerHTML;

  const chatHistoryDiv = document.getElementById('chat-history');
  if (chatHistoryDiv) {
    const userCard = document.createElement('div');
    userCard.className = 'card mt-2';
    userCard.innerHTML = `
      <div class="card-header"><strong>ユーザー:</strong></div>
      <div class="card-body">${questionHTML}</div>
    `;
    chatHistoryDiv.appendChild(userCard);

    const assistantCard = document.createElement('div');
    assistantCard.className = 'card mt-2';
    assistantCard.innerHTML = `
      <div class="card-header"><strong>アシスタント:</strong></div>
      <div class="card-body">${answerHTML}</div>
    `;
    chatHistoryDiv.appendChild(assistantCard);

    chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;
  }
}

// ====== フォームに submit を紐付け ======
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('question-form');
  if (form) form.addEventListener('submit', submitQuestion);
});