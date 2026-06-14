export type RouteGuardAction =
  | { type: 'next' }
  | { type: 'redirect'; to: string }
  | { type: 'waitAuth' }

interface RouteGuardState {
  toPath: string
  isLoggedIn: boolean
  isAdmin: boolean
  authInitialized: boolean
}

const publicPaths = ['/', '/login', '/admin/login']

export function getRouteGuardAction(state: RouteGuardState): RouteGuardAction {
  const { toPath, isLoggedIn, isAdmin, authInitialized } = state

  if (toPath === '/admin/login') {
    if (isLoggedIn && !authInitialized) {
      return { type: 'waitAuth' }
    }
    if (isLoggedIn && isAdmin) {
      return { type: 'redirect', to: '/admin' }
    }
    return { type: 'next' }
  }

  if (toPath.startsWith('/admin')) {
    if (!isLoggedIn) {
      return { type: 'redirect', to: '/admin/login' }
    }
    if (!authInitialized) {
      return { type: 'waitAuth' }
    }
    if (!isAdmin) {
      return { type: 'redirect', to: '/' }
    }
    return { type: 'next' }
  }

  if (isLoggedIn && !authInitialized) {
    return { type: 'waitAuth' }
  }

  if (isLoggedIn && isAdmin) {
    return { type: 'redirect', to: '/admin' }
  }

  if (publicPaths.includes(toPath)) {
    return { type: 'next' }
  }

  if (!isLoggedIn) {
    return { type: 'redirect', to: '/login' }
  }

  return { type: 'next' }
}
