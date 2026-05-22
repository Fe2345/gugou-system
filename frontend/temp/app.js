const STORAGE_KEY = "courseUserAccounts";

const views = document.querySelectorAll(".view");
const tabs = document.querySelectorAll(".tab");
const messageBox = document.querySelector("#message");

const text = {
  required: (label) => `请填写${label}`,
  phoneInvalid: "请输入有效的 11 位手机号",
  passwordShort: "密码至少需要 6 位",
  passwordMismatch: "两次输入的密码不一致",
  needAgreement: "请先同意用户协议",
  accountMissing: "该账号未注册，请先注册",
  accountExists: "该手机号已注册，请直接登录",
  passwordWrong: "密码错误，请重新输入",
  loginOk: "登录成功",
  registerOk: "注册成功，请登录",
  phoneMissing: "未找到该手机号，请先注册",
  resetOk: "密码修改成功，请使用新密码登录",
  accountLabel: "手机号或账号",
  passwordLabel: "密码",
};

function getUsers() {
  return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
}

function saveUsers(users) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(users));
}

function showMessage(message, type = "success") {
  messageBox.textContent = message;
  messageBox.className = `message ${type === "error" ? "error" : ""}`.trim();
  messageBox.hidden = false;
}

function clearMessage() {
  messageBox.hidden = true;
  messageBox.textContent = "";
}

function routeTo(route) {
  clearMessage();
  views.forEach((view) => view.classList.toggle("active", view.id === route));
  tabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.route === route));
}

function isPhone(value) {
  return /^1[3-9]\d{9}$/.test(value);
}

function requireValue(value, label) {
  if (!value.trim()) {
    showMessage(text.required(label), "error");
    return false;
  }
  return true;
}

function findUserByAccount(account) {
  return getUsers().find((user) => user.phone === account || user.account === account);
}

document.querySelectorAll("[data-route]").forEach((button) => {
  button.addEventListener("click", () => routeTo(button.dataset.route));
});

document.querySelector("#loginForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(event.currentTarget));
  const account = data.account.trim();

  if (!requireValue(account, text.accountLabel)) return;
  if (!requireValue(data.password, text.passwordLabel)) return;

  const user = findUserByAccount(account);
  if (!user) {
    routeTo("register");
    showMessage(text.accountMissing, "error");
    return;
  }

  if (user.password !== data.password) {
    showMessage(text.passwordWrong, "error");
    return;
  }

  event.currentTarget.reset();
  showMessage(text.loginOk);
});

document.querySelector("#registerForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(event.currentTarget));
  const phone = data.phone.trim();

  if (!isPhone(phone)) {
    showMessage(text.phoneInvalid, "error");
    return;
  }
  if (data.password.length < 6) {
    showMessage(text.passwordShort, "error");
    return;
  }
  if (data.password !== data.confirmPassword) {
    showMessage(text.passwordMismatch, "error");
    return;
  }
  if (data.agreement !== "on") {
    showMessage(text.needAgreement, "error");
    return;
  }

  const users = getUsers();
  if (users.some((user) => user.phone === phone)) {
    routeTo("login");
    showMessage(text.accountExists, "error");
    return;
  }

  saveUsers([
    ...users,
    {
      phone,
      account: phone,
      password: data.password,
      createdAt: new Date().toISOString(),
    },
  ]);

  event.currentTarget.reset();
  routeTo("login");
  showMessage(text.registerOk);
});

document.querySelector("#forgotForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(event.currentTarget));
  const phone = data.phone.trim();

  if (!isPhone(phone)) {
    showMessage(text.phoneInvalid, "error");
    return;
  }
  if (data.password.length < 6) {
    showMessage(text.passwordShort, "error");
    return;
  }

  const users = getUsers();
  const userIndex = users.findIndex((user) => user.phone === phone);
  if (userIndex === -1) {
    routeTo("register");
    showMessage(text.phoneMissing, "error");
    return;
  }

  users[userIndex].password = data.password;
  saveUsers(users);
  event.currentTarget.reset();
  routeTo("login");
  showMessage(text.resetOk);
});

routeTo("login");
