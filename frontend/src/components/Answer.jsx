import ReactMarkdown from 'react-markdown'

// Shows one answer: the text, the closest recipes, cost/speed details, and the 👍/👎 buttons.
export default function Answer({ result, rating, onRate }) {
  const { id, answer, sources, no_match, model, prompt_tokens, completion_tokens, cost, seconds, warning } = result

  return (
    <section className="card" aria-live="polite">
      {warning && <div className="banner warn">{warning}</div>}

      {/* LLMs write markdown (**bold**, numbered lists), so we render it instead of showing the symbols */}
      <div className="answer">
        <ReactMarkdown>{answer}</ReactMarkdown>
      </div>

      {sources.length > 0 && (
        <>
          <h2>Closest matching recipes</h2>
          <ul className="sources">
            {sources.map((s) => (
              <li key={s.id}>
                {s.title} <span className="muted">distance {s.distance.toFixed(2)}</span>
              </li>
            ))}
          </ul>
        </>
      )}

      {!no_match && (
        <p className="meta">
          {model} · {prompt_tokens}+{completion_tokens} tokens ·{' '}
          {cost === null ? 'cost unknown' : `$${cost.toFixed(5)}`} · {seconds.toFixed(1)}s
        </p>
      )}

      {id && !no_match && (
        <div className="rating">
          <span>Was this helpful?</span>
          <button type="button" aria-label="Helpful" aria-pressed={rating === 1} onClick={() => onRate(1)}>
            👍
          </button>
          <button type="button" aria-label="Not helpful" aria-pressed={rating === -1} onClick={() => onRate(-1)}>
            👎
          </button>
        </div>
      )}
    </section>
  )
}
