type TokenIdentity = {
  u?: string
  admin?: boolean
}

function getIdentityFromToken(): TokenIdentity {
  const token = sessionStorage.getItem('bot_token')
  if (!token) {
    return {}
  }
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      window
        .atob(base64)
        .split('')
        .map((c) => `%${(`00${c.charCodeAt(0).toString(16)}`).slice(-2)}`)
        .join('')
    )
    return JSON.parse(jsonPayload).identity || {}
  } catch {
    return {}
  }
}

export function getUsernameFromToken(): string {
  const token = sessionStorage.getItem('bot_token')
  if (!token) {
    return 'admin'
  }
  const identity = getIdentityFromToken()
  return identity.u || 'admin'
}

export function isAdminUser(): boolean {
  const identity = getIdentityFromToken()
  if (typeof identity.admin === 'boolean') {
    return identity.admin
  }
  return getUsernameFromToken() === 'admin'
}
