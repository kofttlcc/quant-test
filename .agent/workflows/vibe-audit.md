description: Team B (Auditor) 標準作業程序：審計、修復與知識進化
Vibe Audit & Evolve Workflow
Step 1: Deep Scan
1.Read artifacts/handoff_notes.md.

2.Read the code changes in the current feat/ branch.

3.Compare against skills/_base/ standards.

Step 2: Critique & Fix // turbo
1.Identify logic errors, security risks, and type violations.

2.Apply fixes directly to the code.

3.Run tests to ensure the fix works.

Step 3: The Evolution Check (The "Brain" Step)
Ask yourself: "Did the Builder make a mistake that could have been prevented with a rule?"

IF YES:

1.Draft a concise rule explanation.

2.Use tool evolve_skill(category="patterns", title="...", content="...").

3.Log this evolution in the chat.

Step 4: Release
1.If tests pass and skills are updated:

* git checkout main

* git merge feat/...

* Delete the feature branch.

2.Report: "Feature merged. Knowledge base updated with."