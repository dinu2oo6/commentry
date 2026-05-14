import { useState, useCallback } from "react";
import VideoUpload from "./components/VideoUpload";
import StyleSelector from "./components/StyleSelector";
import ProcessingStatus from "./components/ProcessingStatus";
import CommentaryTimeline from "./components/CommentaryTimeline";
import AudioPlayer from "./components/AudioPlayer";

const API = "/api";

export default function App() {
  const [file, setFile] = useState(null);
  const [style, setStyle] = useState("professional");
  const [batsman, setBatsman] = useState("Virat Kohli");
  const [bowler, setBowler] = useState("Jasprit Bumrah");
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState("idle");
  const [progress, setProgress] = useState(0);
  const [step, setStep] = useState("");
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleUpload = useCallback(async () => {
    if (!file) return;
    setStatus("uploading");
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const uploadRes = await fetch(`${API}/upload-video`, { method: "POST", body: formData });
      const uploadData = await uploadRes.json();
      if (!uploadRes.ok) throw new Error(uploadData.error || "Upload failed");

      const jid = uploadData.job_id;
      setJobId(jid);

      const processForm = new FormData();
      processForm.append("job_id", jid);
      processForm.append("style", style);
      processForm.append("batsman", batsman);
      processForm.append("bowler", bowler);

      const processRes = await fetch(`${API}/process-video`, { method: "POST", body: processForm });
      if (!processRes.ok) throw new Error("Process request failed");

      setStatus("processing");
      pollResults(jid);
    } catch (e) {
      setError(e.message);
      setStatus("error");
    }
  }, [file, style, batsman, bowler]);

  const pollResults = useCallback(async (jid) => {
    const poll = async () => {
      try {
        const res = await fetch(`${API}/results/${jid}`);
        const data = await res.json();
        setProgress(data.progress || 0);
        setStep(data.step || "");
        if (data.status === "completed") { setResults(data.results); setStatus("completed"); return; }
        if (data.status === "error") { setError(data.error || "Processing failed"); setStatus("error"); return; }
        setTimeout(poll, 1500);
      } catch {
        setTimeout(poll, 2000);
      }
    };
    poll();
  }, []);

  const handleReset = () => {
    setFile(null); setJobId(null); setStatus("idle");
    setProgress(0); setStep(""); setResults(null); setError(null);
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header__eyebrow">Computer Vision · LLM · Neural TTS</div>
        <h1 className="header__logo">CricComment AI</h1>
        <p className="header__subtitle">
          Drop a cricket video and get AI-powered ball-by-ball commentary with synced audio
        </p>
        <div className="header__divider" />
      </header>

      {status === "idle" && (
        <>
          <div className="main-grid">
            <div className="full-width">
              <VideoUpload file={file} onFileSelect={setFile} />
            </div>

            <div className="card">
              <div className="card__title">
                <span className="card__title-icon">🎙</span> Commentary Style
              </div>
              <StyleSelector style={style} onStyleChange={setStyle} />
            </div>

            <div className="card">
              <div className="card__title">
                <span className="card__title-icon">🏏</span> Player Details
              </div>
              <div className="input-group">
                <div className="input-wrap">
                  <label className="input-label">Batsman</label>
                  <input className="input-field" value={batsman}
                    onChange={(e) => setBatsman(e.target.value)} placeholder="Batsman name" />
                </div>
                <div className="input-wrap">
                  <label className="input-label">Bowler</label>
                  <input className="input-field" value={bowler}
                    onChange={(e) => setBowler(e.target.value)} placeholder="Bowler name" />
                </div>
              </div>
            </div>
          </div>

          <div className="action-row">
            <button className="btn btn-primary" disabled={!file} onClick={handleUpload}>
              Generate Commentary
            </button>
          </div>
        </>
      )}

      {(status === "uploading" || status === "processing") && (
        <ProcessingStatus step={step} progress={progress} status={status} />
      )}

      {status === "error" && (
        <div className="error-card">
          <div className="error-card__icon">⚠</div>
          <div className="error-card__title">Something went wrong</div>
          <p className="error-card__msg">{error}</p>
          <button className="btn btn-ghost" onClick={handleReset}>Try Again</button>
        </div>
      )}

      {status === "completed" && results && (
        <div style={{ marginTop: 32, animation: "fadeIn 0.5s ease" }}>
          {/* Match Stats */}
          <div className="match-stats">
            <div className="stat-box">
              <div className="stat-box__value">{results.match_summary?.score || "0/0"}</div>
              <div className="stat-box__label">Score</div>
            </div>
            <div className="stat-box">
              <div className="stat-box__value">{results.match_summary?.overs || "0.0"}</div>
              <div className="stat-box__label">Overs</div>
            </div>
            <div className="stat-box">
              <div className="stat-box__value">{results.match_summary?.run_rate || "0.0"}</div>
              <div className="stat-box__label">Run Rate</div>
            </div>
            <div className="stat-box">
              <div className="stat-box__value">{results.events?.length || 0}</div>
              <div className="stat-box__label">Events</div>
            </div>
          </div>

          {/* Final Video */}
          {results.final_video?.filename && (
            <div className="video-card" style={{ marginBottom: 18 }}>
              <div className="video-card__header">
                <div className="video-card__title">
                  <span>🎬</span> Final Video with Commentary
                </div>
              </div>
              <video
                controls
                style={{ width: "100%", maxHeight: 520, background: "#000" }}
                src={`/api/video/${results.final_video.filename}`}
              />
              <div className="video-card__footer">
                <span className="video-card__meta">
                  {results.final_video.size_mb} MB
                  {results.final_video.mixed_audio ? " · Mixed audio" : " · Commentary track"}
                </span>
                <a
                  className="btn btn-primary btn-sm"
                  href={`/api/video/${results.final_video.filename}`}
                  download={results.final_video.filename}
                >
                  Download
                </a>
              </div>
            </div>
          )}

          {results.final_video?.error && !results.final_video?.filename && (
            <div className="card full-width" style={{ marginBottom: 18, borderColor: "rgba(244,63,94,0.3)" }}>
              <div className="card__title" style={{ color: "var(--red)" }}>
                <span>⚠</span> Video composition failed
              </div>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem" }}>
                {results.final_video.error}
              </p>
            </div>
          )}

          {/* Audio Player */}
          {results.audio?.full?.filename && (
            <div style={{ marginBottom: 18 }}>
              <AudioPlayer filename={results.audio.full.filename} provider={results.audio.full.provider} />
            </div>
          )}

          {/* Commentary Timeline */}
          <div className="card">
            <div className="card__title">
              <span className="card__title-icon">📋</span> Ball-by-Ball Commentary
            </div>
            <CommentaryTimeline events={results.events || []} />
          </div>

          <div className="action-row">
            <button className="btn btn-ghost" onClick={handleReset}>New Video</button>
          </div>
        </div>
      )}
    </div>
  );
}
