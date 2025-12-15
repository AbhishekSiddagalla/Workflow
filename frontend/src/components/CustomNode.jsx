import React from "react";
import { Handle, Position } from "@xyflow/react";

export default function CustomNode({ id, data }) {
  const { onAddNode, onDeleteNode, onLabelChange, onSelect, selected } = data;
  return (
    <div
      onClick={onSelect}
      style={{
        border: selected ? "2px solid #1976d2" : "1px solid #999",
        borderRadius: "8px",
        padding: "8px",
        background: "#fff",
        width: 130,
        textAlign: "center",
        boxShadow: selected ? "0px 0px 0px rgba(25,118,210,0.4)" : "none",
      }}
    >
      <Handle type="target" position={Position.Top} />
      <input
        type="text"
        value={data.label}
        onChange={(e) => onLabelChange(id, e.target.value)}
        style={{
          width: "100%",
          border: "none",
          textAlign: "center",
          background: "transparent",
          outline: "none",
          fontWeight: "bold",
        }}
      />

      {selected && (
        <div style={{ marginTop: "4px" }}>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onAddNode(id);
            }}
            style={{
              background: "#4caf50",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              padding: "2px 6px",
              fontSize: "10px",
              marginRight: "4px",
            }}
          >
            +
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDeleteNode(id);
            }}
            style={{
              background: "#f44336",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              padding: "2px 6px",
              fontSize: "10px",
            }}
          >
            -
          </button>
        </div>
      )}
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
