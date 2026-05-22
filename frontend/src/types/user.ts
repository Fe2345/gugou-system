export interface UserInfo {
  id: string
  phone: string
  nickname: string
  avatar: string
  role: 'user' | 'admin'
  createdAt: string
}

export interface LoginForm {
  account: string
  password: string
}

export interface RegisterForm {
  phone: string
  password: string
  confirmPassword: string
}

export interface LoginResult {
  token: string
  user: UserInfo
}
