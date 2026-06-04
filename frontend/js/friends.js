import { apiFetch } from './api.js';

let currentUserId = null;
let currentUserData = null;
let activeChatUserId = null;
let activeChatFriend = null;
let pollInterval = null;
let lastMessageId = 0;

export function init(userId, userData) {
  currentUserId = userId;
  currentUserData = userData;
  loadFriends();
  loadRequests();
}

// ── Danh sách bạn bè ─────────────────────────────────────

async function loadFriends() {
  const listEl = document.getElementById('friends-list');
  try {
    const res = await apiFetch('/friends');
    listEl.innerHTML = '';
    if (res.data.length === 0) {
      listEl.innerHTML = '<p class="friends-empty">Oops, có vẻ như chưa có ai ở đây cả!</p>';
      return;
    }
    res.data.forEach(f => listEl.appendChild(renderFriendItem(f)));
  } catch {
    listEl.innerHTML = '<p class="friends-empty">Không thể tải danh sách bạn bè.</p>';
  }
}

function renderFriendItem(friend) {
  const name = friend.display_name || friend.username;
  const item = document.createElement('div');
  item.className = 'friend-item';
  item.dataset.userId = friend.id;
  item.title = name;

  const avatarHtml = friend.avatar_url
    ? `<img src="${friend.avatar_url}" class="friend-avatar" alt="${name}" />`
    : `<div class="friend-avatar friend-avatar-placeholder">${name[0].toUpperCase()}</div>`;

  item.innerHTML = `${avatarHtml}<span class="friend-item-name">${name}</span>`;

  item.addEventListener('click', () => openChat(friend));
  return item;
}

// ── Lời mời kết bạn ──────────────────────────────────────

async function loadRequests() {
  try {
    const res = await apiFetch('/friends/requests');
    const badge = document.getElementById('request-badge');
    const count = res.data.length;
    badge.textContent = count > 0 ? count : '';
    badge.style.display = count > 0 ? 'flex' : 'none';

    const panel = document.getElementById('requests-panel');
    panel.innerHTML = '';
    if (count === 0) {
      panel.innerHTML = '<p class="friends-empty">Không có lời mời nào.</p>';
      return;
    }
    res.data.forEach(req => {
      const name = req.sender_display_name || req.sender_username;
      const el = document.createElement('div');
      el.className = 'request-item';
      el.innerHTML = `
        <span class="request-name">${name} <small>@${req.sender_username}</small></span>
        <div class="request-actions">
          <button class="btn-accept" data-id="${req.id}">✓</button>
          <button class="btn-reject" data-id="${req.id}">✗</button>
        </div>`;
      el.querySelector('.btn-accept').addEventListener('click', () => acceptRequest(req.id));
      el.querySelector('.btn-reject').addEventListener('click', () => rejectRequest(req.id));
      panel.appendChild(el);
    });
  } catch {}
}

async function acceptRequest(requestId) {
  await apiFetch(`/friends/requests/${requestId}/accept`, { method: 'POST' });
  loadFriends();
  loadRequests();
}

async function rejectRequest(requestId) {
  await apiFetch(`/friends/requests/${requestId}/reject`, { method: 'POST' });
  loadRequests();
}

// ── Nút + (thêm bạn) ─────────────────────────────────────

document.getElementById('add-friend-btn').addEventListener('click', () => {
  const panel = document.getElementById('add-friend-panel');
  const isOpen = panel.style.display !== 'none';
  panel.style.display = isOpen ? 'none' : 'block';
  if (!isOpen) {
    document.getElementById('search-user-input').focus();
    loadRequests();
  }
});

document.getElementById('search-user-btn').addEventListener('click', searchUsers);
document.getElementById('search-user-input').addEventListener('keydown', e => {
  if (e.key === 'Enter') searchUsers();
});

async function searchUsers() {
  const q = document.getElementById('search-user-input').value.trim();
  const resultsEl = document.getElementById('search-user-results');
  if (!q) { resultsEl.innerHTML = ''; return; }

  resultsEl.innerHTML = '<p class="friends-empty">Đang tìm...</p>';
  try {
    const res = await apiFetch(`/users/search?q=${encodeURIComponent(q)}`);
    resultsEl.innerHTML = '';
    if (res.data.length === 0) {
      resultsEl.innerHTML = '<p class="friends-empty">Không tìm thấy người dùng nào.</p>';
      return;
    }
    res.data.forEach(u => resultsEl.appendChild(renderSearchResult(u)));
  } catch {
    resultsEl.innerHTML = '<p class="friends-empty">Lỗi tìm kiếm.</p>';
  }
}

function renderSearchResult(user) {
  const name = user.display_name || user.username;
  const el = document.createElement('div');
  el.className = 'search-result-item';

  const avatarHtml = user.avatar_url
    ? `<img src="${user.avatar_url}" class="friend-avatar" alt="${name}" />`
    : `<div class="friend-avatar friend-avatar-placeholder">${name[0].toUpperCase()}</div>`;

  el.innerHTML = `
    ${avatarHtml}
    <div class="search-result-info">
      <span class="search-result-name">${name}</span>
      <span class="search-result-username">@${user.username}</span>
    </div>
    <button type="button" class="btn-send-request">...</button>
  `;

  updateRequestBtn(el.querySelector('.btn-send-request'), user.id);
  return el;
}

