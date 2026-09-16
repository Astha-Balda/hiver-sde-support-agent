import { useState } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);

  const suggestions = [
    {
      icon: "📦",
      title: "Track my order",
      text: "Where is my order? It is late.",
    },
    {
      icon: "💳",
      title: "Payment issue",
      text: "My payment failed but money was deducted.",
    },
    {
      icon: "↩",
      title: "Request a refund",
      text: "I want a refund for my order.",
    },
    {
      icon: "⚠",
      title: "Wrong product",
      text: "I received the wrong product.",
    },
  ];

  const sendMessage = (text = message) => {
    if (!text.trim()) return;

    setMessages((prev) => [
      ...prev,
      {
        text: text.trim(),
        sender: "user",
      },
    ]);

    setMessage("");
  };

  const handleSuggestion = (text) => {
    sendMessage(text);
  };

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">R</div>

          <div>
            <h1>ResolveAI</h1>
            <span>Support assistant</span>
          </div>
        </div>

        <button
          className="new-chat"
          onClick={() => setMessages([])}
        >
          <span>+</span>
          New conversation
        </button>

        <div className="sidebar-section">
          <p className="section-title">Recent</p>

          {messages.length > 0 ? (
            <div className="conversation">
              <div className="conversation-icon">💬</div>

              <div>
                <strong>{messages[0].text.slice(0, 24)}</strong>
                <span>Just now</span>
              </div>
            </div>
          ) : (
            <p className="empty-history">
              Your conversations will appear here.
            </p>
          )}
        </div>

        <div className="sidebar-bottom">
          <div className="online-status">
            <span></span>
            AI assistant online
          </div>

          <div className="powered">
            Powered by Gemini
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="main">

        <div className="chat-area">
          {messages.length === 0 ? (
            <div className="welcome">
              <div className="welcome-icon">✦</div>

              <p className="eyebrow">AI CUSTOMER SUPPORT</p>

              <h2>
                How can we
                <br />
                <span>help you today?</span>
              </h2>

              <p className="welcome-text">
                Get quick, helpful answers about orders, payments,
                refunds, deliveries, and more.
              </p>

              <div className="suggestions">
                {suggestions.map((item) => (
                  <button
                    key={item.title}
                    className="suggestion-card"
                    onClick={() => handleSuggestion(item.text)}
                  >
                    <div className="suggestion-icon">
                      {item.icon}
                    </div>

                    <div>
                      <strong>{item.title}</strong>
                      <span>{item.text}</span>
                    </div>

                    <span className="arrow">→</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="messages">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`message-row ${msg.sender}`}
                >
                  {msg.sender === "assistant" && (
                    <div className="avatar">R</div>
                  )}

                  <div className="message-content">
                    <div className="message-name">
                      {msg.sender === "user"
                        ? "You"
                        : "ResolveAI"}
                    </div>

                    <div className="message-bubble">
                      {msg.text}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Input */}
        <div className="input-wrapper">
          <div className="input-box">
            <input
              type="text"
              value={message}
              placeholder="Ask ResolveAI anything..."
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  sendMessage();
                }
              }}
            />

            <button
              className="send-button"
              onClick={() => sendMessage()}
              disabled={!message.trim()}
            >
              ↑
            </button>
          </div>

          <p className="input-note">
            ResolveAI can make mistakes. Please verify important information.
          </p>
        </div>
      </main>
    </div>
  );
}

export default App;