---
title: gist-message-queue
description: Async agent-to-agent communication via GitHub Gist
---

# gist-message-queue

**Type:** Skill  
**Install:** `pi install github:carlosfrias/gist-message-queue`

Asynchronous agent-to-agent communication using GitHub Gist as a persistent message queue.

## Commands

| Command | Purpose |
|---------|---------|
| `gist-mq init <gist-id>` | Initialize message queue |
| `gist-mq send <type> <file>` | Send message to queue |
| `gist-mq recv <type>` | Receive message from queue |
| `gist-mq status` | Show queue status |
| `gist-mq log` | Show message log |
| `gist-mq check <type>` | Check if message exists |
| `gist-mq clear` | Clear local cache |

## Use Cases

| Scenario | Why Gist MQ |
|----------|-------------|
| **Multi-node troubleshooting** | Node agents report to orchestrator autonomously |
| **Cross-session coordination** | Sessions on different machines communicate async |
| **Offline-capable workflows** | Agents work offline, sync when connected |
| **Audit trail** | All messages preserved in Gist history |

## Prerequisites

- GitHub account
- GitHub CLI (`gh`) installed and authenticated

## Repository

[github.com/carlosfrias/gist-message-queue](https://github.com/carlosfrias/gist-message-queue)
