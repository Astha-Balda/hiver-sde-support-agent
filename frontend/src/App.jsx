import { useState, useEffect, useRef } from "react";
import "./App.css";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "/api"
).replace(/\/$/, "");

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

    const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

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

  const sendMessage = async (text = message) => {
    const query = text.trim();

    if (!query || loading) return;

    // Show user's message immediately
    setMessages((prev) => [
      ...prev,
      {
        text: query,
        sender: "user",
      },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/support`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            query: query,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Backend request failed");
      }

      const data = await response.json();

      // Add AI response
      setMessages((prev) => [
        ...prev,
        {
          text: data.response,
          sender: "assistant",
          confidence: data.confidence,
          similarity: data.similarity,
        },
      ]);
    } catch (error) {
      console.error("Error:", error);

      setMessages((prev) => [
        ...prev,
        {
          text: "Sorry, I am unable to connect to the support service right now. Please try again.",
          sender: "assistant",
        },
      ]);
    } finally {
      setLoading(false);
    }
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
                <strong>
                  {messages[0].text.slice(0, 24)}
                </strong>

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

              <div className="welcome-icon">
                ✦
              </div>

              <p className="eyebrow">
                AI CUSTOMER SUPPORT
              </p>

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
                    onClick={() =>
                      handleSuggestion(item.text)
                    }
                  >

                    <div className="suggestion-icon">
                      {item.icon}
                    </div>

                    <div>
                      <strong>
                        {item.title}
                      </strong>

                      <span>
                        {item.text}
                      </span>
                    </div>

                    <span className="arrow">
                      →
                    </span>

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
                    <div className="avatar">
                      R
                    </div>
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

              {/* Auto-scroll target */}
              <div ref={messagesEndRef} />

              {/* Loading indicator */}
              {loading && (
                <div className="message-row assistant">

                  <div className="avatar">
                    R
                  </div>

                  <div className="message-content">

                    <div className="message-name">
                      ResolveAI
                    </div>

                    <div className="message-bubble typing">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>

                  </div>

                </div>
              )}

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
              disabled={loading}
              onChange={(e) =>
                setMessage(e.target.value)
              }
              onKeyDown={(e) => {

                if (e.key === "Enter") {
                  sendMessage();
                }

              }}
            />

            <button
              className="send-button"
              onClick={() => sendMessage()}
              disabled={!message.trim() || loading}
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
