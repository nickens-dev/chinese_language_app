# Frontend

The frontend is a responsive React and TypeScript application built with Vite. It presents data and collects learner input; scheduling, mastery, and scoring rules remain in the backend.

## Source map

```text
src/
  app/          Application shell and cross-feature composition
  features/     User capabilities, beginning with the deck library
  components/   Future reusable presentation components
  api/          Backend access functions and later generated API types
  styles/       Shared design tokens and global responsive styles
```

The current slice renders and filters visual deck cards, supports multi-deck selection, and provides create, detail, edit, and archive workflows through the deck API. Language-item management is the next boundary.

## Commands

After installing Node.js 22 or newer:

```powershell
npm.cmd install
npm.cmd run dev
```

Run `npm.cmd run lint`, `npm.cmd run test`, and `npm.cmd run build` for validation. Vite serves the interface at `http://localhost:5173` and proxies `/api` requests to FastAPI at `http://127.0.0.1:8000`.

The `.cmd` form works under restrictive Windows PowerShell execution policies without changing system security settings. In shells where `npm` already works, either form is acceptable.

## Boundaries

- Components may format data for display but must not invent mastery or scheduling rules.
- API calls live under `src/api`, not directly inside presentation components.
- Domain types will eventually be generated from FastAPI's OpenAPI contract.
- Features are grouped by learner capability instead of technical file type.
