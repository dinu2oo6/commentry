const STEPS = [
  { key: 'uploaded',              icon: '📤', label: 'Video uploaded' },
  { key: 'extracting_frames',     icon: '🎞', label: 'Extracting frames' },
  { key: 'detecting_events',      icon: '🔍', label: 'Detecting cricket events' },
  { key: 'generating_commentary', icon: '🎙', label: 'Generating AI commentary' },
  { key: 'generating_audio',      icon: '🔊', label: 'Synthesising neural audio' },
  { key: 'composing_video',       icon: '🎬', label: 'Composing final video' },
  { key: 'done',                  icon: '✅', label: 'Complete' },
]

export default function ProcessingStatus({ step, progress, status }) {
  const currentIdx = STEPS.findIndex(s => s.key === step)

  return (
    <div className="card" style={{ marginTop: 28 }}>
      <div className="card__title" style={{ marginBottom: 0 }}>
        <span className="card__title-icon">⚡</span>
        {status === 'uploading' ? 'Uploading video…' : 'Processing Pipeline'}
      </div>

      <div className="processing">
        <div className="processing__header">
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            {STEPS[Math.max(0, currentIdx)]?.label || 'Starting…'}
          </span>
          <span className="processing__pct">{progress}%</span>
        </div>

        <div className="processing__steps">
          {STEPS.map((s, i) => {
            const isCompleted = i < currentIdx
            const isActive    = i === currentIdx
            return (
              <div
                key={s.key}
                className={`step-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
              >
                <div className="step-item__dot" />
                <span className="step-item__icon">
                  {isCompleted ? '✓' : s.icon}
                </span>
                <span className="step-item__label">{s.label}</span>
                <span className="step-item__status">
                  {isCompleted ? 'done' : isActive ? <span className="spinner" /> : ''}
                </span>
              </div>
            )
          })}
        </div>

        <div className="progress-track">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
      </div>
    </div>
  )
}
