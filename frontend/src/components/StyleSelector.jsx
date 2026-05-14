const STYLES = [
  { id: 'professional', icon: '🎤', name: 'Professional', desc: 'Harsha Bhogle style — measured and eloquent' },
  { id: 'hype',         icon: '🔥', name: 'Hype',         desc: 'IPL energy — maximum excitement' },
  { id: 'funny',        icon: '😄', name: 'Funny',        desc: 'Casual banter with pop culture refs' },
  { id: 'analytical',   icon: '📊', name: 'Analytical',   desc: 'Stats, technique, and patterns' },
]

export default function StyleSelector({ style, onStyleChange }) {
  return (
    <div className="style-grid">
      {STYLES.map(s => (
        <div
          key={s.id}
          className={`style-card ${style === s.id ? 'active' : ''}`}
          onClick={() => onStyleChange(s.id)}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && onStyleChange(s.id)}
        >
          <div className="style-card__icon">{s.icon}</div>
          <div className="style-card__name">{s.name}</div>
          <div className="style-card__desc">{s.desc}</div>
        </div>
      ))}
    </div>
  )
}
