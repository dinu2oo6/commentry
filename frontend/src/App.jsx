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
  const [status, setStatus] = useState("idle"); // idle | uploading | processing | completed | error
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

      const uploadRes = await fetch(`${API}/upload-video`, {
        method: "POST",
        body: formData,
      });
      const uploadData = await uploadRes.json();
      if (!uploadRes.ok) throw new Error(uploadData.error || "Upload failed");

      const jid = uploadData.job_id;
      setJobId(jid);

      // Start processing
      const processForm = new FormData();
      processForm.append("job_id", jid);
      processForm.append("style", style);
      processForm.append("batsman", batsman);
      processForm.append("bowler", bowler);

      const processRes = await fetch(`${API}/process-video`, {
        method: "POST",
        body: processForm,
      });
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

        if (data.status === "completed") {
          setResults(data.results);
          setStatus("completed");
          return;
        }
        if (data.status === "error") {
          setError(data.error || "Processing failed");
          setStatus("error");
          return;
        }
        setTimeout(poll, 1500);
      } catch {
        setTimeout(poll, 2000);
      }
    };
    poll();
  }, []);

  const handleReset = () => {
    setFile(null);
    setJobId(null);
    setStatus("idle");
    setProgress(0);
    setStep("");
    setResults(null);
    setError(null);
  };

  return (
    <div className="app">
      <header className="header">
        <h1 className="header__logo">CricComment AI</h1>
        <p className="header__subtitle">
          AI-Powered Cricket Commentary from Video
        </p>
        <span className="header__badge">Computer Vision • LLM • TTS</span>
      </header>

      {status === "idle" && (
        <>
          <div className="main-grid">
            <div className="full-width">
              <VideoUpload file={file} onFileSelect={setFile} />
            </div>
            <div className="full-width card">
              <div className="card__title">
                <span className="card__title-icon">🎙️</span> Commentary Style
              </div>
              <StyleSelector style={style} onStyleChange={setStyle} />
            </div>
            <div className="full-width card">
              <div className="card__title">
                <span className="card__title-icon">🏏</span> Player Details
              </div>
              <div className="input-group">
                <div style={{ flex: 1 }}>
                  <div className="input-label">Batsman</div>
                  <input
                    className="input-field"
                    value={batsman}
                    onChange={(e) => setBatsman(e.target.value)}
                    placeholder="Batsman name"
                  />
                </div>
                <div style={{ flex: 1 }}>
                  <div className="input-label">Bowler</div>
                  <input
                    className="input-field"
                    value={bowler}
                    onChange={(e) => setBowler(e.target.value)}
                    placeholder="Bowler name"
                  />
                </div>
              </div>
            </div>
          </div>
          <div className="action-row">
            <button
              className="btn btn-primary"
              disabled={!file}
              onClick={handleUpload}
            >
              🚀 Generate Commentary
            </button>
          </div>
        </>
      )}

      {(status === "uploading" || status === "processing") && (
        <ProcessingStatus step={step} progress={progress} status={status} />
      )}

      {status === "error" && (
        <div
          className="card full-width"
          style={{ marginTop: 24, textAlign: "center" }}
        >
          <div
            className="card__title"
            style={{ color: "var(--accent-red)", justifyContent: "center" }}
          >
            <span className="card__title-icon">❌</span> Error
          </div>
          <p style={{ color: "var(--text-secondary)", marginBottom: 16 }}>
            {error}
          </p>
          <button className="btn btn-ghost" onClick={handleReset}>
            Try Again
          </button>
        </div>
      )}

      {status === "completed" && results && (
        <div className="main-grid" style={{ marginTop: 24 }}>
          {/* Match Summary */}
          <div className="full-width">
            <div className="match-card">
              <div className="stat-box">
                <div className="stat-box__value">
                  {results.match_summary?.score || "0/0"}
                </div>
                <div className="stat-box__label">Score</div>
              </div>
              <div className="stat-box">
                <div className="stat-box__value">
                  {results.match_summary?.overs || "0.0"}
                </div>
                <div className="stat-box__label">Overs</div>
              </div>
              <div className="stat-box">
                <div className="stat-box__value">
                  {results.match_summary?.run_rate || "0.0"}
                </div>
                <div className="stat-box__label">Run Rate</div>
              </div>
              <div className="stat-box">
                <div className="stat-box__value">
                  {results.events?.length || 0}
                </div>
                <div className="stat-box__label">Events</div>
              </div>
            </div>
          </div>

          {/* Final Video with Commentary */}
          {results.final_video?.filename && (
            <div
              className="full-width card"
              style={{ padding: 0, overflow: "hidden" }}
            >
              <div
                className="card__title"
                style={{ padding: "20px 28px 10px" }}
              >
                <span className="card__title-icon">🎬</span> Final Video with
                Commentary
              </div>
              <video
                controls
                style={{ width: "100%", maxHeight: 500, background: "#000" }}
                src={`/api/video/${results.final_video.filename}`}
              />
              <div
                style={{
                  padding: "12px 28px 20px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <span
                  style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}
                >
                  {results.final_video.size_mb} MB • Commentary audio merged
                </span>
                <a
                  className="btn btn-primary"
                  href={`/api/video/${results.final_video.filename}`}
                  download={results.final_video.filename}
                  style={{ fontSize: "0.85rem", padding: "10px 22px" }}
                >
                  ⬇ Download Video
                </a>
              </div>
            </div>
          )}

          {results.final_video?.error && (
            <div className="full-width card" style={{ marginTop: 16 }}>
              <div
                className="card__title"
                style={{ color: "var(--accent-red)" }}
              >
                <span className="card__title-icon">⚠️</span> Final Video
                Generation Issue
              </div>
              <p style={{ color: "var(--text-secondary)", margin: "0 0 8px" }}>
                The commentary audio was generated, but the final merged video
                could not be created.
              </p>
              <p
                style={{
                  color: "var(--text-secondary)",
                  margin: 0,
                  fontSize: "0.95rem",
                }}
              >
                {results.final_video.error}
              </p>
            </div>
          )}

          {/* Audio Player */}
          {results.audio?.full?.filename && (
            <div className="full-width">
              <AudioPlayer
                filename={results.audio.full.filename}
                provider={results.audio.full.provider}
              />
            </div>
          )}

          {/* Commentary Timeline */}
          <div className="full-width card">
            <div className="card__title">
              <span className="card__title-icon">📋</span> Ball-by-Ball
              Commentary
            </div>
            <CommentaryTimeline events={results.events || []} />
          </div>

          <div className="full-width action-row">
            <button className="btn btn-ghost" onClick={handleReset}>
              🔄 New Video
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
