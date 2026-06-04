import { apiFetch } from './api.js';

const params = new URLSearchParams(location.search);
const username = params.get('u');

const token = localStorage.getItem('token');
if (!token) { window.location.href = 'index.html'; }

document.getElementById('logout-btn').addEventListener('click', () => {
  localStorage.removeItem('token');
  window.location.href = 'index.html';
});

let currentUserId = null;
let currentUsername = null;
let isOwnProfile = false;
let profileUser = null;

function timeAgo(dateStr) {
  const diff = Math.floor((Date.now() - new Date(dateStr)) / 1000);
  if (diff < 60) return `${diff} giây trước`;
  if (diff < 3600) return `${Math.floor(diff / 60)} phút trước`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} giờ trước`;
  return `${Math.floor(diff / 86400)} ngày trước`;
}

function escapeHtml(text) {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function renderAvatar(url, name) {
  const img = document.getElementById('profile-avatar');
  const old = document.getElementById('avatar-placeholder');
  if (old) old.remove();

  if (url) {
    img.src = url;
    img.style.display = 'block';
  } else {
    img.style.display = 'none';
    img.insertAdjacentHTML('afterend',
      `<div class="avatar-placeholder" id="avatar-placeholder">${(name || '?')[0].toUpperCase()}</div>`);
  }
}

function renderProfile(p) {
  profileUser = p;
  document.title = `${p.display_name || p.username} - Mini Social`;
  document.getElementById('profile-display-name').textContent = p.display_name || p.username;
  document.getElementById('profile-username-tag').textContent = `@${p.username}`;
  document.getElementById('profile-followers').textContent = p.followers;
  document.getElementById('profile-following').textContent = p.following;
  renderAvatar(p.avatar_url, p.display_name || p.username);

  const actionsEl = document.getElementById('profile-actions');
  actionsEl.innerHTML = '';

  if (isOwnProfile) {
    actionsEl.innerHTML = `<button type="button" id="edit-btn">Chỉnh sửa hồ sơ</button>`;
    document.getElementById('upload-avatar-btn').style.display = 'inline-block';
    document.getElementById('edit-btn').addEventListener('click', openEditPanel);

    const displayNameEl = document.getElementById('profile-display-name');
    if (!displayNameEl.querySelector('.btn-edit-username')) {
      const pencil = document.createElement('button');
      pencil.type = 'button';
      pencil.className = 'btn-edit-username';
      pencil.title = 'Đổi tên hiển thị';
      pencil.textContent = '✏️';
      pencil.addEventListener('click', openEditPanel);
      displayNameEl.appendChild(pencil);
    }
  } else {
    const following = p.is_following;
    actionsEl.innerHTML = `
      <button type="button" id="follow-btn" class="${following ? 'btn-following' : ''}">
        ${following ? 'Đang theo dõi' : 'Theo dõi'}
      </button>
      <button type="button" id="friend-btn" data-user-id="${p.id}">...</button>`;
    document.getElementById('follow-btn').addEventListener('click', () => toggleFollow(p.id, p.username));
    loadFriendStatus(p.id);
  }
}

async function loadFriendStatus(userId) {
  const btn = document.getElementById('friend-btn');
  if (!btn) return;
  try {
    const res = await apiFetch(`/friends/${userId}/status`);
    const { status, request_id } = res.data;
    if (status === 'accepted') {
      btn.textContent = 'Bạn bè';
      btn.className = 'btn-following';
      btn.onclick = () => removeFriend(userId);
    } else if (status === 'sent') {
      btn.textContent = 'Đã gửi lời mời';
      btn.disabled = true;
    } else if (status === 'received') {
      btn.textContent = 'Chấp nhận lời mời';
      btn.onclick = () => acceptFriendRequest(request_id, userId);
    } else {
      btn.textContent = 'Kết bạn';
      btn.onclick = () => sendFriendRequest(userId);
    }
  } catch {
    btn.style.display = 'none';
  }
}

async function sendFriendRequest(userId) {
  try {
    await apiFetch(`/friends/request/${userId}`, { method: 'POST' });
    const btn = document.getElementById('friend-btn');
    btn.textContent = 'Đã gửi lời mời';
    btn.disabled = true;
    btn.onclick = null;
  } catch (e) { alert(e.message); }
}

async function acceptFriendRequest(requestId, userId) {
  try {
    await apiFetch(`/friends/requests/${requestId}/accept`, { method: 'POST' });
    loadFriendStatus(userId);
  } catch (e) { alert(e.message); }
}

async function removeFriend(userId) {
  if (!confirm('Xóa bạn bè?')) return;
  try {
    await apiFetch(`/friends/${userId}`, { method: 'DELETE' });
    loadFriendStatus(userId);
  } catch (e) { alert(e.message); }
}

async function toggleFollow(userId, uname) {
  const btn = document.getElementById('follow-btn');
  const isFollowing = btn.classList.contains('btn-following');
  try {
    if (isFollowing) {
      await apiFetch(`/users/${userId}/follow`, { method: 'DELETE' });
    } else {
      await apiFetch(`/users/${userId}/follow`, { method: 'POST' });
    }
    const updated = await apiFetch(`/users/${uname}`);
    renderProfile(updated.data);
  } catch (e) {
    alert(e.message);
  }
}

function openEditPanel() {
  const panel = document.getElementById('edit-panel');
  const input = document.getElementById('edit-display-name');
  const displayNameEl = document.getElementById('profile-display-name');
  // Lấy chỉ text node, bỏ qua nút ✏️
  const nameText = Array.from(displayNameEl.childNodes)
    .filter(n => n.nodeType === Node.TEXT_NODE)
    .map(n => n.textContent)
    .join('').trim();
  input.value = nameText;
  panel.style.display = 'block';
  input.focus();
}

document.getElementById('cancel-edit').addEventListener('click', () => {
  document.getElementById('edit-panel').style.display = 'none';
});


document.getElementById('edit-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const displayName = document.getElementById('edit-display-name').value.trim();
  try {
    const res = await apiFetch('/users/me', {
      method: 'PUT',
      body: JSON.stringify({ display_name: displayName || null }),
    });
    const displayNameEl = document.getElementById('profile-display-name');
    const pencil = displayNameEl.querySelector('.btn-edit-username');
    displayNameEl.textContent = res.data.display_name || res.data.username;
    if (pencil) displayNameEl.appendChild(pencil);
    document.getElementById('edit-panel').style.display = 'none';
  } catch (e) {
    alert(e.message);
  }
});

// Avatar upload
document.getElementById('upload-avatar-btn').addEventListener('click', () => {
  document.getElementById('avatar-input').click();
});

document.getElementById('avatar-input').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const form = new FormData();
  form.append('file', file);
  try {
    const res = await fetch('/users/me/avatar', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: form,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || 'Upload thất bại');
    const img = document.getElementById('profile-avatar');
    const placeholder = document.getElementById('avatar-placeholder');
    if (placeholder) placeholder.remove();
    img.src = data.data.avatar_url + '?t=' + Date.now();
    img.style.display = 'block';
  } catch (err) {
    alert(err.message);
  }
});

function renderPosts(posts) {
  const el = document.getElementById('user-posts');
  el.innerHTML = '';
  if (posts.length === 0) {
    el.innerHTML = '<p class="empty-text">Chưa có bài đăng nào.</p>';
    return;
  }
  posts.forEach(p => el.appendChild(renderPostCard(p)));
}

function renderPostCard(post) {
  const card = document.createElement('div');
  card.className = 'post-card';
  card.dataset.id = post.id;

  const name = profileUser ? (profileUser.display_name || profileUser.username) : '';
  const avatarHtml = profileUser && profileUser.avatar_url
    ? `<img src="${profileUser.avatar_url}" class="post-avatar" alt="${name}" />`
    : `<div class="post-avatar post-avatar-placeholder">${(name || '?')[0].toUpperCase()}</div>`;

  card.innerHTML = `
    <div class="post-header">
      <div class="post-author-row">
        ${avatarHtml}
        <div>
          <span class="post-author">${escapeHtml(name)}</span>
          <span class="post-author-username">@${profileUser ? profileUser.username : ''}</span>
        </div>
      </div>
      <span class="post-time">${timeAgo(post.created_at)}</span>
    </div>
    <p class="post-content">${escapeHtml(post.content)}</p>
    <div class="post-actions">
      <button class="btn-like ${post.user_liked ? 'liked' : ''}" data-post-id="${post.id}">
        ♥ <span class="like-count">${post.like_count}</span>
      </button>
      <button class="btn-comments" data-post-id="${post.id}">
        💬 <span class="comment-count">${post.comment_count}</span> bình luận
      </button>
    </div>
    <div class="comment-section" id="comments-${post.id}" style="display:none">
      <div class="comment-list" id="comment-list-${post.id}"></div>
      <form class="comment-form" data-post-id="${post.id}">
        <input type="text" placeholder="Viết bình luận..." required />
        <button type="submit">Gửi</button>
      </form>
    </div>
  `;
  card.querySelector('.btn-like').addEventListener('click', () => toggleLike(post.id, card));
  card.querySelector('.btn-comments').addEventListener('click', () => toggleComments(post.id));
  card.querySelector('.comment-form').addEventListener('submit', e => submitComment(e, post.id));
  return card;
}

async function toggleLike(postId, card) {
  try {
    const res = await apiFetch(`/posts/${postId}/like`, { method: 'POST' });
    card.querySelector('.like-count').textContent = res.data.total_likes;
    card.querySelector('.btn-like').classList.toggle('liked', res.data.liked);
  } catch (e) { console.error(e); }
}

async function toggleComments(postId) {
  const section = document.getElementById(`comments-${postId}`);
  if (section.style.display === 'none') {
    section.style.display = 'block';
    await loadComments(postId);
  } else {
    section.style.display = 'none';
  }
}

async function loadComments(postId) {
  const listEl = document.getElementById(`comment-list-${postId}`);
  listEl.innerHTML = '<p class="loading-text">Đang tải...</p>';
  try {
    const res = await apiFetch(`/posts/${postId}/comments`);
    listEl.innerHTML = '';
    if (res.data.length === 0) {
      listEl.innerHTML = '<p class="empty-text">Chưa có bình luận nào.</p>';
      return;
    }
    res.data.forEach(c => {
      const el = document.createElement('div');
      el.className = 'comment-item';
      el.innerHTML = `<strong>@${c.username}</strong> ${escapeHtml(c.content)}`;
      listEl.appendChild(el);
    });
  } catch { listEl.innerHTML = '<p class="empty-text">Không thể tải bình luận.</p>'; }
}

async function submitComment(e, postId) {
  e.preventDefault();
  const input = e.target.querySelector('input');
  const content = input.value.trim();
  if (!content) return;
  try {
    await apiFetch(`/posts/${postId}/comments`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    });
    input.value = '';
    await loadComments(postId);
    const card = document.querySelector(`[data-id="${postId}"]`);
    const countEl = card.querySelector('.comment-count');
    countEl.textContent = parseInt(countEl.textContent) + 1;
  } catch (e) { console.error(e); }
}

async function init() {
  if (!username) { window.location.href = 'feed.html'; return; }

  try {
    const me = await apiFetch('/auth/me');
    currentUserId = me.data.id;
    currentUsername = me.data.username;
    const headerLink = document.getElementById('current-username');
    headerLink.textContent = me.data.display_name || `@${currentUsername}`;
    headerLink.href = `profile.html?u=${currentUsername}`;
    isOwnProfile = currentUsername === username;
  } catch {
    window.location.href = 'index.html';
    return;
  }

  try {
    const [profileRes, postsRes] = await Promise.all([
      apiFetch(`/users/${username}`),
      apiFetch(`/users/${username}/posts`),
    ]);
    renderProfile(profileRes.data);
    renderPosts(postsRes.data);
  } catch (e) {
    document.getElementById('profile-card').innerHTML =
      `<p class="empty-text">Lỗi: ${e.message}</p>`;
  }
}

init();
