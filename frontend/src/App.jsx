import { useState } from "react";
import { registerAudioAPI, verifyAudioAPI } from "./api";
import { Upload, CheckCircle, AlertTriangle, FileAudio, ArrowRight } from "lucide-react";
import './App.css';

function App() {
  // --- STATES ---
  // 'home' | 'analyzing' | 'match_found' | 'register_new' | 'success'
  const [screen, setScreen] = useState("home"); 
  
  const [file, setFile] = useState(null);
  const [matchData, setMatchData] = useState(null);
  
  // Registration Form Data
  const [audioId, setAudioId] = useState("");
  const [ownerName, setOwnerName] = useState("");

  // --- LOGIC: STEP 1 (VERIFY) ---
  const handleAnalyze = async () => {
    if (!file) {
      alert("Please select an audio file first!");
      return;
    }

    setScreen("analyzing");

    try {
      // 1. Send file to backend to check
      const data = await verifyAudioAPI(file);

      // 2. Decide where to go based on result
      if (data.status === "MATCH_FOUND") {
        setMatchData(data);
        setScreen("match_found");
      } else {
        // Assume no match found, let's register it
        setScreen("register_new");
      }
    } catch (error) {
      console.error(error);
      alert("Error connecting to server. Is backend running?");
      setScreen("home");
    }
  };

  // --- LOGIC: STEP 2 (REGISTER) ---
  const handleRegister = async () => {
    if (!audioId || !ownerName) {
      alert("Please fill in all details.");
      return;
    }

    try {
      // Use the file we already uploaded in Step 1
      await registerAudioAPI(file, audioId); 
      setScreen("success");
    } catch (error) {
      alert("Registration failed.");
    }
  };

  // --- LOGIC: RESET ---
  const resetApp = () => {
    setFile(null);
    setMatchData(null);
    setAudioId("");
    setOwnerName("");
    setScreen("home");
  };

  // ================= RENDER =================

  return (
    <div className="app-container">
      
      {/* HEADER */}
      <header className="navbar">
        <h2>🎵 AudioShield <span style={{fontSize: "0.6em", opacity: 0.8}}>Blockchain Copyright</span></h2>
      </header>

      <main className="main-content">

        {/* --- SCREEN 1: HOME / UPLOAD --- */}
        {screen === "home" && (
          <div className="card fade-in">
            <h1>Verify Audio Copyright</h1>
            <p>Upload a track to check for existing blockchain records.</p>
            
            <div className="upload-box">
              <input 
                type="file" 
                id="file-upload" 
                accept="audio/*"
                onChange={(e) => setFile(e.target.files[0])}
                hidden
              />
              <label htmlFor="file-upload" className="upload-label">
                <Upload size={48} color="#646cff" />
                <span style={{marginTop: "15px", fontSize: "1.2em"}}>
                  {file ? file.name : "Click to Upload Audio"}
                </span>
              </label>
            </div>

            <button className="primary-btn" onClick={handleAnalyze} disabled={!file}>
              Analyze Audio <ArrowRight size={18} style={{marginLeft: "10px"}}/>
            </button>
          </div>
        )}

        {/* --- SCREEN 2: ANALYZING --- */}
        {screen === "analyzing" && (
          <div className="card fade-in">
            <div className="spinner"></div>
            <h3>Scanning Blockchain...</h3>
            <p>Generating acoustic fingerprint & comparing hashes.</p>
          </div>
        )}

        {/* --- SCREEN 3: MATCH FOUND (WARNING) --- */}
        {screen === "match_found" && matchData && (
          <div className="card match-card fade-in">
            <div className="icon-badge warning">
              <AlertTriangle size={40} />
            </div>
            <h2 style={{color: "#d9534f"}}>Match Detected!</h2>
            <p>This audio is already registered on the blockchain.</p>
            
            <div className="data-display">
              <div className="data-row">
                <span>Song ID:</span>
                <strong>{matchData.metadata.audio_id}</strong>
              </div>
              <div className="data-row">
                <span>Owner:</span>
                <strong className="mono">{matchData.metadata.owner.substring(0, 15)}...</strong>
              </div>
              <div className="data-row">
                <span>Match Score:</span>
                <strong>{matchData.match_score} (High Confidence)</strong>
              </div>
            </div>

            <button className="secondary-btn" onClick={resetApp}>
              Check Another File
            </button>
          </div>
        )}

        {/* --- SCREEN 4: NO MATCH (REGISTER FORM) --- */}
        {screen === "register_new" && (
          <div className="card fade-in">
            <div className="icon-badge success">
              <CheckCircle size={40} />
            </div>
            <h2 style={{color: "#4CAF50"}}>No Match Found</h2>
            <p>This content appears original. Register it now to claim ownership.</p>

            <div className="form-group">
              <label>Track Title (Audio ID)</label>
              <input 
                type="text" 
                placeholder="e.g., Summer Vibes v1"
                value={audioId}
                onChange={(e) => setAudioId(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Owner Name</label>
              <input 
                type="text" 
                placeholder="e.g., John Doe"
                value={ownerName}
                onChange={(e) => setOwnerName(e.target.value)}
              />
            </div>

            <div className="file-preview">
              <FileAudio size={18} /> 
              <span>{file?.name}</span>
            </div>

            <button className="primary-btn" onClick={handleRegister}>
              Mint to Blockchain
            </button>
            <br/>
            <button className="text-btn" onClick={resetApp}>Cancel</button>
          </div>
        )}

        {/* --- SCREEN 5: SUCCESS --- */}
        {screen === "success" && (
          <div className="card fade-in">
             <div className="icon-badge success">
              <CheckCircle size={60} />
            </div>
            <h1>Registration Complete!</h1>
            <p>Your audio fingerprint has been permanently added to the blockchain database.</p>
            <button className="primary-btn" onClick={resetApp}>Home</button>
          </div>
        )}

      </main>
    </div>
  );
}

export default App;