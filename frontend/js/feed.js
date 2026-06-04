import { apiFetch } from './api.js';
import { init as initFriends } from './friends.js';

const feedEl = document.getElementById('feed');
const postForm = document.getElementById('post-form');
const usernameEl = document.getElementById('current-username');

let currentUserId = null;

function timeAgo(dateStr) {
  const diff = Math.floor((Date.now() - new Date(dateStr)) / 1000);
  if (diff < 60) return `${diff} giây trước`;
  if (diff < 3600) return `${Math.floor(diff / 60)} phút trước`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} giờ trước`;
  return `${Math.floor(diff / 86400)} ngày trước`;
}

function avatarHtml(url, name) {
  if (url) return `<img src="${url}" class="post-avatar" alt="avatar" />`;
  return `<div class="post-avatar post-avatar-placeholder">${(name || '?')[0].toUpperCase()}</div>`;
}

function renderPost(post) {
  const card = document.createElement('div');
  card.className = 'post-card';
  card.dataset.id = post.id;

  const displayName = post.display_name || post.username;

  card.innerHTML = `
    <div class="post-header">
      <div class="post-author-row">
        ${avatarHtml(post.avatar_url, displayName)}
        <div>
          <a href="profile.html?u=${post.username}" class="post-author">${escapeHtml(displayName)}</a>
          <span class="post-author-username">@${post.username}</span>
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
  card.querySelector('.comment-form').addEventListener('submit', (e) => submitComment(e, post.id));

  return card;
}

function escapeHtml(text) {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

async function toggleLike(postId, card) {
  try {
    const res = await apiFetch(`/posts/${postId}/like`, { method: 'POST' });
    const countEl = card.querySelector('.like-count');
    countEl.textContent = res.data.total_likes;
    const btn = card.querySelector('.btn-like');
    btn.classList.toggle('liked', res.data.liked);
  } catch (e) {
    console.error('Like failed', e);
  }
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
    res.data.forEach((c) => {
      const el = document.createElement('div');
      el.className = 'comment-item';
      el.innerHTML = `<strong>@${c.username}</strong> ${escapeHtml(c.content)}`;
      listEl.appendChild(el);
    });
  } catch (e) {
    listEl.innerHTML = '<p class="empty-text">Không thể tải bình luận.</p>';
  }
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
  } catch (e) {
    console.error('Comment failed', e);
  }
}

async function loadFeed() {
  feedEl.innerHTML = '<p class="loading-text">Đang tải bảng tin...</p>';
  try {
    const res = await apiFetch('/feed');
    feedEl.innerHTML = '';
    if (res.data.length === 0) {
      feedEl.innerHTML = '<p class="empty-text">Bảng tin trống. Hãy follow ai đó để xem bài đăng của họ!</p>';
      return;
    }
    res.data.forEach((post) => feedEl.appendChild(renderPost(post)));
  } catch (e) {
    feedEl.innerHTML = '<p class="empty-text">Không thể tải bảng tin.</p>';
  }
}

async function init() {
  let me;
  try {
    me = await apiFetch('/auth/me');
    currentUserId = me.data.id;
    if (usernameEl) {
      usernameEl.textContent = me.data.display_name || `@${me.data.username}`;
      usernameEl.href = `profile.html?u=${me.data.username}`;
    }
  } catch {
    window.location.href = 'index.html';
    return;
  }
  initFriends(currentUserId, me.data);
  await loadFeed();
}

const textarea = postForm.querySelector('textarea');
const charCount = postForm.querySelector('.char-count');
textarea.addEventListener('input', () => {
  charCount.textContent = `${textarea.value.length} / 500`;
});

postForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const textarea = postForm.querySelector('textarea');
  const content = textarea.value.trim();
  if (!content) return;

  const btn = postForm.querySelector('button[type="submit"]');
  btn.disabled = true;
  try {
    await apiFetch('/posts', {
      method: 'POST',
      body: JSON.stringify({ content }),
    });
    textarea.value = '';
    charCount.textContent = '0 / 500';
    await loadFeed();
  } catch (err) {
    alert(err.message || 'Đăng bài thất bại');
  } finally {
    btn.disabled = false;
  }
});

document.getElementById('logout-btn').addEventListener('click', () => {
  localStorage.removeItem('token');
  window.location.href = 'index.html';
});

const token = localStorage.getItem('token');
if (!token) {
  window.location.href = 'index.html';
} else {
  init();
}
