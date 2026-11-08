<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# DX-OS Internal Service Portal — Issue #39

**MOCK / DEVELOPMENT · Tier 2 UI prototype. There is no real end-to-end HTTP yet. Issue #39 must stay OPEN.**

A standalone single-page application with a Vietnamese user interface. It demonstrates two services, IT Support and Facility, on the same components, request view model, service interface and timeline. It changes nothing in Core, Gateway, Identity, Workflow, Flyway V1–V4 or PR #35.

## Run on localhost

Requires Node.js >= 22.12 (checked with Node 24.19.0), npm and a modern browser.

```powershell
Set-Location D:\olp\issue39-university-ui\frontend
npm.cmd ci
npm.cmd run dev
```

Open **http://127.0.0.1:5173**. On macOS/Linux use `npm` instead of `npm.cmd`. No backend, database, `.env` file or credentials are needed.

```powershell
npm.cmd run build
npm.cmd run preview -- --port 4173
```

Production hosting must provide an SPA fallback to `index.html` for deep links. Deployment is out of scope here.

## Stack and structure

React 19, Vite 8, strict TypeScript, React Router 7, Lucide, Be Vietnam Pro served locally, and CSS tokens; exact versions are in `package-lock.json`. The stack was confirmed by the user after an audit. The app does not load fonts, analytics or any third-party resource at run time.

```text
src/
  components/ui.tsx           Shared table, badges, timeline, modal, UI states
  domain/request.ts          Shared view model, labels, validation, filtering
  fixtures/requests.ts        Synthetic demo records for both services
  services/RequestService.ts  UI-facing application service interface
  services/portalService.ts   Composition root: interface -> mock service
  services/MockRequestService.ts  In-memory demo responses and fault controls
  services/HttpApiClient.ts   Closed HTTP boundary; rejects before networking
  hooks/useRequests.ts        Loading, read errors, expired demo session handling
  pages/                     Dashboard, list/history/desk, create, detail, system
  context.tsx                Demo role, success announcements, refresh state
  tokens.css / styles.css    Palette, typography, responsive and reduced motion
tests/portal.spec.ts          Browser smoke, WCAG checks and real screenshots
scripts/check-security.mjs    Source/bundle credential-pattern check
```

By default MOCK uses `RequestService` through the composition root. `HttpApiClient` is separate and always returns `LIVE_BLOCKED`. APP-10/11/13/14 already have a mapper, the Assignment Form, a typed HTTP adapter for the nine candidate routes of PR #63, and a separate Portal feature through optional `helpdeskService` injection. They are tested only with a fake transport; there is no concrete LIVE transport, token or flag that enables LIVE. Do not treat the mock view model as a backend DTO. See the [MVP inventory and real-connection checklist](https://github.com/tricore-opentrix/opentrix/blob/c73bbc306a698141169304e5da848ea0686700db/docs/application/issue39-mvp-readiness-20261027.md) (a permalink to commit `c73bbc3` on the branch `feature/a05-portal-bff-integration`, which is not on `main`).

Logout, a role change and a 401 invalidate the async results of the old session. A late response does not navigate, announce anything or expire the new session; a 401 for the current session still ends the session after the user leaves the screen. Assignment does not start a GET Detail after logout. A write that was already sent is neither cancelled nor replayed; an MVP unknown outcome stays locked until it is reconciled. This is a demo/fake session lifecycle, not an OIDC/BFF logout or session revocation.

The two workflow UX flows share the form, table, metadata, action dialog and timeline. The fixed responses in the mock exist only for the demo; this is **not a frontend Workflow engine**: it does not execute definitions and has no BPMN editor, persistence or Core orchestration. The actions that are really allowed must be decided by the backend after the security gate.

## Screens

| Route           | Content                                                             |
| --------------- | ------------------------------------------------------------------- |
| `/session`      | Enter/end the demo session, change role, simulate expiry; SSO is blocked |
| `/login`        | Email/password form, remembers only the email; submit and password recovery are blocked |
| `/register`     | Student/Lecturer registration form; creates no account and grants no permission |
| `/`             | Dashboard and quick access to the two services                      |
| `/requests`     | Accent-insensitive search, service/status filters, pagination       |
| `/requests/new` | Shared form, validation, loading, success/error                     |
| `/approvals`    | Handler desk for the simulated handler role                         |
| `/requests/:id` | Detail, mock version, handling actions and timeline                 |
| `/history`      | History of each request, newest first                               |
| `/integration`  | Capability status, LIVE-block check and fault controls              |

Loading is simulated with a 350 ms delay. With no results, the screen guides the user to change the filters. A read error has a reload button that the user triggers. The form keeps its content on a network error. Writes are locked against double submit and are never retried automatically. On `COMMIT_OUTCOME_UNKNOWN` the UI disables further submits and tells the user to check the history. A simulated 401 ends the session and shows a message; 403 and hidden/missing 404 show safe messages. None of this is evidence of backend authorization checks.