async function updateRequestBtn(btn, userId) {
  try {
    const res = await apiFetch(`/friends/${userId}/status`);
    const { status, request_id } = res.data;
    if (status === 'accepted') {
      btn.textContent = 'Bạn bè ✓';
      btn.disabled = true;
    } else if (status === 'sent') {
      btn.textContent = 'Đã gửi';
      btn.disabled = true;
    } else if (status === 'received') {
      btn.textContent = 'Chấp nhận';
      btn.onclick = async () => {
        await apiFetch(`/friends/requests/${request_id}/accept`, { method: 'POST' });
        btn.textContent = 'Bạn bè ✓';
        btn.disabled = true;
        loadFriends();
        loadRequests();
      };
    } else {
      btn.textContent = 'Kết bạn';
      btn.onclick = async () => {
        try {
          await apiFetch(`/friends/request/${userId}`, { method: 'POST' });
          btn.textContent = 'Đã gửi';
          btn.disabled = true;
          btn.onclick = null;
        } catch (e) { alert(e.message); }
      };
    }
  } catch {
    btn.style.display = 'none';
  }
}

// ── Nút 🔍 (lọc bạn bè) ─────────────────────────────────

document.getElementById('search-friends-btn').addEventListener('click', () => {
  const input = document.getElementById('filter-friends-input');
  const isHidden = input.style.display === 'none';
  input.style.display = isHidden ? 'block' : 'none';
  if (isHidden) input.focus();
  else { input.value = ''; filterFriends(''); }
});

document.getElementById('filter-friends-input').addEventListener('input', e => {
  filterFriends(e.target.value.trim().toLowerCase());
});

function filterFriends(query) {
  const items = document.querySelectorAll('#friends-list .friend-item');
  items.forEach(item => {
    const name = (item.title || '').toLowerCase();
    item.style.display = (!query || name.includes(query)) ? '' : 'none';
  });
}

// ── Cửa sổ chat ──────────────────────────────────────────

function openChat(friend) {
  activeChatUserId = friend.id;
  activeChatFriend = friend;
  lastMessageId = 0;
  clearInterval(pollInterval);

  const name = friend.display_name || friend.username;
  const win = document.getElementById('chat-window');
  document.getElementById('chat-friend-name').textContent = name;

  const avatarEl = document.getElementById('chat-friend-avatar');
  avatarEl.innerHTML = '';
  avatarEl.appendChild(makeChatAvatar(friend));

  win.style.display = 'flex';

  loadMessages(friend.id);
  pollInterval = setInterval(() => pollMessages(friend.id), 3000);
}

document.getElementById('chat-close').addEventListener('click', () => {
  document.getElementById('chat-window').style.display = 'none';
  clearInterval(pollInterval);
  activeChatUserId = null;
});

document.getElementById('chat-form').addEventListener('submit', async e => {
  e.preventDefault();
  const input = document.getElementById('chat-input');
  const content = input.value.trim();
  if (!content || !activeChatUserId) return;
  input.value = '';
  try {
    const res = await apiFetch(`/messages/${activeChatUserId}`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    });
    appendMessage(res.data, true);
    lastMessageId = Math.max(lastMessageId, res.data.id);
  } catch {}
});

async function loadMessages(userId) {
  const box = document.getElementById('chat-messages');
  box.innerHTML = '<p class="friends-empty">Đang tải...</p>';
  try {
    const res = await apiFetch(`/messages/${userId}`);
    box.innerHTML = '';
    res.data.forEach(m => appendMessage(m, m.sender_id === currentUserId));
    if (res.data.length > 0) {
      lastMessageId = Math.max(...res.data.map(m => m.id));
    }
    box.scrollTop = box.scrollHeight;
  } catch {
    box.innerHTML = '<p class="friends-empty">Không thể tải tin nhắn.</p>';
  }
}

async function pollMessages(userId) {
  if (!activeChatUserId) return;
  try {
    const res = await apiFetch(`/messages/${userId}?after_id=${lastMessageId}`);
    if (res.data.length > 0) {
      const box = document.getElementById('chat-messages');
      res.data.forEach(m => appendMessage(m, m.sender_id === currentUserId));
      lastMessageId = Math.max(...res.data.map(m => m.id));
      box.scrollTop = box.scrollHeight;
    }
  } catch {}
}

function makeChatAvatar(data) {
  const name = data ? (data.display_name || data.username || '') : '';
  if (data && data.avatar_url) {
    const img = document.createElement('img');
    img.src = data.avatar_url;
    img.className = 'chat-avatar';
    img.alt = name;
    return img;
  }
  const el = document.createElement('div');
  el.className = 'chat-avatar chat-avatar-placeholder';
  el.textContent = (name || '?')[0].toUpperCase();
  return el;
}

function appendMessage(msg, isMine) {
  const box = document.getElementById('chat-messages');
  const row = document.createElement('div');
  row.className = `chat-msg-row ${isMine ? 'mine' : 'theirs'}`;

  const avatarData = isMine ? currentUserData : activeChatFriend;
  row.appendChild(makeChatAvatar(avatarData));

  const bubble = document.createElement('div');
  bubble.className = `chat-bubble ${isMine ? 'mine' : 'theirs'}`;
  bubble.textContent = msg.content;
  row.appendChild(bubble);

  box.appendChild(row);
}
