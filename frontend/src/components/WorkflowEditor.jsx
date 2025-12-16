import React, { useCallback, useState, useMemo, useEffect } from "react";
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import CustomNode from "./CustomNode";
import { fetchTemplates, saveWorkflow } from "../api/workflowApi";
// import axiosInstance from "./axiosInstance";

const nodeTypes = {
  customNode: CustomNode,
};

const initialNodes = [];
const initialEdges = [];

export default function WorkflowEditor() {
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);
  const [selectedNode, setSelectedNode] = useState(null);
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [nodeDetails, setNodeDetails] = useState({});
  const [templateList, setTemplateList] = useState([]);
  const [workflowName, setWorkflowName] = useState("");

  useEffect(() => {
    const loadTemplates = async () => {
      try {
        const data = await fetchTemplates();
        setTemplateList(data.templates);
      } catch (error) {
        console.error("Error Fetching Templates:", error);
      }
    };
    loadTemplates();
  }, []);

  const getOutgoingTargets = (nodeId) => {
    const outgoingEdges = edges.filter((e) => e.source === nodeId);
    return outgoingEdges.map((e) => e.target);
  };

  const tryParseJSON = (str) => {
    try {
      return JSON.parse(str);
    } catch (e) {
      return null;
    }
  };

  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );

  const onEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );

  const onConnect = useCallback(
    (connection) =>
      setEdges((eds) => addEdge({ ...connection, type: "smoothstep" }, eds)),
    []
  );

  const verticalGap = 150;

  const onAddNode = useCallback(
    (parentId) => {
      const newNodeId = `n${nodes.length + 1}`;

      setNodes((nds) => {
        const parentNode = nds.find((n) => n.id === parentId);
        if (!parentId) return nds;

        const shiftedNodes = nds.map((n) => {
          if (n.position.y > parentNode.position.y) {
            return {
              ...n,
              position: {
                ...n.position,
                y: n.position.y + verticalGap,
              },
            };
          }
          return n;
        });

        const newNode = {
          id: newNodeId,
          position: {
            x: parentNode.position.x,
            y: parentNode.position.y + verticalGap,
          },
          data: { label: `Node ${nds.length + 1}` },
          type: "customNode",
        };

        return [...shiftedNodes, newNode];
      });

      setEdges((eds) => {
        const existingChildEdge = eds.find((e) => e.source === parentId);

        if (!existingChildEdge) {
          return [
            ...eds,
            {
              id: `${parentId} - ${newNodeId}`,
              source: parentId,
              target: newNodeId,
              type: "smoothstep",
            },
          ];
        }

        const childId = existingChildEdge.target;

        const remaining = eds.filter((e) => e !== existingChildEdge);

        return [
          ...remaining,
          {
            id: `${parentId} - ${newNodeId}`,
            source: parentId,
            target: newNodeId,
            type: "smoothstep",
          },
          {
            id: `${newNodeId} - ${childId}`,
            source: newNodeId,
            target: childId,
            type: "smoothstep",
          },
        ];
      });
    },
    [nodes]
  );

  const onDeleteNode = useCallback(
    (nodeId) => {
      setNodes((nds) => {
        const nodeToDelete = nds.find((n) => n.id === nodeId);
        if (!nodeToDelete) return nds;

        const gapY = 150;

        const updatedNodes = nds
          .filter((n) => n.id !== nodeId)
          .map((n) => {
            if (n.position.y > nodeToDelete.position.y) {
              return {
                ...n,
                position: {
                  ...n.position,
                  y: n.position.y - gapY,
                },
              };
            }
            return n;
          });

        return updatedNodes;
      });
      setEdges((eds) => {
        const incoming = eds.filter((e) => e.target === nodeId);
        const outgoing = eds.filter((e) => e.source === nodeId);

        const remaining = eds.filter(
          (e) => e.source !== nodeId && e.target !== nodeId
        );

        const newEdges = [];

        incoming.forEach((inEdge) => {
          outgoing.forEach((outEdge) => {
            if (inEdge.source !== outEdge.target) {
              const id = `${inEdge.source} - ${outEdge.target}`;

              if (!remaining.some((e) => e.id === id)) {
                newEdges.push({
                  id,
                  source: inEdge.source,
                  target: outEdge.target,
                  type: "smoothstep",
                });
              }
            }
          });
        });

        return [...remaining, ...newEdges];
      });
      if (selectedNode?.id === nodeId) {
        setSelectedNode(null);
      }

      setNodeDetails((prev) => {
        const updated = { ...prev };
        delete updated[nodeId];
        return updated;
      });
    },
    [selectedNode]
  );

  const onLabelChange = useCallback((nodeId, newLabel) => {
    setNodes((nds) =>
      nds.map((n) =>
        n.id === nodeId ? { ...n, data: { ...n.data, label: newLabel } } : n
      )
    );
  }, []);

  const handleAddInitialNode = () => {
    const firstNode = {
      id: "n1",
      position: { x: 250, y: 250 },
      data: { label: "Start Node" },
      type: "customNode",
    };
    setNodes([firstNode]);
  };

  const handleNodeClick = (_, node) => {
    setSelectedNode(node);
    setIsPanelOpen(true);
  };

  const handleDetailsChange = (e) => {
    const { name, value } = e.target;

    if (!selectedNode) return;

    setNodeDetails((prev) => ({
      ...prev,
      [selectedNode.id]: { ...prev[selectedNode.id], [name]: value },
    }));
  };

  const handleTemplateSelect = (templateName) => {
    const template = templateList.find((t) => t.name === templateName);

    if (!template || !selectedNode) return;

    const payload = JSON.stringify(template.components || [], null, 2);

    setNodeDetails((prev) => ({
      ...prev,
      [selectedNode.id]: {
        ...prev[selectedNode.id],
        templateName,
        payload,
        params: template?.language?.code || "",
      },
    }));
  };

  const handleSave = async () => {
    if (!workflowName) {
      alert("Please neter workflow name");
      return;
    }

    const nodesPayload = nodes.map((n, idx) => {
      const details = nodeDetails[n.id] || {};
      const selectedTemplateName = details.templateName || null;
      const templateObj = templateList.find(
        (t) =>
          t.name === selectedTemplateName ||
          t.template_name === selectedTemplateName
      );

      const templateButtons = (
        templateObj?.components?.[0]?.components ||
        templateObj?.buttons ||
        templateObj?.template_params?.buttons ||
        []
      ).map((b, i) => {
        return {
          id: b.id || `btn_${selectedTemplateName || "t"}_${i}`,
          title:
            b.text || b.title || b.label || b?.payload || `Button ${i + 1}`,
        };
      });

      const outgoing = getOutgoingTargets(n.id);

      const buttons = templateButtons.map((btn, i) => ({
        id: btn.id,
        title: btn.title,
        next_node_client_id: outgoing[i] || null,
      }));

      return {
        client_node_id: n.id,
        label: n.data?.label || "",
        template_name: selectedTemplateName,
        template_payload: details.payload
          ? tryParseJSON(details.payload)
          : null,
        template_params: details.params || null,
        buttons,
        position: n.position,
        order: idx + 1,
      };
    });

    const payload = {
      workflow_name: workflowName,
      nodes: nodesPayload,
    };

    try {
      await saveWorkflow(payload);
      alert("workflow saved");

      // clear form
      setWorkflowName("");
      setNodes([]);
      setEdges([]);
      setNodeDetails({});
      setSelectedNode(null);
      setIsPanelOpen(false);
    } catch (err) {
      console.error(err);
      alert("Error saving workflow");
    }
  };

  return (
    <div style={{ height: "100vh", display: "flex" }}>
      {/* Left Slide Panel */}
      <div
        style={{
          width: isPanelOpen ? "300px" : "50px",
          transition: "width 0.3s ease",
          background: "#f4f4f4",
          padding: "10px",
          borderRight: "1px solid #ddd",
          overflow: "hidden",
        }}
      >
        {/* toggle button */}
        <button
          onClick={() => setIsPanelOpen(!isPanelOpen)}
          style={{
            width: "30px",
            height: "30px",
            marginBottom: "10px",
            cursor: "pointer",
          }}
        >
          {isPanelOpen ? "<<" : ">>"}
        </button>

        {/* panel content */}
        {isPanelOpen && (
          <div>
            {!selectedNode ? (
              <p>Select a node</p>
            ) : (
              <>
                <h4>Node Details</h4>
                <p>
                  <strong>ID:</strong> {selectedNode.id}
                </p>

                <label>
                  Template Name:
                  <select
                    type="text"
                    name="templateName"
                    value={nodeDetails[selectedNode.id]?.templateName || ""}
                    onChange={(e) => handleTemplateSelect(e.target.value)}
                    style={{ width: "100%", marginBottom: "10px" }}
                  >
                    <option value="">Select Template</option>
                    {templateList.map((tpl) => (
                      <option key={tpl.name} value={tpl.name}>
                        {" "}
                        {tpl.name}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Payload:
                  <textarea
                    name="payload"
                    value={nodeDetails[selectedNode.id]?.payload || ""}
                    onChange={handleDetailsChange}
                    style={{
                      width: "100%",
                      height: "60px",
                      marginBottom: "10px",
                    }}
                  />
                </label>

                <label>
                  params:
                  <input
                    type="text"
                    name="params"
                    value={nodeDetails[selectedNode.id]?.params || ""}
                    onChange={handleDetailsChange}
                    style={{ width: "100%" }}
                  />
                </label>
              </>
            )}
          </div>
        )}
      </div>

      {/* Workflow Area */}
      <div style={{ flex: 1, position: "relative" }}>
        <div
          style={{
            padding: "10px",
            display: "flex",
            gap: "10px",
            alignItems: "center",
          }}
        >
          <input
            placeeholder="Workflow Name"
            value={workflowName}
            onChange={(e) => setWorkflowName(e.target.value)}
            style={{ padding: "6px", minWidth: 220 }}
          />
          {nodes.length === 0 ? (
            <button onClick={handleAddInitialNode}>Add A Node</button>
          ) : (
            <button onClick={handleSave}>Save Workflow</button>
          )}
        </div>

        <ReactFlow
          nodes={nodes.map((node) => ({
            ...node,
            data: {
              ...node.data,
              onAddNode,
              onDeleteNode,
              onLabelChange,
              selectedNode,
              onSelect: () => setSelectedNode(node),
              selected: selectedNode?.id === node.id,
            },
          }))}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onPaneClick={() => {
            setSelectedNode(null);
            setIsPanelOpen(false);
          }}
          onNodeClick={handleNodeClick}
          nodeTypes={nodeTypes}
          fitView
        >
          <MiniMap />
          <Controls />
          <Background />
        </ReactFlow>
      </div>
    </div>
  );
}
