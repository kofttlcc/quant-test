Workflow 01: Gemini Development Cycle (Iron Laws Edition)

Trigger: Phase 1 Initialization.

Phase 1: Planning & Options (The Choice)

Actor: PM + Architects

Input: User Request.

Mandatory Action:

Clarify: If request is vague, ASK the user.

Design Options: Create docs/Plan_Options.md.

Plan A (Conservative): ... (Pros/Cons)

Plan B (Aggressive): ... (Pros/Cons)

Wait for User: User selects a plan.

Checklist: Generate docs/Dev_Checklist.md (in Traditional Chinese).

Exit Condition: User approves Plan and Checklist.

Phase 2: Blueprint & Implementation (The Build)

Actor: Specific Role (e.g., DataEng, MLE)

Input: Approved Checklist Item.

Mandatory Action (Per Feature):

Natural Language Description: Explain how you will implement this in Traditional Chinese.

Wait for User/PM: Confirm the logic is sound.

Code: Write the code.

Localization: Ensure all outputs are Chinese.

Self-Test: Run if __name__ == "__main__":.

Constraint: Atomic Isolation. Don't touch other modules.

Phase 3: Integration & UI

Actor: Backend & Frontend

Action: Connect API and UI.

Rule: UI MUST BE TRADITIONAL CHINESE.

Evidence: Screenshots (Simulated) or Logs.

Phase 4: The QA Gauntlet (Regression)

Actor: QA Engineer

Action:

Test New Feature: Does it work?

Regression Test: Did we break the previous module?

Reverse Audit: If bug found, trace back to source.

Exit Condition: All Tests Passed.

Phase 5: Acceptance

Actor: PM & Fund Manager

Action: Verify Checklist & Metrics.

Output: "TASK_COMPLETED_READY_FOR_HANDOFF"