export default function ArchitectureDiagram() {
  return (
    <svg
      viewBox="0 0 860 420"
      className="arch-diagram"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label="TACO architecture diagram showing agent zones connected through the TACO shared layer">
      {/* Top agent zones */}
      <g>
        {/* Preconstruction */}
        <rect x="20" y="20" width="250" height="110" rx="6" fill="#8B5CF6" />
        <text x="145" y="48" textAnchor="middle" className="zone-label">
          Preconstruction
        </text>
        <rect x="35" y="60" width="100" height="28" rx="4" fill="rgba(255,255,255,0.2)" />
        <text x="85" y="79" textAnchor="middle" className="agent-label">
          Takeoff Agent
        </text>
        <rect x="150" y="60" width="105" height="28" rx="4" fill="rgba(255,255,255,0.2)" />
        <text x="202" y="79" textAnchor="middle" className="agent-label">
          Estimating Agent
        </text>
        <rect x="35" y="96" width="220" height="24" rx="4" fill="rgba(255,255,255,0.15)" />
        <text x="145" y="113" textAnchor="middle" style={{fontSize: '9px', fill: 'rgba(255,255,255,0.8)'}}>
          bid-leveling | value-engineering | scope-review
        </text>

        {/* Document Management */}
        <rect x="305" y="20" width="250" height="110" rx="6" fill="#3B82F6" />
        <text x="430" y="48" textAnchor="middle" className="zone-label">
          Document Management
        </text>
        <rect x="320" y="60" width="100" height="28" rx="4" fill="rgba(255,255,255,0.2)" />
        <text x="370" y="79" textAnchor="middle" className="agent-label">
          RFI Agent
        </text>
        <rect x="435" y="60" width="105" height="28" rx="4" fill="rgba(255,255,255,0.2)" />
        <text x="487" y="79" textAnchor="middle" className="agent-label">
          Submittal Agent
        </text>
        <rect x="320" y="96" width="220" height="24" rx="4" fill="rgba(255,255,255,0.15)" />
        <text x="430" y="113" textAnchor="middle" style={{fontSize: '9px', fill: 'rgba(255,255,255,0.8)'}}>
          spec-compliance | change-order | drawing-markup
        </text>

        {/* Field + Coordination */}
        <rect x="590" y="20" width="250" height="110" rx="6" fill="#22C55E" />
        <text x="715" y="48" textAnchor="middle" className="zone-label">
          Field + Coordination
        </text>
        <rect x="605" y="60" width="105" height="28" rx="4" fill="rgba(255,255,255,0.2)" />
        <text x="657" y="79" textAnchor="middle" className="agent-label">
          Schedule Agent
        </text>
        <rect x="720" y="60" width="105" height="28" rx="4" fill="rgba(255,255,255,0.2)" />
        <text x="772" y="79" textAnchor="middle" className="agent-label">
          Safety Agent
        </text>
        <rect x="605" y="96" width="220" height="24" rx="4" fill="rgba(255,255,255,0.15)" />
        <text x="715" y="113" textAnchor="middle" style={{fontSize: '9px', fill: 'rgba(255,255,255,0.8)'}}>
          clash-detection | progress-tracking | punch-list
        </text>
      </g>

      {/* Schema labels above TACO bar */}
      <text x="145" y="158" textAnchor="middle" className="schema-label">
        bom-v1 | estimate-v1
      </text>
      <text x="430" y="158" textAnchor="middle" className="schema-label">
        rfi-v1 | change-order-v1
      </text>
      <text x="715" y="158" textAnchor="middle" className="schema-label">
        schedule-v1
      </text>

      {/* Connection lines top */}
      <line x1="145" y1="130" x2="145" y2="170" stroke="#d1d5db" strokeWidth="1.5" strokeDasharray="4,3" />
      <line x1="430" y1="130" x2="430" y2="170" stroke="#d1d5db" strokeWidth="1.5" strokeDasharray="4,3" />
      <line x1="715" y1="130" x2="715" y2="170" stroke="#d1d5db" strokeWidth="1.5" strokeDasharray="4,3" />

      {/* TACO central bar */}
      <rect x="20" y="170" width="820" height="60" rx="6" fill="#EAB308" />
      <text x="430" y="198" textAnchor="middle" className="taco-bar-text">
        TACO — Shared Task Types, Data Schemas, Agent Discovery
      </text>
      <text x="430" y="218" textAnchor="middle" style={{fontSize: '10px', fill: 'rgba(0,0,0,0.5)'}}>
        Every TACO agent is a standard A2A agent
      </text>

      {/* Connection lines bottom */}
      <line x1="145" y1="230" x2="145" y2="270" stroke="#d1d5db" strokeWidth="1.5" strokeDasharray="4,3" />
      <line x1="430" y1="230" x2="430" y2="270" stroke="#d1d5db" strokeWidth="1.5" strokeDasharray="4,3" />
      <line x1="715" y1="230" x2="715" y2="270" stroke="#d1d5db" strokeWidth="1.5" strokeDasharray="4,3" />

      {/* Schema labels below TACO bar */}
      <text x="145" y="265" textAnchor="middle" className="schema-label">
        quote-v1
      </text>
      <text x="430" y="265" textAnchor="middle" className="schema-label">
        OAuth scopes | trust tiers
      </text>
      <text x="715" y="265" textAnchor="middle" className="schema-label">
        Agent Cards
      </text>

      {/* Bottom agent zones */}
      <g>
        {/* Supply Chain */}
        <rect x="20" y="280" width="250" height="80" rx="6" fill="#F59E0B" />
        <text x="145" y="308" textAnchor="middle" className="zone-label">
          Supply Chain
        </text>
        <rect x="35" y="318" width="105" height="28" rx="4" fill="rgba(255,255,255,0.25)" />
        <text x="87" y="337" textAnchor="middle" className="agent-label">
          Supplier Agent
        </text>
        <rect x="150" y="318" width="105" height="28" rx="4" fill="rgba(255,255,255,0.25)" />
        <text x="202" y="337" textAnchor="middle" className="agent-label">
          Logistics Agent
        </text>

        {/* External Parties */}
        <rect x="305" y="280" width="250" height="80" rx="6" fill="#EF4444" />
        <text x="430" y="308" textAnchor="middle" className="zone-label">
          External Parties
        </text>
        <rect x="320" y="318" width="105" height="28" rx="4" fill="rgba(255,255,255,0.2)" />
        <text x="372" y="337" textAnchor="middle" className="agent-label">
          Architect Agent
        </text>
        <rect x="435" y="318" width="105" height="28" rx="4" fill="rgba(255,255,255,0.2)" />
        <text x="487" y="337" textAnchor="middle" className="agent-label">
          Engineer Agent
        </text>

        {/* Orchestration */}
        <rect x="590" y="280" width="250" height="80" rx="6" fill="#06B6D4" />
        <text x="715" y="308" textAnchor="middle" className="zone-label">
          Orchestration
        </text>
        <rect x="605" y="318" width="220" height="28" rx="4" fill="rgba(255,255,255,0.2)" />
        <text x="715" y="337" textAnchor="middle" className="agent-label">
          GC Orchestrator / Agent Registry
        </text>
      </g>

      {/* Agent Registry bar at bottom */}
      <rect x="20" y="385" width="820" height="28" rx="4" fill="#f3f4f6" stroke="#d1d5db" />
      <text x="430" y="404" textAnchor="middle" style={{fontSize: '11px', fontWeight: 500, fill: '#6B7280'}}>
        TACO Agent Registry — discover agents by trade, CSI division, task type, and platform
      </text>
    </svg>
  );
}
