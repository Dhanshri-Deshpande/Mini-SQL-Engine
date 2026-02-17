import React, { useEffect, useState, useRef } from "react";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [tables, setTables] = useState([]);
  const [openTabs, setOpenTabs] = useState([]);
  const [activeTab, setActiveTab] = useState(null);
  const [terminalLogs, setTerminalLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  const terminalRef = useRef(null);
  const queryRef = useRef(null);

  useEffect(() => {
    loadTables();
    queryRef.current.focus();
  }, []);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop =
        terminalRef.current.scrollHeight;
    }
  }, [terminalLogs]);

  const loadTables = () => {
    fetch("http://127.0.0.1:5000/tables")
      .then(res => res.json())
      .then(data => setTables(data));
  };

  const sendQuery = () => {
    if (!query.trim()) return;

    const currentQuery = query;
    const upperQuery = currentQuery.toUpperCase();

    setLoading(true);

    fetch("http://127.0.0.1:5000/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: currentQuery })
    })
      .then(res => res.json())
      .then(data => {
        setLoading(false);
        loadTables();

        let message = "✔ Query executed successfully";
        let type = "success";

        if (data.result?.toString().startsWith("Error")) {
          message = data.result;
          type = "error";
        } else {
          if (upperQuery.startsWith("MAKE"))
            message = "✔ Table created successfully";
          else if (upperQuery.startsWith("ADD"))
            message = "✔ Record inserted successfully";
          else if (upperQuery.startsWith("ERASE"))
            message = "✔ Record deleted successfully";
          else if (upperQuery.startsWith("CHANGE"))
            message = "✔ Record updated successfully";
          else if (upperQuery.startsWith("SHOW"))
            message = "✔ Data fetched successfully";
        }

        setTerminalLogs(prev => [
          ...prev,
          { type: "query", message: `DB> ${currentQuery}` },
          { type, message }
        ]);

        if (activeTab) refreshActiveTab();

        setQuery("");
        queryRef.current.focus();
      })
      .catch(() => {
        setLoading(false);
        setTerminalLogs(prev => [
          ...prev,
          { type: "error", message: "❌ Error executing query" }
        ]);
      });
  };

  const refreshActiveTab = () => {
    fetch(`http://127.0.0.1:5000/table/${activeTab}`)
      .then(res => res.json())
      .then(updatedData => {
        setOpenTabs(prev =>
          prev.map(tab =>
            tab.name === activeTab
              ? { ...tab, data: updatedData }
              : tab
          )
        );
      });
  };

  const uploadCSV = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    fetch("http://127.0.0.1:5000/upload", {
      method: "POST",
      body: formData
    })
      .then(res => res.json())
      .then(data => {
        setTerminalLogs(prev => [
          ...prev,
          { type: "success", message: `✔ ${data.message}` }
        ]);
        loadTables();
      });
  };

  const loadTable = (name) => {
    fetch(`http://127.0.0.1:5000/table/${name}`)
      .then(res => res.json())
      .then(data => {
        const exists = openTabs.find(tab => tab.name === name);
        if (!exists) {
          setOpenTabs([...openTabs, { name, data }]);
        }
        setActiveTab(name);
      });
  };

  const closeTab = (name) => {
    const updated = openTabs.filter(tab => tab.name !== name);
    setOpenTabs(updated);
    if (activeTab === name)
      setActiveTab(updated.length ? updated[0].name : null);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendQuery();
    }
  };

  return (
    <div className="app-container">

      {/* Sidebar */}
      <div className="sidebar">
        <h3>📁 Tables</h3>
        <ul>
          {tables.map((table, index) => (
            <li
              key={index}
              className={activeTab === table ? "active-table" : ""}
              onClick={() => loadTable(table)}
              onDoubleClick={() => setQuery(`SHOW ${table}`)}
            >
              {table}
            </li>
          ))}
        </ul>
      </div>

      {/* Main */}
      <div className="main">

        <div className="top-bar">
          <h2>🚀 Mini SQL Engine</h2>
          <input type="file" accept=".csv" onChange={uploadCSV} />
        </div>

        <div className="editor-section">
          <textarea
            ref={queryRef}
            placeholder="Write SQL Query..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={4}
            className="query-box"
          />

          <button className="run-btn" onClick={sendQuery}>
            {loading ? "Running..." : "Run"}
          </button>
        </div>

        {/* Tabs */}
        <div className="tabs">
          {openTabs.map((tab, index) => (
            <div
              key={index}
              className={`tab ${activeTab === tab.name ? "active" : ""}`}
              onClick={() => setActiveTab(tab.name)}
            >
              {tab.name}
              <span
                className="close-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  closeTab(tab.name);
                }}
              >
                ×
              </span>
            </div>
          ))}
        </div>

        {/* Active Table */}
        <div className="table-section">
          {openTabs.map(tab =>
            tab.name === activeTab ? (
              <table key={tab.name}>
                <tbody>
                  {tab.data.map((row, i) => (
                    <tr key={i}>
                      {row.map((cell, j) => (
                        <td key={j}>{cell}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : null
          )}
        </div>

        {/* Terminal */}
        <div className="terminal">
          <div className="terminal-header">🖥 Terminal</div>
          <div className="terminal-body" ref={terminalRef}>
            {terminalLogs.map((log, index) => (
              <div key={index} className={`log ${log.type}`}>
                {log.message}
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;