## Security boundary and BLOCKED APIs

| Capability               | Missing condition                                                                                                                 |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| Identity / SSO           | Verified browser login, OIDC Authorization Code + PKCE, #24                                                                       |
| Gateway / Workflow HTTP  | Registration, resource ACL, tenant binding and security gate #22/#23/#24; every create/activate/transition/snapshot/history call is blocked |
| Data persistence         | An approved HTTP application contract; no direct PostgreSQL or Java connection                                                    |
| Attachments              | Backend Storage API with authorization checks #26: **BLOCKED FEATURE**, no file input and no fake upload                          |
| HTTP DTO / error mapping | OpenAPI and contract review #37                                                                                                   |

There is no secret, admin token, service-role key, database credential, and no `X-User`/`X-Role` used as an identity source. Only the demo name/role is stored in `sessionStorage`; editing that value is not proof of authentication/authorization. Fixture visibility (an employee sees their own sample requests; a handler sees the sample data set) is only UX behavior.

## Testing

```powershell
npm.cmd run build
npm.cmd test
npx.cmd playwright install chromium
npm.cmd run test:smoke
npm.cmd run check:security
```

The smoke suite starts a production preview at `127.0.0.1:4173` and checks the two UI flows, error/empty/validation states, API blocking, keyboard/modal behavior, desktop/tablet/mobile layouts, and axe WCAG 2 A/AA + 2.1 AA. Screenshots are produced directly from localhost at [evidence](https://github.com/tricore-opentrix/opentrix/blob/05c5d9967e88d24cfb4b41f4134dcc2522ac9253/docs/evidence/issue39-portal/README.md) (a permalink to commit `05c5d99`, not on `main`). Composited images are not used as evidence. The security script only checks for common credential patterns and goes with a source and staged-diff review.

Python is not in the deployment environment, so the browser suite uses Playwright with TypeScript and can run with the project's locked dependencies.

## Limits

### Email/password: UI preview only

`/login` and `/register` use the DX-OS branding, Be Vietnam Pro and Lucide, with a
two-column layout on desktop and one column on mobile. Open them from the link on
`/session` or directly by URL. The **Vào phiên Demo** (Enter the Demo session) button
always opens the existing, separate Demo flow.

The email, full name, password length (registration: 12–128 characters) and password
confirmation are checked in the form. These are temporary UI rules, not an approved
Identity policy. Use fake data only; do not type a real password to test.

A valid submit only checks the form locally, clears the password fields and then shows
**BLOCKED FEATURE**. It sends no HTTP request, creates no JWT, creates no account,
does not change the Demo role/session and never reports a successful sign-in. Forgot
password also shows **BLOCKED FEATURE**. There is no endpoint or switch that enables
authentication. The real flow must be handled by the backend Identity service through an
approved and protected API.

Only when the user selects **Ghi nhớ email** (Remember email) is a valid email stored in
`localStorage` under the key `dxos-remembered-email-v1`; unchecking it deletes it
immediately. The password exists only temporarily in the input field and in memory during
validation; it is not stored in browser storage, fixtures or logs and is not sent over the
network. Registration offers only Student/Lecturer and rejects a role value that was
edited to admin/processor. No real permission is granted.

The new tests are in `src/pages/Auth.test.tsx` and `tests/auth.spec.ts`. See the
[Login/Register screenshots](https://github.com/tricore-opentrix/opentrix/blob/00b10fa43d01cc3dcca725b2ed66a43bdaa92268/docs/evidence/issue39-portal/auth/README.md) (a permalink to commit `00b10fa`, not on `main`) at desktop,
tablet, 390 px mobile and 320 px. The existing smoke suite continues to check request
creation, approval, handling, the timeline and the fail-closed `HttpApiClient`. The theme
only raises the contrast of some secondary text colors so that the existing WCAG checks
pass; it does not change the dashboard layout.

- Requests and history exist only in memory in **one tab**. Reloading or restoring the demo resets the fixtures; changing routes through the sidebar keeps the data.
- The demo session stores only the role choice in the tab; there is no SSO, access token or real permission.
- An unknown write result is only a simulated error; the mock does not confirm that a real commit happened.
- Real 401/403/404, cross-tenant denial, concurrency/persistence and end-to-end HTTP have not been verified.
- Browser coverage is currently Chromium; axe does not replace a full manual accessibility audit. Tables scroll horizontally inside their container on small screens.
- No file upload/read, no real notifications and no hosting yet.

See the [demo guide](DEMO_GUIDE.md). Refs #39; only record **mock UI prototype complete** when the local checks pass, and do not close Issue #39.
