import { useRef, useState } from 'react'

export default function VideoUpload({ file, onFileSelect }) {
  const inputRef = useRef(null)
  const [dragover, setDragover] = useState(false)

  const handleDrop = (e) => {
    e.preventDefault()
    setDragover(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped && dropped.type.startsWith('video/')) onFileSelect(dropped)
  }

  const handleChange = (e) => {
    const selected = e.target.files[0]
    if (selected) onFileSelect(selected)
  }

  const formatSize = (bytes) => {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <div
      className={`upload-zone ${dragover ? 'dragover' : ''}`}
      onDragOver={(e) => { e.preventDefault(); setDragover(true) }}
      onDragLeave={() => setDragover(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
    >
      <input ref={inputRef} type="file" accept="video/*" style={{ display: 'none' }} onChange={handleChange} />
      <span className="upload-zone__icon">🎬</span>
      {!file ? (
        <>
          <div className="upload-zone__text">Drop your cricket video here or click to browse</div>
          <div className="upload-zone__hint">Supports MP4, AVI, MOV • Max 500MB</div>
        </>
      ) : (
        <div className="upload-zone__file">
          🎥 {file.name} ({formatSize(file.size)})
        </div>
      )}
    </div>
  )
}
