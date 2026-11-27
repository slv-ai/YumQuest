import { useEffect, useState } from 'react'
import { askQuestion, getHealth, getHistory, sendFeedback } from './api'
import Answer from './components/Answer'
import History from './components/History'
import './App.css'

const EXAMPLES = [
  'What can I make with chickpeas?',
  'A warming soup',
  'Quick pasta dinner',
  'Something with shrimp',
]

export default function App() {
  // "State" = values React remembers. When one changes, the screen updates.
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null) // the latest answer from the backend
  const [rating, setRating] = useState(null) // 1, -1, or null for the latest answer
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])
  const [serverProblem, setServerProblem] = useState(null)

  const refreshHistory = () =>
    getHistory()
      .then(setHistory)
      .catch(() => {}) // history is a nice extra, so a failure here is not worth an error box

  // Runs once when the page opens: is the backend (and database) reachable?
  useEffect(() => {
    getHealth()
      .then(() => getHistory())
      .then(setHistory)
      .catch((e) => setServerProblem(e.message))
  }, [])

  async function handleSubmit(event) {
    event.preventDefault() // stop the browser from reloading the page
    if (!question.trim() || loading) return
    setLoading(true)
    setError(null)
    setResult(null)
    setRating(null)
    try {
      setResult(await askQuestion(question))
      refreshHistory()
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleRate(value) {
    try {
      await sendFeedback(result.id, value)
      setRating(value)
      refreshHistory()
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <main className="app">
      <h1>YumQuest 🍲</h1>
      <p className="subtitle">Ask about recipes. Answers come only from the recipes in the collection.</p>

      {serverProblem && <div className="banner error">{serverProblem}</div>}

      <form onSubmit={handleSubmit} className="ask-form">
        <label htmlFor="question" className="sr-only">
          Your question
        </label>
        <input
          id="question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. high protein vegetarian dinner with chickpeas"
          maxLength={1000}
          disabled={loading}
          autoFocus
        />
        <button type="submit" disabled={loading || !question.trim()}>
          {loading ? 'Thinking…' : 'Ask'}
        </button>
      </form>

      <div className="examples">
        {EXAMPLES.map((text) => (
          <button key={text} type="button" className="chip" disabled={loading} onClick={() => setQuestion(text)}>
            {text}
          </button>
        ))}
      </div>

      {error && (
        <div className="banner error" role="alert">
          {error}
        </div>
      )}
      {loading && <p className="status">Searching recipes and asking the chef…</p>}
      {result && <Answer result={result} rating={rating} onRate={handleRate} />}

      <History items={history} />
    </main>
  )
}
