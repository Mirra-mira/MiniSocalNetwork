import { apiFetch } from './api.js';

const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const forgotForm = document.getElementById('forgot-form');
const toggleButton = document.getElementById('toggle-button');
const toggleText = document.getElementById('toggle-text');
const forgotButton = document.getElementById('forgot-button');
const backToLogin = document.getElementById('back-to-login');
const messageBox = document.getElementById('message');
const loginPanel = document.getElementById('login-panel');
const registerPanel = document.getElementById('register-panel');
const forgotPanel = document.getElementById('forgot-panel');

// 'login' | 'register' | 'forgot'
let currentPanel = 'login';

function showPanel(panel) {
  currentPanel = panel;
  loginPanel.classList.toggle('active', panel === 'login');
  registerPanel.classList.toggle('active', panel === 'register');
  forgotPanel.classList.toggle('active', panel === 'forgot');
  showMessage('');

  if (panel === 'forgot') {
    toggleText.style.display = 'none';
  } else {
    toggleText.style.display = '';
    const showLogin = panel === 'login';
    toggleText.innerHTML = showLogin
      ? 'Bạn chưa có tài khoản? <button id="toggle-button" type="button">Đăng ký</button>'
      : 'Bạn đã có tài khoản? <button id="toggle-button" type="button">Đăng nhập</button>';
    document.getElementById('toggle-button')?.addEventListener('click', () => {
      showPanel(showLogin ? 'register' : 'login');
    });
  }
}

function showMessage(text, isError = true) {
  messageBox.textContent = text;
  messageBox.style.color = isError ? '#dc2626' : '#16a34a';
}

// Ẩn/hiện mật khẩu — áp dụng cho tất cả .toggle-pw trong trang
document.querySelectorAll('.toggle-pw').forEach((btn) => {
  btn.addEventListener('click', () => {
    const input = btn.previousElementSibling;
    if (input.type === 'password') {
      input.type = 'text';
      btn.textContent = 'Ẩn';
    } else {
      input.type = 'password';
      btn.textContent = 'Hiện';
    }
  });
});

// Đăng nhập
loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  showMessage('');

  const formData = new FormData(loginForm);
  const payload = {
    username: formData.get('username')?.toString().trim(),
    password: formData.get('password')?.toString().trim(),
  };

  try {
    const response = await apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    localStorage.setItem('token', response.data.access_token);
    window.location.href = 'feed.html';
  } catch (error) {
    showMessage(error.message || 'Đăng nhập thất bại');
  }
});

// Đăng ký
registerForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  showMessage('');

  const formData = new FormData(registerForm);
  const payload = {
    username: formData.get('username')?.toString().trim(),
    password: formData.get('password')?.toString().trim(),
  };

  try {
    await apiFetch('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    showPanel('login');
    showMessage('Đăng ký thành công. Vui lòng đăng nhập.', false);
  } catch (error) {
    showMessage(error.message || 'Đăng ký thất bại');
  }
});

// Quên mật khẩu
forgotForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  showMessage('');

  const formData = new FormData(forgotForm);
  const username = formData.get('username')?.toString().trim();
  const newPassword = formData.get('new_password')?.toString().trim();
  const confirmPassword = formData.get('confirm_password')?.toString().trim();

  if (newPassword !== confirmPassword) {
    showMessage('Mật khẩu xác nhận không khớp');
    return;
  }

  try {
    await apiFetch('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({ username, new_password: newPassword }),
    });

    showMessage('Đặt lại mật khẩu thành công. Vui lòng đăng nhập.', false);
    forgotForm.reset();
    showPanel('login');
  } catch (error) {
    showMessage(error.message || 'Đặt lại mật khẩu thất bại');
  }
});

forgotButton.addEventListener('click', () => showPanel('forgot'));
backToLogin.addEventListener('click', () => showPanel('login'));
toggleButton.addEventListener('click', () => showPanel('register'));

showPanel('login');
