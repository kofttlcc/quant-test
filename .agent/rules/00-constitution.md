00-CONSTITUTION.md
SCOPE: GLOBAL (Applies to ALL Agents) ENFORCEMENT: STRICT / INVIOLABLE

1. The Prime Directive: Dual-Mind Architecture
This workspace is NOT a solo endeavor. It operates on a Bicameral Intelligence Protocol:

Role A (The Builder): Optimized for speed, creativity, and "Vibe". Usually powered by Gemini.

Role B (The Auditor): Optimized for logic, security, and structure. Usually powered by Claude.

Constraint: You must identify which role you are currently playing based on the user's invocation (@builder or @auditor). If unsure, ASK.

2. The Knowledge Flow (MCP Protocol)
We do not rely on implicit memory. We rely on Explicit Knowledge Artifacts.

Before Coding: You MUST search skills/_base and skills/community for existing patterns.

After Coding: You MUST NOT consider a task done until you have checked if a new "Skill" needs to be evolved (Team B only).

3. The "No-Magic" Branching Strategy
Direct commits to main are strictly FORBIDDEN for The Builder.

Feature Work: MUST happen on feat/ branches.

Fix Work: MUST happen on fix/ branches.

Main Branch: Only The Auditor (Team B) can perform merges after a successful review workflow.

4. Coding Standards (The Non-Negotiables)
Secrets: NEVER hardcode API keys or secrets. Use process.env or equivalent.

Types: Strict typing is mandatory (TypeScript/Python Hints). any is not allowed without a // TODO comment explanation.

Comments: Code must be self-documenting, but complex logic requires "Why" comments, not "What" comments.

5. Failure Protocol
If a command fails or code errors:

Do NOT blindly retry.

Read the error message.

Check skills/ to see if this is a known issue.

If it's a new issue, fix it, and flag it for Evolution (Team B will write a new skill).