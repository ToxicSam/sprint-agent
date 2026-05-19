# docs/ — Sprint Agent Documentation

## OVERVIEW
Technical and user-facing documentation for the full-stack Scrum management tool.

## STRUCTURE

```
docs/
├── API.md              # Full REST API reference with curl examples (Chinese)
├── ARCHITECTURE.md     # System architecture and data flow diagrams
├── BACKEND.md          # Backend conventions, FastAPI patterns, DB schema
├── CHANGELOG.md        # Version history, Keep a Changelog format
├── DATA_FORMAT.md      # init.json schema spec and Zero-Mock data philosophy
├── DEPLOY.md           # Deployment guide: Docker, static hosting, env vars (Chinese, 826 lines)
├── FRONTEND.md         # Frontend architecture: React 19, Vite, Tailwind, state management
├── PUBLISH.md          # Release guide: GitHub releases, Docker images, versioning
├── USAGE.md            # End-user manual: workflows, shortcuts, troubleshooting (Chinese)
└── UX_DESIGN.md        # UX principles: "Quick Actions Everywhere", keyboard-first design
```

## WHERE TO LOOK

| If you need... | Go to |
|---|---|
| API endpoint details / curl examples | `API.md` |
| System architecture / data flows | `ARCHITECTURE.md` |
| Backend code conventions | `BACKEND.md` |
| Frontend patterns / component structure | `FRONTEND.md` |
| Data import/export format | `DATA_FORMAT.md` |
| Deployment steps | `DEPLOY.md` |
| Release process | `PUBLISH.md` |
| User workflows / shortcuts | `USAGE.md` |
| UX rationale / design decisions | `UX_DESIGN.md` |
| What changed in each version | `CHANGELOG.md` |

## CONVENTIONS

- **Bilingual docs**: Most docs are written in Chinese. `CHANGELOG.md` is the only English doc.
- **Version-prefixed headers**: All docs start with `Sprint Agent v2.0 — ...`.
- **Table of contents**: Every doc >100 lines has a TOC with anchor links.
- **Changelog format**: Follows [Keep a Changelog](https://keepachangelog.com/) with `[Unreleased]` section at top.
- **Code blocks**: API docs use `bash` for curl, `json` for request/response bodies.
- **No generated API docs**: OpenAPI/Swagger is served at runtime (`/docs`), but `API.md` is hand-maintained.

## ANTI-PATTERNS

- **Do not duplicate README content**: The root `README.md` already covers quick start, tech stack, and project structure. Docs should go deeper, not repeat.
- **Do not add mock data examples**: Follow the Zero-Mock principle. All examples should reference `init.json` or real API responses.
- **Do not mix languages in one doc**: Each doc is either fully Chinese or fully English. Do not switch mid-document.
- **Do not let API.md drift**: When adding endpoints, update both the code and `API.md` in the same PR.
