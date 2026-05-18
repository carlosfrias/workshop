---
title: Trading Lab Architecture
description: Multi-node orchestration design and deployment patterns
---

# Trading Lab Architecture

**Type:** Design Document  
**Status:** Reference architecture for the 7-node lab

Multi-node orchestration design encompassing hardware specification, network topology, deployment pipeline, and operational playbooks for the pi agent harness across a cluster of Apple Silicon Macs.

## Scope

- Hardware sizing and node assignments
- Network topology (VPN, PXE, DHCP)
- Ollama model depot and sync strategy
- Ansible playbook design patterns
- Cross-node communication (intercom, Gist MQ)
- Disaster recovery and offline operation

## Location

Design documents live in the workspace:

```
technical-infrastructure/designs/trading-lab-architecture/
```

This is **design work**, not a distribution package. It informs the packages that ARE distributed (local-model-pilot, pi-keyword-router, etc.).

## References

- [Multi-Node Setup Guide](/technical-infrastructure/guides/multi-node-setup-2026-04-26)
- [Node Capacity Map](/technical-infrastructure/reference/node-capacity-map)
- [WireGuard Lab VPN](/technical-infrastructure/guides/wireguard-lab-vpn)
