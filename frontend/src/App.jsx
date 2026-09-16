import { useState } from "react";

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [query, setQuery] = useState("");
  const [repoStatus, setRepoStatus] = useState(null);
  const [activeRepoId, setActiveRepoId] = useState(null);
  const [activeRepoName, setActiveRepoName] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);

  const ingestRepository = async () => {
    if (!repoUrl.trim()) return;
    
    setLoading(true);
    setRepoStatus({ message: "Indexing repository...", type: "info" });
    setAnswer("");
    setSources([]);
    setActiveRepoId(null);
    setActiveRepoName("");

    try {
      const response = await fetch(`${API_URL}/api/repositories/ingest`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: repoUrl,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Ingestion failed");
      }

      setActiveRepoId(data.repository_id);
      setActiveRepoName(data.repository);
      
      if (data.cached) {
        setRepoStatus({ 
          message: `✓ Repository already indexed\nUsing existing context for ${data.repository}`, 
          type: "success" 
        });
      } else {
        setRepoStatus({ 
          message: `✓ Successfully indexed ${data.repository}\n${data.files_added} files ready for analysis`, 
          type: "success" 
        });
      }
    } catch (error) {
      setRepoStatus({ message: `Error: ${error.message}`, type: "error" });
    } finally {
      setLoading(false);
    }
  };

  const askQuestion = async () => {
    if (!query.trim() || !activeRepoId) return;

    setLoading(true);
    setAnswer("");
    setSources([]);

    try {
      const response = await fetch(
        `${API_URL}/api/repositories/ask?query=${encodeURIComponent(
          query
        )}&repository_id=${activeRepoId}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Query failed");
      }

      setAnswer(data.answer);
      setSources(data.sources || []);
    } catch (error) {
      setAnswer(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0d1117] via-[#0d1117] to-[#161b22] text-[#c9d1d9] font-system">
      <div className="max-w-5xl mx-auto px-6 py-8 lg:py-12">
        
        {/* Header */}
        <header className="mb-12">
          <div className="flex justify-between items-start mb-2">
            <div>
              <h1 className="text-4xl font-bold text-white tracking-tight mb-1">RepoLens</h1>
              <p className="text-sm text-[#8b949e] font-regular">AI-powered codebase intelligence and analysis</p>
            </div>
            <div className="flex items-center space-x-2 bg-[#21262d] px-3 py-1.5 rounded-md border border-[#30363d]">
              <span className="w-2 h-2 rounded-full bg-[#3fb950] animate-pulse"></span>
              <span className="text-xs font-medium text-[#3fb950]">Ready</span>
            </div>
          </div>
          <div className="h-px bg-gradient-to-r from-[#30363d] via-[#30363d] to-transparent mt-6"></div>
        </header>

        {/* Main Content Grid */}
        <div className="space-y-8">

          {/* Repository Ingestion Section */}
          <section>
            <div className="mb-4">
              <h2 className="text-sm font-semibold uppercase tracking-widest text-[#8b949e] mb-1">Connect Repository</h2>
              <p className="text-xs text-[#6e7681]">Index a GitHub repository to begin analysis</p>
            </div>
            
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-[#3fb950]/10 via-transparent to-transparent rounded-lg blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <div className="relative bg-[#161b22] border border-[#30363d] hover:border-[#3fb950]/30 rounded-lg p-5 transition-all duration-300">
                <div className="flex gap-3">
                  <input
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !loading && repoUrl.trim()) {
                        e.preventDefault();
                        ingestRepository();
                      }
                    }}
                    placeholder="github.com/owner/repository"
                    className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-md px-4 py-2.5 text-sm text-[#c9d1d9] focus:outline-none focus:border-[#3fb950] focus:ring-2 focus:ring-[#3fb950]/20 placeholder-[#484f58] disabled:opacity-50 transition-all duration-200"
                    disabled={loading}
                  />
                  <button
                    onClick={ingestRepository}
                    disabled={loading || !repoUrl.trim()}
                    className="bg-[#238636] hover:bg-[#2ea043] active:bg-[#238636] disabled:bg-[#238636]/40 disabled:text-white/40 text-white px-6 py-2.5 rounded-md text-sm font-semibold transition-all duration-200 border border-[#1a7f37] hover:shadow-lg hover:shadow-[#3fb950]/20 whitespace-nowrap"
                  >
                    {loading && !activeRepoId ? "Indexing..." : "Index"}
                  </button>
                </div>

                {repoStatus && (
                  <div className={`mt-4 text-sm font-medium ${
                    repoStatus.type === 'error' ? 'text-[#f85149]' : 
                    repoStatus.type === 'success' ? 'text-[#3fb950]' : 'text-[#58a6ff]'
                  }`}>
                    {repoStatus.message}
                  </div>
                )}
              </div>
            </div>
          </section>

          {/* Query Section */}
          <section>
            <div className="mb-4 flex justify-between items-start">
              <div>
                <h2 className="text-sm font-semibold uppercase tracking-widest text-[#8b949e] mb-1">Query Repository</h2>
                <p className="text-xs text-[#6e7681]">Ask questions about your codebase</p>
              </div>
              {activeRepoName && (
                <div className="flex items-center space-x-2 bg-[#0d1117] px-3 py-1.5 rounded-md border border-[#3fb950]/30">
                  <span className="w-2 h-2 rounded-full bg-[#3fb950]"></span>
                  <span className="text-xs font-mono text-[#3fb950]">{activeRepoName}</span>
                </div>
              )}
            </div>

            {!activeRepoId ? (
              <div className="bg-[#161b22] border border-[#30363d] border-dashed rounded-lg p-8 text-center">
                <div className="mb-3">
                  <svg className="w-10 h-10 mx-auto text-[#8b949e]/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <p className="text-[#8b949e] text-sm">Index a repository above to start querying</p>
              </div>
            ) : (
              <div className="bg-[#161b22] border border-[#30363d] rounded-lg overflow-hidden">
                <div className="p-5 space-y-4">
                  <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && e.ctrlKey && activeRepoId && !loading && query.trim()) {
                        e.preventDefault();
                        askQuestion();
                      }
                    }}
                    placeholder="What would you like to know about this codebase? (Ctrl+Enter to send)"
                    className="w-full bg-[#0d1117] border border-[#30363d] rounded-md px-4 py-3 text-sm text-[#c9d1d9] focus:outline-none focus:border-[#3fb950] focus:ring-2 focus:ring-[#3fb950]/20 placeholder-[#484f58] disabled:opacity-50 resize-none transition-all duration-200"
                    rows="4"
                    disabled={loading}
                  />
                  <div className="flex justify-end">
                    <button
                      onClick={askQuestion}
                      disabled={!activeRepoId || loading || !query.trim()}
                      className="bg-[#238636] hover:bg-[#2ea043] active:bg-[#238636] disabled:bg-[#238636]/40 disabled:text-white/40 text-white px-6 py-2 rounded-md text-sm font-semibold transition-all duration-200 border border-[#1a7f37] hover:shadow-lg hover:shadow-[#3fb950]/20"
                    >
                      {loading ? "Analyzing..." : "Send Query"}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </section>

          {/* Results Section */}
          {answer && (
            <section className="space-y-6 pt-4 border-t border-[#30363d]">
              
              {/* Answer */}
              <div>
                <h2 className="text-sm font-semibold uppercase tracking-widest text-[#8b949e] mb-4">Analysis Result</h2>
                <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-6">
                  <div className="prose prose-invert max-w-none text-sm text-[#c9d1d9] leading-relaxed whitespace-pre-wrap font-light">
                    {answer}
                  </div>
                </div>
              </div>

              {/* Sources */}
              <div>
                <h2 className="text-sm font-semibold uppercase tracking-widest text-[#8b949e] mb-4">Source References</h2>
                {sources.length > 0 ? (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                    {sources.map((source, index) => (
                      <div
                        key={index}
                        className="bg-[#161b22] border border-[#30363d] hover:border-[#3fb950]/30 rounded-lg p-4 transition-all duration-200 group"
                      >
                        <div className="font-mono text-xs text-[#58a6ff] mb-2 truncate group-hover:text-[#79c0ff] transition-colors" title={source.file}>
                          📄 {source.file}
                        </div>
                        <div className="flex items-center justify-between gap-2">
                          <span className="text-[11px] font-mono text-[#8b949e] truncate" title={source.symbol || "N/A"}>
                            {source.symbol || "Function"}
                          </span>
                          <span className="px-2 py-0.5 rounded-sm bg-[#0d1117] text-[#58a6ff] text-[10px] font-mono border border-[#30363d] whitespace-nowrap">
                            {source.language || "Unknown"}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 text-center">
                    <p className="text-sm text-[#8b949e]">No direct sources found for this query</p>
                  </div>
                )}
              </div>

            </section>
          )}

        </div>

        {/* Footer */}
        <footer className="mt-16 pt-8 border-t border-[#30363d]">
          <p className="text-xs text-[#6e7681] text-center">RepoLens • AI Codebase Intelligence Platform</p>
        </footer>

      </div>
    </div>
  );
}

export default App;