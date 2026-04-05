import { useRef, useState } from 'react'

export default function AudioPlayer({ filename, provider }) {
  const audioRef = useRef(null)
  const [playing, setPlaying] = useState(false)

  const audioUrl = `/api/audio/${filename}`

  const togglePlay = () => {
    if (!audioRef.current) return
    if (playing) { audioRef.current.pause() }
    else { audioRef.current.play() }
    setPlaying(!playing)
  }

  return (
    <div className="audio-player">
      <audio ref={audioRef} src={audioUrl} onEnded={() => setPlaying(false)} />
      <button className="audio-player__btn" onClick={togglePlay}>
        {playing ? '⏸' : '▶'}
      </button>
      <div className="audio-player__info">
        <div className="audio-player__title">Generated Commentary</div>
        <div className="audio-player__sub">Provider: {provider || 'gTTS'}</div>
      </div>
      {playing && (
        <div className="audio-player__wave">
          <span /><span /><span /><span /><span />
        </div>
      )}
      <a className="audio-player__download" href={audioUrl} download={filename}>⬇ Download</a>
    </div>
  )
}
