import { useRef, useState, useEffect } from 'react'

export default function AudioPlayer({ filename, provider }) {
  const audioRef  = useRef(null)
  const [playing,   setPlaying]   = useState(false)
  const [current,   setCurrent]   = useState(0)
  const [duration,  setDuration]  = useState(0)

  const audioUrl = `/api/audio/${filename}`

  useEffect(() => {
    const el = audioRef.current
    if (!el) return
    const onTimeUpdate = () => setCurrent(el.currentTime)
    const onDuration   = () => setDuration(el.duration || 0)
    const onEnded      = () => { setPlaying(false); setCurrent(0) }
    el.addEventListener('timeupdate', onTimeUpdate)
    el.addEventListener('loadedmetadata', onDuration)
    el.addEventListener('ended', onEnded)
    return () => {
      el.removeEventListener('timeupdate', onTimeUpdate)
      el.removeEventListener('loadedmetadata', onDuration)
      el.removeEventListener('ended', onEnded)
    }
  }, [])

  const togglePlay = () => {
    if (!audioRef.current) return
    if (playing) { audioRef.current.pause() }
    else          { audioRef.current.play() }
    setPlaying(!playing)
  }

  const handleSeek = (e) => {
    if (!audioRef.current || !duration) return
    const rect  = e.currentTarget.getBoundingClientRect()
    const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width))
    audioRef.current.currentTime = ratio * duration
    setCurrent(ratio * duration)
  }

  const fmt = (s) => {
    const m = Math.floor(s / 60)
    const sec = Math.floor(s % 60)
    return `${m}:${String(sec).padStart(2, '0')}`
  }

  const pct = duration > 0 ? (current / duration) * 100 : 0

  return (
    <div className="audio-player">
      <audio ref={audioRef} src={audioUrl} preload="metadata" />

      <div className="audio-player__top">
        <button className="audio-player__btn" onClick={togglePlay} aria-label={playing ? 'Pause' : 'Play'}>
          {playing ? '⏸' : '▶'}
        </button>

        <div className="audio-player__info">
          <div className="audio-player__title">Generated Commentary Audio</div>
          <div className="audio-player__sub">{provider || 'Neural TTS'} · {filename}</div>
        </div>

        {playing && (
          <div className="audio-player__wave">
            <span /><span /><span /><span /><span /><span />
          </div>
        )}

        <span className="audio-player__time">
          {fmt(current)} / {fmt(duration)}
        </span>
      </div>

      {/* Progress bar */}
      <div className="audio-player__progress-row">
        <div
          style={{
            flex: 1, height: 4, background: 'var(--bg-raised)',
            borderRadius: 4, cursor: 'pointer', position: 'relative',
          }}
          onClick={handleSeek}
        >
          <div
            className="audio-player__progress-fill"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      <div className="audio-player__actions">
        <a className="audio-player__download" href={audioUrl} download={filename}>
          Download Audio
        </a>
      </div>
    </div>
  )
}
