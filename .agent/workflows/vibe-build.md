---
description: 
---

description: Team A (Builder) 標準作業程序：從需求到代碼實現
Vibe Build Workflow
@.agent/roles/builder.md @.agent/rules/constitution.md

Step 1: Context Loading // turbo
1.Read .agent/rules/constitution.md to confirm constraints.

2.CRITICAL: Use search_knowledge tool to find existing patterns in skills/.

* Query: Based on the user's current request.

3.State your plan briefly: "I found pattern X, applying it to build Y."

Step 2: Vibe Coding // turbo
1.Create a new branch: git checkout -b feat/[timestamp]-vibe.

2.Generate the code files. Focus on functionality first, perfection second.

3.Run local tests (if available) or create a simple verify.py script.

Step 3: Handoff
1.Do NOT merge.

2.Create a handoff artifact: artifacts/handoff_notes.md listing:

* What was built.

* What shortcuts were taken (e.g., "hardcoded styling").

* Any uncertainties.

3.Commit changes: git commit -am "feat: vibe implementation"

4.STOP. Inform user: "Build complete. Please call @auditor to review."