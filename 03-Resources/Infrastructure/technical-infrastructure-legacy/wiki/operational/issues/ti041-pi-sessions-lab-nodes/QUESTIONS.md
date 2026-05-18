# TI-041 Open Questions

## Q1: Installation Method
Should pi be installed via npm (`npm install -g @earendil-works/pi-coding-agent`) or as a standalone binary download? npm requires Node.js on each lab node.

## Q2: Persistence Mechanism
Should pi sessions run under systemd (auto-restart on crash) or under tmux/screen (manual restart)? systemd is more robust but requires root/sudo access.

## Q3: Intercom Broker Location
Does the intercom broker run on the orchestrator node (Mac) and accept connections from lab nodes, or should each lab node run its own broker? Same-machine assumption may need broker config changes.

## Q4: Model Selection on Lab Nodes
Lab nodes run local models (qwen3.5:4b, qwen3:8b, gemma4:e4b). Should the lab node pi session be configured to use local models by default, or should the orchestrator specify the model per task?

## Q5: Session Naming Convention
Should lab node sessions be named `fnet1-worker`, `fnet2-worker`, etc., or should they use role-based names (`worker-high`, `worker-low`)?

## Q6: Security
Should lab node pi sessions be restricted to read-only workspace access, or can they write to the mounted workspace? Full write access matches current SSH behavior.

## Q7: Fallback Strategy
If the pi session on a lab node crashes, should the orchestrator auto-fallback to SSH dispatch, or should it mark the node offline and redistribute work?

## Q8: Resource Overhead
Running pi on each lab node consumes RAM (~500MB–1GB per session). Should we limit pi to high-RAM nodes (fnet3–fnet6, 31GB) only, or run on all 7 nodes?
