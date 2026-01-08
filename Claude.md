# Payment Microservices Project

## Overview
Cinema booking platform with multiple microservices handling user management, 
movie listings, showtimes, and payment processing.

## Tech Stack
- Python/Flask microservices
- REST APIs
- JSON for data exchange

## Git Workflow
- This is a fork of umermansoor/microservices
- Default branch: `main` (NOT master - master exists but is deprecated)
- **CRITICAL**: When creating PRs with `gh pr create`, you MUST specify:
  - `--repo jacobkleiman3/demo-repo` (to target this fork, not upstream)
  - `--base main` (to target the main branch, not master)
  - Full command: `gh pr create --repo jacobkleiman3/demo-repo --base main --head <branch-name>`
- Always create feature branches for new work (never commit directly to main)
- PR workflow: Create feature branch → Make changes → Push → PR to `main` on this fork