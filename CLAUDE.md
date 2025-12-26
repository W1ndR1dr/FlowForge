# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FlowForge is an AI-assisted parallel development orchestrator. It enables systematic, parallel AI-assisted development by managing feature backlogs, generating optimized Claude Code prompts, automating Git worktree workflows, and orchestrating merges.

**Philosophy**: Built for "vibecoders" - developers who work extensively with AI assistance but may not be Git experts. FlowForge handles the complexity so users can focus on features.

## Build Commands

```bash
# Install in development mode
pip install -e .

# Install with server dependencies (for MCP server/web UI)
pip install -e ".[server]"

# Run CLI
forge --help
forge init
forge add "Feature Title"
forge start feature-id

# Run MCP/HTTP server (for remote access from Pi or mobile)
forge-server

# Server environment variables:
FLOWFORGE_PROJECTS_PATH=/Users/Brian/Projects/Active  # Where to find projects
FLOWFORGE_MAC_HOST=macs-tailscale-hostname            # For Pi→Mac SSH
FLOWFORGE_MAC_USER=Brian                               # Mac username
FLOWFORGE_PORT=8081                                    # Server port
FLOWFORGE_HOST=0.0.0.0                                 # Bind address
```

## Architecture

```
flowforge/
├── cli.py                # Typer CLI commands (main entry point)
├── config.py             # Project configuration (FlowForgeConfig, ProjectConfig)
├── registry.py           # Feature registry (Feature dataclass, CRUD, hierarchy)
├── worktree.py           # Git worktree management (WorktreeManager, ClaudeCodeLauncher)
├── intelligence.py       # Tiered AI intelligence (expert suggestion, research detection)
├── prompt_builder.py     # Implementation prompt generation
├── merge.py              # Merge orchestration (MergeOrchestrator, conflict detection)
├── mcp_server.py         # Remote MCP server for Claude Code (FlowForgeMCPServer)
├── server.py             # FastAPI wrapper (MCP + REST + Web UI at /)
└── remote.py             # SSH execution for Pi→Mac remote worktree creation
```

### Key Data Flow

1. **Feature Lifecycle**: `planned` → `in-progress` → `review` → `completed`
2. **Start Feature** (`forge start`): Creates worktree → generates prompt with expert suggestions → copies to clipboard
3. **Merge Feature** (`forge merge`): Conflict check (dry-run) → merge → validation (build command) → cleanup

### Per-Project Data (`.flowforge/`)

- `config.json` - Project settings (main branch, build command, claude command)
- `registry.json` - Feature database (all Feature objects)
- `prompts/` - Generated implementation prompts
- `research/` - Deep research outputs

## CLI Commands

```bash
# Project Setup
forge init                           # Initialize FlowForge
forge init --from-roadmap "docs/"    # Import features from markdown files

# Feature Management
forge add "Feature Title"            # Add feature (interactive)
forge list                           # Tree view of features
forge show <id>                      # Feature details

# Parallel Development (creates worktrees in .flowforge-worktrees/)
forge start <id>                     # Create worktree + generate prompt
forge start <id> --deep-research     # Force deep research mode
forge start <id> --skip-experts      # Skip expert suggestion phase
forge stop <id>                      # Mark ready for review
forge status                         # Show all active worktrees

# Merge Operations
forge sync <id>                      # Rebase feature onto latest main
forge merge-check                    # Check all review features for conflicts
forge merge-check <id>               # Check specific feature
forge merge <id>                     # Merge with validation
forge merge --auto                   # Merge all safe features in order
```

## Coding Style

- 4-space indentation, type hints on all function signatures
- Dataclasses for data models, Pydantic for API models
- Typer for CLI, Rich for output formatting
- Snake_case for functions/variables

### Key Patterns

**CLI Command Pattern:**
```python
@app.command()
def command_name(
    required_arg: str = typer.Argument(..., help="Description"),
    optional_flag: bool = typer.Option(False, "--flag", "-f", help="Description"),
):
    """Docstring becomes help text."""
    project_root, config, registry = get_context()
    # ... implementation
```

