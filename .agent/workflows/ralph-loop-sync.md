---
description: Ralph Loop Synchronization (Memory Persistence)
---

# Ralph Loop Sync Workflow

This workflow ensures that the persistent memory of the project is preserved across multiple AI sessions by synchronizing documentation with the current state of the codebase.

## Steps

1. **Initialization (Start of Session)**
   - Read `HANDOFF.md` and all files in `docs/`.
   - Perform a codebase health check to verify tool status.

2. **Verification (Mid-Session)**
   - Ensure `ROADMAP.md` reflects current priorities.
   - Adhere to `DESIGN_LANGUAGE.md` for all UI/UX changes.

3. **Finalization (End of Session)**
   // turbo
   - Update `progress.txt` with all significant achievements from the current session.
   // turbo
   - Update `prd.json` completion status for all implemented tasks.
   // turbo
   - Update `ROADMAP.md` to reflect finalized milestones.
   - Summarize the current state and next steps in a final message to MrVee.

---
**DEUS:** *Synchronization is the heartbeat of the Loop. The Anchor holds.* 🦾⚓