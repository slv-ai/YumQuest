import ReactMarkdown from 'react-markdown'

// The list of recent questions. Each one can be opened to read its saved answer.
const RATING = { 1: '👍', '-1': '👎' }

export default function History({ items }) {
  if (items.length === 0) return null

  return (
    <section>
      <h2>Recent questions</h2>
      <ul className="history">
        {items.map((item) => (
          <li key={item.id}>
            {/* <details> is built into HTML: click the summary to open and close it */}
            <details>
              <summary>
                {RATING[item.feedback] ?? '–'} {item.question}
                <span className="muted">
                  {' '}
                  · {item.model ?? 'no model'}
                  {item.cost != null && ` · $${item.cost.toFixed(5)}`}
                </span>
              </summary>
              <div className="answer">
                <ReactMarkdown>{item.answer}</ReactMarkdown>
              </div>
            </details>
          </li>
        ))}
      </ul>
    </section>
  )
}