**Registry Updates** (save is automatic):
```python
registry.update_feature(feature_id, status=FeatureStatus.IN_PROGRESS, branch="...")
```

**MergeOrchestrator Pattern:**
```python
orchestrator = MergeOrchestrator(project_root, registry, main_branch, build_command)
result = orchestrator.check_conflicts(feature_id)  # Dry-run merge
result = orchestrator.merge_feature(feature_id, validate=True)  # Actual merge
```

## Testing

No automated tests yet. Test manually:
```bash
# Initialize in a test project
cd ~/Projects/Active/AirFit
forge init --from-roadmap "docs/Roadmap Features/"

# Test core workflow
forge list
forge add "Test Feature"
forge start test-feature
forge stop test-feature
forge merge-check test-feature
forge merge test-feature
```

## Key Design Decisions

### Tiered Intelligence System
Instead of hardcoded personas, FlowForge uses AI to dynamically:
1. **Tier 1**: Suggest relevant domain experts for any feature
2. **Tier 2**: Detect when deep research is warranted, open research threads
3. **Tier 3**: Research across multiple AI providers for critical decisions

### Git Worktrees for Parallelization
Each feature gets its own worktree, enabling multiple Claude Code sessions simultaneously:
```
project/
├── .flowforge-worktrees/
│   ├── feature-a/          # Claude Code session 1
│   ├── feature-b/          # Claude Code session 2
│   └── feature-c/          # Claude Code session 3
```

### MCP Server for Remote Access
The MCP server enables Claude Code on iOS/web to natively call FlowForge tools via Tailscale:
- Configure `http://pi.tailnet:8081` as MCP server
- Use natural language: "Start the zone2-tracking feature on AirFit"
- Claude calls `flowforge_start_feature("AirFit", "zone2-tracking")` automatically

**Available MCP tools**: `flowforge_list_projects`, `flowforge_list_features`, `flowforge_status`, `flowforge_start_feature`, `flowforge_stop_feature`, `flowforge_merge_check`, `flowforge_merge`, `flowforge_add_feature`

## Commit Conventions

```bash
feat(cli): Add merge command
fix(worktree): Handle existing branch case
refactor(registry): Simplify dependency tracking
```

## macOS App (FlowForgeApp)

The SwiftUI macOS app lives in `FlowForgeApp/`. Uses XcodeGen to manage the Xcode project.

### Server (required for full features)

The app connects to the FlowForge server for worktrees, prompts, git operations, etc.

```bash
# Start the server (run in background or separate terminal)
cd /Users/Brian/Projects/Active/FlowForge
source .venv/bin/activate
FLOWFORGE_PROJECTS_PATH=/Users/Brian/Projects/Active FLOWFORGE_PORT=8081 forge-server

# Or as one-liner to start in background:
cd /Users/Brian/Projects/Active/FlowForge && source .venv/bin/activate && FLOWFORGE_PROJECTS_PATH=/Users/Brian/Projects/Active FLOWFORGE_PORT=8081 forge-server &
```

The app auto-connects to `http://localhost:8081`. When migrating to Pi, just update `PlatformConfig.swift` with the Tailscale hostname.

### Build & Deploy (when user says "build the app", "deploy it", etc.)

```bash
cd /Users/Brian/Projects/Active/FlowForge/FlowForgeApp

# 1. Regenerate Xcode project (picks up new files automatically)
xcodegen generate

# 2. Build Release
xcodebuild -project FlowForgeApp.xcodeproj -scheme FlowForgeApp -configuration Release -derivedDataPath build ONLY_ACTIVE_ARCH=YES -quiet

# 3. Install to Applications (replaces previous version)
rm -rf /Applications/FlowForge.app && cp -R build/Build/Products/Release/FlowForge.app /Applications/

# 4. Launch
open /Applications/FlowForge.app
```

**One-liner for quick iteration:**
```bash
cd /Users/Brian/Projects/Active/FlowForge/FlowForgeApp && xcodegen generate && xcodebuild -project FlowForgeApp.xcodeproj -scheme FlowForgeApp -configuration Release -derivedDataPath build ONLY_ACTIVE_ARCH=YES -quiet && rm -rf /Applications/FlowForge.app && cp -R build/Build/Products/Release/FlowForge.app /Applications/ && open /Applications/FlowForge.app
```

