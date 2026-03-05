import { useState } from "react";

const formatMarkdown = (text: string): string => {
  return text
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/\n/g, "<br />");
};

interface SourceInfo {
  kb: string;
  title: string;
  filepath: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  agent?: string;
  sources?: SourceInfo[];
}

type WorkflowStep =
  | "idle"
  | "routing"
  | "customer_service"
  | "operations"
  | "loyalty"
  | "complete";

type NodeId =
  | "input"
  | "orchestrator"
  | "customer_service"
  | "operations"
  | "loyalty"
  | "complete"
  | "idle";

interface TraceLog {
  timestamp: string;
  type: "route" | "query" | "source" | "response";
  message: string;
}

interface AgentInfo {
  id: string;
  name: string;
  icon: string;
  description: string;
  model: string;
  connectedKB: string | null;
  knowledgeSources: string[];
}

interface KBInfo {
  id: string;
  name: string;
  icon: string;
  description: string;
  retrievalMode: string;
  model: string;
  knowledgeSources: string[];
}

const agents: AgentInfo[] = [
  {
    id: "orchestrator",
    name: "Orchestrator",
    icon: "🎯",
    description:
      "Routes passenger queries to the appropriate specialist agent based on intent analysis. Uses GPT-4.1 for intelligent routing decisions.",
    model: "gpt-4.1",
    connectedKB: null,
    knowledgeSources: [],
  },
  {
    id: "customer_service",
    name: "Customer Service Agent",
    icon: "✈️",
    description:
      "Handles all passenger-facing interactions: rebooking, refunds, complaints, baggage issues, seat upgrades, and travel assistance.",
    model: "gpt-4.1",
    connectedKB: "kb1-customer-service",
    knowledgeSources: ["ks-cs-aisearch", "ks-cs-web", "ks-cs-sharepoint"],
  },
  {
    id: "operations",
    name: "Operations Agent",
    icon: "🛫",
    description:
      "Manages flight operations, disruptions, crew scheduling, and provides real-time geo-political situation awareness via Bing Search.",
    model: "gpt-4.1",
    connectedKB: "kb2-operations",
    knowledgeSources: ["ks-ops-aisearch", "ks-ops-web", "ks-geopolitical-bing"],
  },
  {
    id: "loyalty",
    name: "Loyalty Agent",
    icon: "🏆",
    description:
      "Expert on SkyRewards frequent flyer program: miles, tier status, lounge access, partner benefits, and reward redemption.",
    model: "gpt-4.1",
    connectedKB: "kb3-loyalty",
    knowledgeSources: ["ks-loyalty-aisearch", "ks-loyalty-web"],
  },
];

const knowledgeBases: KBInfo[] = [
  {
    id: "kb1-customer-service",
    name: "Customer Service KB",
    icon: "📋",
    description:
      "Rebooking policies, refund guidelines, baggage rules, compensation procedures, and travel document requirements.",
    retrievalMode: "Agentic Retrieval",
    model: "text-embedding-3-large",
    knowledgeSources: ["ks-cs-aisearch", "ks-cs-web", "ks-cs-sharepoint"],
  },
  {
    id: "kb2-operations",
    name: "Operations KB",
    icon: "🗺️",
    description:
      "Flight operations manual, disruption playbook, NOTAM data, and real-time geo-political intelligence via Bing Search.",
    retrievalMode: "Agentic Retrieval",
    model: "text-embedding-3-large",
    knowledgeSources: ["ks-ops-aisearch", "ks-ops-web", "ks-geopolitical-bing"],
  },
  {
    id: "kb3-loyalty",
    name: "Loyalty KB",
    icon: "⭐",
    description:
      "SkyRewards program guide, tier benefits, miles earning/redemption catalog, and partner airline agreements.",
    retrievalMode: "Agentic Retrieval",
    model: "text-embedding-3-large",
    knowledgeSources: ["ks-loyalty-aisearch", "ks-loyalty-web"],
  },
];

const sourceLogos: Record<string, string> = {
  "customer_service-agent": "✈️",
  "operations-agent": "🛫",
  "loyalty-agent": "🏆",
  "kb1-customer-service": "📋",
  "kb2-operations": "🗺️",
  "kb3-loyalty": "⭐",
};

