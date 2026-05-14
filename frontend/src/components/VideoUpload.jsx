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
      <input
        ref={inputRef}
        type="file"
        accept="video/*"
        style={{ display: 'none' }}
        onChange={handleChange}
      />

      <div className="upload-zone__icon-wrap">
        <div className="upload-zone__icon-ring" />
        <span className="upload-zone__icon">🎬</span>
      </div>

      {!file ? (
        <>
          <div className="upload-zone__text">Drop your cricket video here</div>
          <div className="upload-zone__hint">or click to browse · MP4, AVI, MOV · Max 500 MB</div>
        </>
      ) : (
        <div className="upload-zone__file">
          <span>🎥</span>
          <span>{file.name}</span>
          <span style={{ opacity: 0.6 }}>({formatSize(file.size)})</span>
        </div>
      )}
    </div>
  )
}
