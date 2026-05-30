import { apiFetch } from './api.js';

const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const toggleButton = document.getElementById('toggle-button');
const toggleText = document.getElementById('toggle-text');
const messageBox = document.getElementById('message');
const loginPanel = document.getElementById('login-panel');
const registerPanel = document.getElementById('register-panel');

let showLogin = true;

function updateFormState() {
  loginPanel.classList.toggle('active', showLogin);
  registerPanel.classList.toggle('active', !showLogin);
  toggleText.innerHTML = showLogin
    ? 'Bạn chưa có tài khoản? <button id="toggle-button" type="button">Đăng ký</button>'
    : 'Bạn đã có tài khoản? <button id="toggle-button" type="button">Đăng nhập</button>';

  const button = document.getElementById('toggle-button');
  button?.addEventListener('click', () => {
    showLogin = !showLogin;
    updateFormState();
  });
}

function showMessage(text, isError = true) {
  messageBox.textContent = text;
  messageBox.style.color = isError ? '#dc2626' : '#16a34a';
}

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

    showMessage('Đăng ký thành công. Vui lòng đăng nhập.', false);
    showLogin = true;
    updateFormState();
  } catch (error) {
    showMessage(error.message || 'Đăng ký thất bại');
  }
});

updateFormState();
