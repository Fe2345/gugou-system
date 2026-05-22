export function isPhone(value: string): boolean {
  return /^1[3-9]\d{9}$/.test(value)
}

export function isPassword(value: string): boolean {
  return value.length >= 6
}

export function isEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
}
