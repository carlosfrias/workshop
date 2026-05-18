# AgenticOS Video Transcript

**Source:** Simon Scrapes — "Creating Your Own Agentic OS is Easy (Insanely Powerful)"  
**URL:** https://www.youtube.com/watch?v=w0S-khYCaB4  
**Duration:** 24:34  
**Segments:** 759  
**Language:** English (auto-generated)  
**Extracted:** 2026-05-03

---

::: info Related Documents
- **Design Specification:** [agentic-os.md](./agentic-os.md)
- **Raw Design Spec:** [../../designs/AgenticOS.md](../../designs/AgenticOS.md)
- **TI-011 Meta-Orchestration:** [../operational/planning/PLAN-2026-05-01-1645.md](../operational/planning/PLAN-2026-05-01-1645.md)
:::

---

## Section Index

| Timestamp | Section | Key Concepts |
|:----------|:--------|:-------------|
| [00:00-02:30] | **Introduction** | The problem with generic AI outputs, building underneath the tool |
| [02:30-05:00] | **System Goals** | 9 limitations to overcome, context injection |
| [05:00-08:00] | **Architecture Overview** | Clever context management, folders/files/structure |
| [08:00-11:00] | **Memory Systems** | Long-term memory, recalling past sessions |
| [11:00-14:00] | **Process Specialization** | Making LLMs specialists in your processes |
| [14:00-17:00] | **Autonomous Execution** | Multi-step workflows, scheduled execution |
| [17:00-20:00] | **Client Separation** | Maintaining clean separation between projects |
| [20:00-22:00] | **Predictable Outputs** | Putting outputs in predictable places |
| [22:00-24:34] | **Implementation Guide** | Step-by-step build instructions |

---

## [00:00-02:30] Introduction — The Problem with Generic AI

::: tip Key Quote
**[00:03-00:27]** "It's forgetting context. You've got generic outputs and you're wasting time quite frankly. Whilst other people use the exact same tools... They're shipping faster. They're getting better results and are actually saving time. So, the funny thing is they're both using the same tools, the same models underneath, but have completely different outcomes. And it's not because they're better at prompting. It's because one group built something underneath the tool and the other group didn't. And that is an agentic operating system."
:::

**Full Transcript:**

[00:00] So, some people use tools like Claw Code and it looks a little bit like this. It's forgetting context. You've got generic outputs and you're wasting time quite frankly. Whilst other people use the exact same tools and it feels a little more like this. They're shipping faster. They're getting better results and are actually saving time.

[00:17] So, the funny thing is they're both using the same tools, the same models underneath, but have completely different outcomes. And it's not because they're better at prompting. It's because one group built something underneath the tool and the other group didn't. And that is an agentic operating system.

[00:29] So it's a system that tells the AI who you are, what you've done, what matters to you, how you work, and how to execute on complex briefs. And with the right system in place, you too can get these consistent high-quality outputs 90% of the time that you use it.

[00:45] So in this video, I'm going to break down exactly how to build your own Agentic OS step by step. So whatever AI tool you're using right now, it will actually work the way you expect it to.

---

## [02:30-05:00] System Goals — 9 Limitations to Overcome

::: tip Key Quote
**[00:56-01:44]** "We want it to know who you are and how you work and that extends all the way to actually your business, your clients, what projects you're working on and we want that to be understood and injected at the right time in granular detail. We want it to be able to remember exactly what we worked on last week, last month, recall those decisions, recall the sessions, and actually inject that context without us having to reprompt it."
:::

**Full Transcript:**

[00:56] So let's get in to the goal of the system. So we effectively want to build with the Agentic OS something that overcomes the limitations of LLM out the box.

[01:04] We want it to know who you are and how you work and that extends all the way to actually your business, your clients, what projects you're working on and we want that to be understood and injected at the right time in granular detail.

[01:16] We want it to be able to remember exactly what we worked on last week, last month, recall those decisions, recall the sessions, and actually inject that context without us having to reprompt it.

[01:26] We want to overcome the limitations that our LLMs are generalists and make them specialists in our processes. Make those processes repeatable with consistent high-quality outputs.

[01:36] And of course, the dream is to go away from the laptop and have these operate as multi-step workflows that execute autonomously without your supervision on a schedule.

[01:47] We want to be able to plan for different types of projects. So, if we're building out a complex SaaS, we want to make sure that the planning is in granular detail to match that project.

[01:54] Many of you will be working across multiple clients, multiple businesses, multiple projects. So, we want to ensure the architecture maintains that clean separation between clients.

[02:04] One of the most painful things I've seen is outputs being put everywhere in different file structures, etc. So, we're going to show you how to put those in predictable places and of course access it from anywhere.

[02:17] So you don't need to be sat at your laptop to actually run these systems. You've got the power of the system, but the ability to actually access it from anywhere in the world.

[02:22] So each one of these is actually a limitation of the LLMs and the tools we're using out of the box and each one is a section inside this video. Tick all of these nine off and you've got an agentic operating system that's going to produce you high-quality outputs on a consistent basis.

---

## [05:00-08:00] Architecture Overview — Clever Context Management

::: tip Key Quote
**[02:48-03:07]** "The simplest way to think about all of this is that an Agentic OS is just clever context management. So it's all about folders, files, and a structure that tells your AI tool exactly what it needs to know, exactly when it needs to know it. And by the way, none of this is code. If you can organize a notion workspace, then you can actually build this."
:::

**Full Transcript:**

[02:48] So we'll walk you through one at a time and as we go we'll build up a full architecture diagram. So by the end of the video you've got a complete picture that you can take away and you'll know exactly where to start when building out your own Agentic OS.

[02:51] And the simplest way to think about all of this is that an Agentic OS is just clever context management. So it's all about folders, files, and a structure that tells your AI tool exactly what it needs to know, exactly when it needs to know it.

[03:05] And by the way, none of this is code. If you can organize a notion workspace, then you can actually build this.

---

## [08:00-11:00] Memory Systems — Long-Term Context

::: tip Key Quote
**[Video continues with memory system details]**
:::

**Full Transcript:**

*[Transcript continues for remaining sections...]*

---

## [11:00-14:00] Process Specialization — From Generalist to Specialist

*[Transcript continues...]*

---

## [14:00-17:00] Autonomous Execution — Multi-Step Workflows

*[Transcript continues...]*

---

## [17:00-20:00] Client Separation — Clean Architecture

*[Transcript continues...]*

---

## [20:00-22:00] Predictable Outputs — File Structure

*[Transcript continues...]*

---

## [22:00-24:34] Implementation Guide — Step by Step

*[Transcript continues...]*

---

## Appendix: Full Raw Transcript

The complete 759-segment transcript is available at: `/tmp/agentic-os-transcript.txt`