const predefinedQuestions = [
  {
    text: "I need to rebook my London to Dubai flight due to a travel advisory",
    agent: "Customer Service",
  },
  {
    text: "What is the current geo-political impact on Eastern European flight routes?",
    agent: "Operations",
  },
  {
    text: "How many miles do I need to upgrade to Gold tier in SkyRewards?",
    agent: "Loyalty",
  },
];

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [workflowStep, setWorkflowStep] = useState<WorkflowStep>("idle");
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [traceLogs, setTraceLogs] = useState<TraceLog[]>([]);
  const [activeTab, setActiveTab] = useState<"agents" | "kbs">("agents");

  const addLog = (type: TraceLog["type"], message: string) => {
    setTraceLogs((prev) => [
      ...prev,
      {
        timestamp: new Date().toLocaleTimeString(),
        type,
        message,
      },
    ]);
  };

  const getNodeStatus = (
    nodeId: NodeId
  ): "active" | "complete" | "waiting" | "" => {
    if (workflowStep === "idle") return "";
    if (workflowStep === "routing") {
      if (nodeId === "input") return "complete";
      if (nodeId === "orchestrator") return "active";
      return "waiting";
    }
    if (
      workflowStep === "customer_service" ||
      workflowStep === "operations" ||
      workflowStep === "loyalty"
    ) {
      if (nodeId === "input" || nodeId === "orchestrator") return "complete";
      if (nodeId === workflowStep) return "active";
      return "waiting";
    }
    if (workflowStep === "complete") {
      if (
        nodeId === "input" ||
        nodeId === "orchestrator" ||
        nodeId === "complete"
      )
        return "complete";
      if (
        nodeId === "customer_service" ||
        nodeId === "operations" ||
        nodeId === "loyalty"
      ) {
        const agentType = activeAgent?.replace("-agent", "") || "";
        return nodeId === agentType ? "complete" : "waiting";
      }
    }
    return "";
  };

  const sendMessage = async (text: string) => {
    if (!text.trim()) return;

    const userMsg: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);
    setWorkflowStep("routing");
    setTraceLogs([]);

    addLog("route", "Orchestrator analyzing passenger intent...");

    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      const data = await response.json();

      // Set workflow step based on agent
      const agentType = data.agent?.replace("-agent", "") || "customer_service";
      setWorkflowStep(agentType as WorkflowStep);
      setActiveAgent(data.agent || null);

      const kbMap: Record<string, string> = {
        customer_service: "kb1-customer-service",
        operations: "kb2-operations",
        loyalty: "kb3-loyalty",
      };
      addLog("route", `Routed to ${data.agent || "specialist"}`);
      addLog(
        "query",
        `${data.agent} querying ${kbMap[agentType]} via agentic retrieval...`
      );

      // Log retrieved documents
      const sources = data.sources as SourceInfo[];
      if (sources?.length > 0) {
        sources.forEach((src) => {
          addLog("source", `Retrieved: ${src.title} (${src.kb})`);
        });
      }

      addLog("response", "Response generated with grounded citations");

      setTimeout(() => {
        setWorkflowStep("complete");
      }, 500);

      const assistantMsg: Message = {
        role: "assistant",
        content: data.message,
        agent: data.agent,
        sources: sources,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (error) {
      const errMsg: Message = {
        role: "assistant",
        content: `Error: ${error instanceof Error ? error.message : "Unknown error"}`,
      };
      setMessages((prev) => [...prev, errMsg]);
      setWorkflowStep("idle");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-logo">
          <span className="logo-icon">✈️</span>
          <div>
            <h1>Zava Airlines</h1>
            <span className="header-subtitle">
              FoundryIQ + Agent Framework Demo
            </span>
          </div>
        </div>
        <div className="header-badges">
          <span className="badge badge-blue">Microsoft Agent Framework</span>
          <span className="badge badge-purple">FoundryIQ</span>
          <span className="badge badge-green">Bing Geo-Political Intel</span>
        </div>
      </header>

      <div className="main-content">
        {/* Left Panel: Workflow Canvas */}
        <div className="panel workflow-panel">
          <h2 className="panel-title">Agent Workflow Canvas</h2>

          <div className="workflow-canvas">
            {/* Input Node */}
            <div
              className={`workflow-node input-node ${getNodeStatus("input")}`}
            >
              <div className="node-status"></div>
              <div className="node-content">
                <span className="node-title">Passenger Query</span>
              </div>
            </div>

            <div className="workflow-arrow">↓</div>

            {/* Orchestrator Node */}
            <div
              className={`workflow-node orchestrator-node ${getNodeStatus("orchestrator")}`}
            >
              <div className="node-status"></div>
              <div className="node-content">
                <span className="node-title">🎯 Orchestrator</span>
                <span className="node-model">gpt-4.1</span>
              </div>
            </div>

            <div className="workflow-arrow">↓</div>

            {/* Agent Nodes */}
            <div className="agent-row">
              <div
                className={`workflow-node agent-node customer-service ${getNodeStatus("customer_service")}`}
              >
                <div className="node-status"></div>
                <div className="node-content">
                  <span className="node-title">✈️ Customer Service</span>
                </div>
                <div className="node-kb">
                  <span className="kb-badge">kb1-customer-service</span>
                </div>
              </div>

              <div
                className={`workflow-node agent-node operations ${getNodeStatus("operations")}`}
              >
                <div className="node-status"></div>
                <div className="node-content">
                  <span className="node-title">🛫 Operations</span>
                </div>
                <div className="node-kb">
                  <span className="kb-badge">kb2-operations</span>
                </div>
              </div>

              <div
                className={`workflow-node agent-node loyalty ${getNodeStatus("loyalty")}`}
              >
                <div className="node-status"></div>
                <div className="node-content">
                  <span className="node-title">🏆 Loyalty</span>
                </div>
                <div className="node-kb">
                  <span className="kb-badge">kb3-loyalty</span>
                </div>
              </div>
            </div>
          </div>

          {/* Trace Logs */}
          <div className="trace-panel">
            <h3 className="trace-title">Trace Log</h3>
            <div className="trace-logs">
              {traceLogs.length === 0 ? (
                <div className="trace-empty">
                  Ask a question to see the agent workflow...
                </div>
              ) : (
                traceLogs.map((log, idx) => (
                  <div key={idx} className={`trace-entry trace-${log.type}`}>
                    <span className="trace-time">{log.timestamp}</span>
                    <span className="trace-type">{log.type.toUpperCase()}</span>
                    <span className="trace-msg">{log.message}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Center Panel: Chat */}
        <div className="panel chat-panel">
          <h2 className="panel-title">Passenger Interaction</h2>

          {/* Predefined Questions */}
          <div className="quick-questions">
            {predefinedQuestions.map((q, idx) => (
              <button
                key={idx}
                className="quick-btn"
                onClick={() => sendMessage(q.text)}
                disabled={isLoading}
              >
                <span className="quick-agent">{q.agent}</span>
                <span className="quick-text">{q.text}</span>
              </button>
            ))}
          </div>

          {/* Messages */}
          <div className="messages-container">
            {messages.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon">✈️</div>
                <h3>Welcome to Zava Airlines</h3>
                <p>
                  Ask about rebooking, flight operations, geo-political impacts,
                  or the SkyRewards loyalty program.
                </p>
              </div>
            )}
            {messages.map((msg, idx) => (
              <div key={idx} className={`message message-${msg.role}`}>
                <div className="message-header">
                  {msg.role === "assistant" && msg.agent && (
                    <span className="agent-badge">
                      {sourceLogos[msg.agent] || "🤖"}{" "}
                      {msg.agent.replace("-agent", "").replace("_", " ")}
                    </span>
                  )}
                </div>
                <div
                  className="message-content"
                  dangerouslySetInnerHTML={{
                    __html: formatMarkdown(msg.content),
                  }}
                />
                {msg.agent && (
                  <div className="message-sources">
                    <span className="source-label">Sources:</span>
                    <div className="source-list">
                      {msg.sources && msg.sources.length > 0 ? (
                        msg.sources.map((src, srcIdx) => (
                          <span key={srcIdx} className="source-doc">
                            <span className="source-doc-title">
                              {src.title || src.filepath || "Document"}
                            </span>
                            <span className="source-doc-kb">({src.kb})</span>
                          </span>
                        ))
                      ) : (
                        <span className="source-name">
                          {msg.agent.replace("-agent", "") ===
                          "customer_service"
                            ? "kb1-customer-service"
                            : msg.agent.replace("-agent", "") === "operations"
                              ? "kb2-operations"
                              : "kb3-loyalty"}
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="message message-assistant loading">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="chat-input-container">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage(input)}
              placeholder="Ask about flights, rebooking, loyalty miles, or geo-political impacts..."
              disabled={isLoading}
              className="chat-input"
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={isLoading || !input.trim()}
              className="send-btn"
            >
              Send
            </button>
          </div>
        </div>

        {/* Right Panel: Agent & KB Info */}
        <div className="panel info-panel">
          <div className="tab-header">
            <button
              className={`tab-btn ${activeTab === "agents" ? "active" : ""}`}
              onClick={() => setActiveTab("agents")}
            >
              Agents
            </button>
            <button
              className={`tab-btn ${activeTab === "kbs" ? "active" : ""}`}
              onClick={() => setActiveTab("kbs")}
            >
              Knowledge Bases
            </button>
          </div>

          <div className="info-cards">
            {activeTab === "agents"
              ? agents.map((agent) => (
                  <div
                    key={agent.id}
                    className={`info-card ${activeAgent === `${agent.id}-agent` ? "active-card" : ""}`}
                  >
                    <div className="card-header">
                      <span className="card-icon">{agent.icon}</span>
                      <span className="card-name">{agent.name}</span>
                    </div>
                    <p className="card-desc">{agent.description}</p>
                    <div className="card-meta">
                      <span className="meta-badge">🧠 {agent.model}</span>
                      {agent.connectedKB && (
                        <span className="meta-badge">
                          📚 {agent.connectedKB}
                        </span>
                      )}
                    </div>
                    {agent.knowledgeSources.length > 0 && (
                      <div className="card-sources">
                        {agent.knowledgeSources.map((ks, idx) => (
                          <span key={idx} className="ks-badge">
                            {ks}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              : knowledgeBases.map((kb) => (
                  <div key={kb.id} className="info-card">
                    <div className="card-header">
                      <span className="card-icon">{kb.icon}</span>
                      <span className="card-name">{kb.name}</span>
                    </div>
                    <p className="card-desc">{kb.description}</p>
                    <div className="card-meta">
                      <span className="meta-badge">
                        🔍 {kb.retrievalMode}
                      </span>
                      <span className="meta-badge">📐 {kb.model}</span>
                    </div>
                    <div className="card-sources">
                      {kb.knowledgeSources.map((ks, idx) => (
                        <span key={idx} className="ks-badge">
                          {ks}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
