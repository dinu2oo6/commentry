const EVENT_LABEL = {
  DOT: 'Dot', SINGLE: '1 Run', DOUBLE: '2 Runs', TRIPLE: '3 Runs',
  FOUR: 'Four!', SIX: 'Six!!', WICKET: 'Wicket!', WIDE: 'Wide', NO_BALL: 'No Ball',
}

export default function CommentaryTimeline({ events }) {
  if (!events || events.length === 0) {
    return (
      <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', padding: '8px 0' }}>
        No events detected.
      </p>
    )
  }

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60)
    const s = Math.floor(seconds % 60)
    return `${m}:${String(s).padStart(2, '0')}`
  }

  return (
    <div className="timeline">
      {events.map((ev, i) => (
        <div className="timeline-item" key={i}>
          <div className="timeline-item__left">
            <span className="timeline-item__time">{formatTime(ev.timestamp || 0)}</span>
            <span className="timeline-item__index">#{i + 1}</span>
          </div>

          <div className="timeline-item__content">
            <div className="timeline-item__top">
              <span className={`badge badge-${ev.event}`}>
                {EVENT_LABEL[ev.event] || ev.event}
              </span>
              {ev.shot && (
                <span className="timeline-item__shot">
                  {ev.shot.replace(/_/g, ' ')}
                </span>
              )}
            </div>

            <div className="timeline-item__commentary">{ev.commentary}</div>

            <div className="timeline-item__meta">
              {ev.score && (
                <span className="meta-chip">
                  <span style={{ opacity: 0.5 }}>SCR</span> {ev.score}
                </span>
              )}
              {ev.overs && (
                <span className="meta-chip">
                  <span style={{ opacity: 0.5 }}>OV</span> {ev.overs}
                </span>
              )}
              {ev.run_rate > 0 && (
                <span className="meta-chip">
                  <span style={{ opacity: 0.5 }}>RR</span> {ev.run_rate}
                </span>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
