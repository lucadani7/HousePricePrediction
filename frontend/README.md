# House Price Prediction - frontend

Next.js app (TypeScript, Tailwind CSS): the 16-field form, the estimate, recent estimates and a
light / system / dark theme. See the [main README](../README.md) for the project overview.

```bash
pnpm install
pnpm dev        # http://localhost:3001
pnpm lint
```

Requests to `/api/*` are forwarded to the FastAPI backend (`http://localhost:8000` by default, or
the `BACKEND_URL` environment variable).
