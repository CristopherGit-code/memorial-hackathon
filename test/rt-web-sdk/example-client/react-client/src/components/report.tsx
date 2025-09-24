import React from "react";

type ReportProps = {
  result: string;
};

const Report: React.FC<ReportProps> = ({ result }) => {
  const data = JSON.parse(result);
  const final_result: string = data.result;
  console.log(final_result)

  let lines
  try{
      lines = final_result.split("\n").map((l) => l.trim()).filter(Boolean);
  }catch (error){
    return  (
        <div>
            <p>Waiting for transcription...</p>
        </div>
    )
  }

  // Extract structured fields
  const title = lines.find((l) => l.toLowerCase().includes("formal business"));
  const subject = lines.find((l) => l.toLowerCase().startsWith("subject:"));
  const date = lines.find((l) => l.toLowerCase().startsWith("date:"));
  const greeting = lines.find((l) => l.toLowerCase().startsWith("dear"));
  const closingIndex = lines.findIndex(
    (l) =>
      l.toLowerCase().startsWith("best regards") ||
      l.toLowerCase().startsWith("regards")
  );

  const bodyLines = lines.filter(
    (l, i) =>
      l !== title &&
      l !== subject &&
      l !== date &&
      l !== greeting &&
      (closingIndex === -1 || i < closingIndex)
  );

  const listItems = bodyLines.filter((l) => l.startsWith("- "));
  const paragraphs = bodyLines.filter((l) => !l.startsWith("- "));

  const closing = closingIndex !== -1 ? lines.slice(closingIndex) : [];

  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: 12,
        padding: "2rem",
        maxWidth: 700,
        margin: "2rem auto",
        fontFamily: "Segoe UI, Arial, sans-serif",
        background: "#fff",
        boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
      }}
    >
      {title && (
        <h1 style={{ marginBottom: "1rem", fontSize: "1.5rem", color: "#333" }}>
          {title}
        </h1>
      )}
      {subject && (
        <h2
          style={{
            marginBottom: "0.5rem",
            fontSize: "1.2rem",
            fontWeight: 500,
            color: "#444",
          }}
        >
          {subject.replace("Subject:", "").trim()}
        </h2>
      )}
      {date && (
        <div style={{ fontStyle: "italic", marginBottom: "1.5rem" }}>
          {date}
        </div>
      )}
      {greeting && (
        <div style={{ marginBottom: "1rem", fontWeight: 500 }}>{greeting}</div>
      )}
      {paragraphs.map((p, idx) => (
        <p key={idx} style={{ marginBottom: "1rem", lineHeight: 1.6 }}>
          {p}
        </p>
      ))}
      {listItems.length > 0 && (
        <ul style={{ marginBottom: "1.5rem", paddingLeft: "1.5rem" }}>
          {listItems.map((li, idx) => (
            <li key={idx} style={{ marginBottom: "0.5rem" }}>
              {li.substring(2)}
            </li>
          ))}
        </ul>
      )}
      {closing.length > 0 && (
        <div style={{ marginTop: "2rem" }}>
          {closing.map((c, idx) => (
            <div key={idx} style={{ marginBottom: "0.25rem" }}>
              {c}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Report;
