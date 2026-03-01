import { useState, useRef } from "react"
import axios from "axios"
import "./App.css"

// ✅ Hardcoded correct backend URL
const API_URL = "http://127.0.0.1:8000"

const TONES = [
  { value: "professional", emoji: "💼", label: "Professional", desc: "Formal & trustworthy" },
  { value: "casual", emoji: "😊", label: "Casual", desc: "Friendly & relaxed" },
  { value: "luxury", emoji: "✨", label: "Luxury", desc: "Premium & exclusive" },
  { value: "playful", emoji: "🎉", label: "Playful", desc: "Fun & energetic" },
]

export default function App() {

  const [step, setStep] = useState(1)
  const [file, setFile] = useState(null)
  const [columns, setColumns] = useState([])
  const [rowCount, setRowCount] = useState(0)
  const [preview, setPreview] = useState([])
  const [isDragging, setIsDragging] = useState(false)

  const [selectedCol, setSelectedCol] = useState("")
  const [tone, setTone] = useState("professional")
  const [keywords, setKeywords] = useState("")
  const [maxLength, setMaxLength] = useState(200)

  const [loadingCols, setLoadingCols] = useState(false)
  const [isRewriting, setIsRewriting] = useState(false)

  const [downloadUrl, setDownloadUrl] = useState(null)
  const [downloadName, setDownloadName] = useState("")
  const [error, setError] = useState("")

  const fileInputRef = useRef(null)

  // ================= FILE UPLOAD =================
  async function handleFile(selectedFile) {
    setError("")
    setFile(selectedFile)
    setLoadingCols(true)

    try {
      const form = new FormData()
      form.append("file", selectedFile)

      const res = await axios.post(`${API_URL}/get-columns`, form)

      setColumns(res.data.columns)
      setRowCount(res.data.row_count)
      setPreview(res.data.preview)
      setSelectedCol(res.data.columns[0])
      setStep(2)

    } catch (err) {
      console.error(err)
      setError("Failed to read file. Check backend connection.")
    } finally {
      setLoadingCols(false)
    }
  }

  function onFileInputChange(e) {
    if (e.target.files[0]) handleFile(e.target.files[0])
  }

  function onDragOver(e) {
    e.preventDefault()
    setIsDragging(true)
  }

  function onDragLeave() {
    setIsDragging(false)
  }

  function onDrop(e) {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0])
  }

  // ================= REWRITE =================
  async function handleRewrite() {
    if (!file || !selectedCol) return

    setIsRewriting(true)
    setError("")

    try {
      const form = new FormData()
      form.append("file", file)
      form.append("column", selectedCol)
      form.append("tone", tone)
      form.append("keywords", keywords)
      form.append("max_length", maxLength)

      const res = await axios.post(`${API_URL}/rewrite`, form, {
        responseType: "blob",
      })

      const url = URL.createObjectURL(res.data)
      setDownloadUrl(url)
      setDownloadName(`rewritten_${file.name}`)
      setStep(3)

    } catch (err) {
      console.error(err)
      setError("Rewriting failed. Make sure backend is running.")
    } finally {
      setIsRewriting(false)
    }
  }

  function triggerDownload() {
    const link = document.createElement("a")
    link.href = downloadUrl
    link.download = downloadName
    link.click()
  }

  function reset() {
    setStep(1)
    setFile(null)
    setColumns([])
    setRowCount(0)
    setPreview([])
    setSelectedCol("")
    setDownloadUrl(null)
    setError("")
    if (fileInputRef.current) fileInputRef.current.value = ""
  }

  // ================= UI =================
  return (
    <div className="app">

      <header className="header">
        <div className="logo">Rewrite<span>.AI</span></div>
        <div className="header-badges">
          <span className="badge">React + FastAPI</span>
          <span className="badge badge-green">Mock Mode</span>
        </div>
      </header>

      <main className="main">

        <div className="hero">
          <h1>Rewrite product descriptions<br />
            <span className="hero-accent">at scale with AI</span>
          </h1>
        </div>

        {error && (
          <div className="error-bar">
            ⚠ {error}
          </div>
        )}

        {/* STEP 1 */}
        {step === 1 && (
          <div className="card upload-card">
            <h2>Upload your product CSV</h2>

            <div
              className={`drop-zone ${isDragging ? "dragging" : ""}`}
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
              onDrop={onDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={onFileInputChange}
                style={{ display: "none" }}
              />

              {loadingCols ? (
                <p>Reading file...</p>
              ) : (
                <>
                  <div className="drop-icon">📂</div>
                  <p><strong>Drop your file here</strong> or click to browse</p>
                </>
              )}
            </div>
          </div>
        )}

        {/* STEP 2 */}
        {step === 2 && (
          <div className="card">
            <h3>{rowCount} rows detected</h3>

            <label>Select description column:</label>
            <select
              value={selectedCol}
              onChange={e => setSelectedCol(e.target.value)}
            >
              {columns.map(col => (
                <option key={col} value={col}>{col}</option>
              ))}
            </select>

            <button
              className="btn-primary"
              onClick={handleRewrite}
              disabled={isRewriting}
            >
              {isRewriting ? "Rewriting..." : `Rewrite ${rowCount} Descriptions`}
            </button>
          </div>
        )}

        {/* STEP 3 */}
        {step === 3 && (
          <div className="card success-card">
            <h2>All {rowCount} descriptions rewritten!</h2>

            <button className="btn-primary" onClick={triggerDownload}>
              ⬇ Download CSV
            </button>

            <button className="btn-ghost" onClick={reset}>
              Process another file
            </button>
          </div>
        )}

      </main>

    </div>
  )
}