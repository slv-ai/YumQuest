// Everything that talks to the backend lives in this one file,
// so the components never call fetch() themselves.

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(path, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    })
  } catch {
    // fetch() only throws when the request could not be made at all (no network, server off)
    throw new Error('Cannot reach the server. Is the backend running?')
  }

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    // Our backend sends errors as { "detail": "a message for humans" }
    if (typeof data?.detail === 'string') throw new Error(data.detail)
    if (response.status >= 500) throw new Error('The server is not responding. Is the backend running?')
    throw new Error('The request was not valid.')
  }
  return data
}

export const askQuestion = (question) =>
  request('/api/ask', { method: 'POST', body: JSON.stringify({ question }) })

export const sendFeedback = (conversationId, value) =>
  request('/api/feedback', {
    method: 'POST',
    body: JSON.stringify({ conversation_id: conversationId, value }),
  })

export const getHistory = () => request('/api/history?limit=10')

export const getHealth = () => request('/api/health')
