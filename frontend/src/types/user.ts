export interface UserInfo {
  id: string
  phone: string
  nickname: string
  avatar: string
  role: 'user' | 'admin'
  createdAt: string
  creditScore: number
  status: 'normal' | 'frozen' | 'disabled' | 'deleted'
  bio: string
  contact: string
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
  access: string
  refresh: string
  user: UserInfo
}
