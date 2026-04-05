const STYLES = [
  { id: 'professional', icon: '🎤', name: 'Professional', desc: 'Harsha Bhogle style' },
  { id: 'hype',         icon: '🔥', name: 'Hype',         desc: 'IPL commentary energy' },
  { id: 'funny',        icon: '😄', name: 'Funny',        desc: 'Casual & humorous' },
  { id: 'analytical',   icon: '📊', name: 'Analytical',   desc: 'Stats & technique' },
]

export default function StyleSelector({ style, onStyleChange }) {
  return (
    <div className="style-grid">
      {STYLES.map(s => (
        <div
          key={s.id}
          className={`style-card ${style === s.id ? 'active' : ''}`}
          onClick={() => onStyleChange(s.id)}
        >
          <div className="style-card__icon">{s.icon}</div>
          <div className="style-card__name">{s.name}</div>
          <div className="style-card__desc">{s.desc}</div>
        </div>
      ))}
    </div>
  )
}
