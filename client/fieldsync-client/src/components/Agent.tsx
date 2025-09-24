import React, { useState } from "react";
import { sendMessage } from "../services/api";

const Agent: React.FC = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<{ user: string; bot: string }[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    setMessages([...messages, { user: input, bot: "" }]);
    setLoading(true);

    const result = await sendMessage(input);
    setMessages((prev) => [...prev.slice(0, -1), { user: input, bot: result.result || "Error" }]);

    setInput("");
    setLoading(false);
  };

  return (
    <div style={{ padding: "1rem" }}>
      <div style={{ maxHeight: "300px", overflowY: "auto", marginBottom: "1rem" }}>
        {messages.map((m, i) => (
          <div key={i} style={{ marginBottom: "0.5rem" }}>
            <strong>User:</strong> {m.user} <br />
            <strong>Bot:</strong> {m.bot}
          </div>
        ))}
      </div>

      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type your message..."
        style={{ marginRight: "0.5rem" }}
      />
      <button onClick={handleSend} disabled={loading}>
        {loading ? "Sending..." : "Send"}
      </button>
    </div>
  );
};

export default Agent;
