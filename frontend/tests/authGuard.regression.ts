import assert from 'node:assert/strict'
import { getRouteGuardAction } from '../src/router/authGuard.js'

const action = getRouteGuardAction({
  toPath: '/admin',
  isLoggedIn: true,
  isAdmin: false,
  authInitialized: false,
})

assert.deepEqual(action, { type: 'waitAuth' })