### Adding New Swift Files

Just create the file anywhere in these folders - XcodeGen picks them up automatically:
- `App/` - macOS app entry point
- `Models/` - Data models (Feature, AppState, etc.)
- `Views/` - SwiftUI views
- `Services/` - APIClient, CLIBridge, etc.
- `Shared/` - Cross-platform utilities
- `Design/` - Design system (tokens, animations, components)

Then run `xcodegen generate` before building.

### Project Structure

```
FlowForgeApp/
├── project.yml              # XcodeGen config (defines targets, settings)
├── App/                     # macOS entry point
├── App-iOS/                 # iOS companion app entry point
├── Models/                  # Feature, AppState, Project, Proposal
├── Views/                   # ContentView, Kanban/, MissionControl/, etc.
├── Services/                # APIClient, CLIBridge, WebSocketClient
├── Shared/                  # Cross-platform code
└── Design/                  # Design system
    ├── DesignTokens.swift   # Colors, spacing, typography
    ├── AnimationPrimitives.swift  # Spring physics, micro-interactions
    └── Components/          # VibeInput, StreakBadge, ConfettiView, etc.
```

### Design System Philosophy

Built with guidance from legendary designers (see plan file):
- **Jony Ive**: Every pixel feels considered
- **Dieter Rams**: Less, but better
- **Bret Victor**: Immediate feedback, see the work
- **Edward Tufte**: Show the data, eliminate chartjunk
- **Mike Matas**: Physics-based, magical moments

## iOS TestFlight Deployment

### Deploy to TestFlight
```bash
./scripts/deploy-to-testflight.sh --auto             # [RECOMMENDED] Claude decides version
./scripts/deploy-to-testflight.sh --bump-build       # Build number only (1.0 build 1 → 2)
./scripts/deploy-to-testflight.sh --bump-version     # Force version bump
```

Archives, exports, and uploads to TestFlight. `--auto` uses Claude to analyze commits and determine if version bump is needed (MAJOR/MINOR/PATCH or BUILD-only).

**Prerequisites:**
- Credentials in `~/.appstore/credentials` (shared with AirFit)
- App exists in App Store Connect (bundle ID: `com.flowforge.app.ios`)

### TestFlight Release Workflow

When the user says **"push to TestFlight"**, **"deploy iOS"**, or similar:

1. **Pre-flight**: Ensure git working tree is clean (commit pending changes first)
2. **Deploy**: Run `./scripts/deploy-to-testflight.sh --auto`
3. **Post-deploy**: Report version/build number, remind to check App Store Connect in ~10 minutes

### If deployment fails
- Verify `~/.appstore/credentials` exists with valid API keys
- Verify signing certificates in Xcode → Settings → Accounts
- Check App Store Connect for compliance issues

## macOS Release (Sparkle Auto-Updates)

### Release a new macOS version
```bash
./scripts/release-macos.sh              # Build, sign, update appcast
./scripts/release-macos.sh 1.2.0        # Specify version
```

This script:
1. Generates Sparkle EdDSA keys (first run only, saved to `~/.flowforge-keys/`)
2. Builds Release archive
3. Signs with Sparkle
4. Updates `appcast.xml`
5. Installs to `/Applications`

**After running**, create a GitHub release and push:
```bash
git add appcast.xml
git commit -m "Release v1.x.x"
git push
gh release create v1.x.x releases/FlowForge-1.x.x.zip --title "FlowForge 1.x.x"
```

The macOS app checks `appcast.xml` on GitHub for updates and auto-installs new versions.

## Additional Documentation

- `docs/SESSION_CONTEXT.md` - Full development context, verified working features, what's next
- `docs/RASPBERRY_PI_SETUP.md` - Step-by-step Pi deployment guide (Tailscale, systemd, SSH keys)
- `docs/PLAN.md` - Original development plan with architecture diagrams
