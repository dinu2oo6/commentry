const STEPS = [
  { key: 'uploaded',              icon: '📤', label: 'Video uploaded' },
  { key: 'extracting_frames',     icon: '🎞️', label: 'Extracting frames' },
  { key: 'detecting_events',      icon: '🔍', label: 'Detecting cricket events' },
  { key: 'generating_commentary', icon: '🎙️', label: 'Generating commentary' },
  { key: 'generating_audio',      icon: '🔊', label: 'Generating audio' },
  { key: 'composing_video',       icon: '🎬', label: 'Composing final video' },
  { key: 'done',                  icon: '✅', label: 'Complete!' },
]

export default function ProcessingStatus({ step, progress, status }) {
  const currentIdx = STEPS.findIndex(s => s.key === step)

  return (
    <div className="card" style={{ marginTop: 24 }}>
      <div className="card__title">
        <span className="card__title-icon">⚡</span>
        {status === 'uploading' ? 'Uploading video…' : 'Processing Pipeline'}
      </div>
      <div className="processing">
        <div className="processing__steps">
          {STEPS.map((s, i) => {
            const isCompleted = i < currentIdx
            const isActive = i === currentIdx
            return (
              <div key={s.key} className={`step-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}>
                <span className="step-item__icon">
                  {isCompleted ? '✅' : isActive ? <span className="spinner" /> : s.icon}
                </span>
                <span className="step-item__label">{s.label}</span>
                <span className="step-item__status">
                  {isCompleted ? 'Done' : isActive ? 'In progress…' : ''}
                </span>
              </div>
            )
          })}
        </div>
        <div className="progress-bar">
          <div className="progress-bar__fill" style={{ width: `${progress}%` }} />
        </div>
      </div>
    </div>
  )
}
