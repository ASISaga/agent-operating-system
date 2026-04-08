# agent-operating-system — MCP Routing and Foundry Orchestration for Boardroom

## Objective

Enable the Agent Operating System to route MCP app payloads from boardroom
workflows to connected clients via Server-Sent Events (SSE), manage
dual-mode sessions (structured workflows and dynamic discussions), and
orchestrate multi-agent conversations through the Foundry Agent Service.

## Context

The boardroom chat interface supports two modes:

1. **Structured workflow** — A workflow-owner agent conducts a step-by-step
   conversation with an external entity.  Steps come from YAML files.
2. **Dynamic discussion** — The full C-suite engages in purpose-driven debate.

Both modes use the same MCP transport and persist conversations through
`subconscious.asisaga.com`.

## Requirements

### 1. MCP App Payload Delivery

When a workflow calls `aos.mcp.send_app_payload()`, the AOS must:
- Wrap the payload in an `mcp_app` envelope with the specified `app_id`
- Deliver it to the correct client session via the existing SSE transport
- Support `app_id: "boardroom_ui"` for boardroom-specific rendering
- Route the payload to `subconscious.asisaga.com` for persistence

### 2. Navigation Command Routing

When the `<chatroom>` client sends text commands (e.g. `cmd:next`, `cmd:back`):
- Recognise the `cmd:` prefix as a workflow navigation command
- Extract the command type (`next`, `back`)
- Route the command to the active `workflow-orchestration` instance
- The workflow responds with the next/previous step's MCP app payload
- This applies to **any** registered workflow, not just the pitch

### 3. Dual-Mode Session Management

Support both structured and dynamic sessions concurrently:
- **Structured sessions**: Track `workflow_id`, `step_id`, and `owner` agent
- **Dynamic sessions**: Track participating CXO agents and debate state
- Both modes persist to `subconscious.asisaga.com`
- Session reconnection restores the correct mode and state

### 4. Workflow Step Resolution

When receiving a `GOTO_STEP` command, resolve the target step from the
workflow YAML and construct the MCP-compliant JSON payload containing:
- `narrative` — step narrative text
- `response` — agent response text
- `actions[]` — array of `{label, description, url}`
- `navigation` — `{next, back}` step IDs

### 5. Foundry Agent Service Integration

The multi-agent orchestration uses Foundry Agent Service:
- Start orchestrations for both structured workflows (single owner agent)
  and dynamic discussions (full C-suite)
- Route agent messages and MCP app payloads through the orchestration
- Support purpose-driven perpetual orchestrations

### 6. MCP App Payload Persistence Routing

Route all MCP app payloads (graphical UI elements) to
`subconscious.asisaga.com` alongside text messages:
- Both text and MCP app payloads are stored per session
- On reconnect, replay the full conversation including graphical elements

## Dependencies

- `aos-client-sdk` — SDK extensions for `send_app_payload()` API
- `subconscious.asisaga.com` — Session and conversation persistence layer

## References

→ **Backend prompt**: `docs/workflow/prompts/backend.md`
→ **Architecture**: `docs/workflow/Architecture.md`
→ **Communication protocol**: `docs/workflow/Communication.md`
→ **Workflow YAML samples**: `docs/workflow/samples/`
→ **Boardroom schema**: `docs/workflow/boardroom.yaml`
→ **Multi-repo roadmap**: `docs/multi-repository-implementation.md`