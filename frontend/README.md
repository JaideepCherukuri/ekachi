# Ekachi Frontend

English | [中文](README_zh.md)

This is the Vite frontend for Ekachi. It provides the task chat workspace, session history, authentication flow, file upload UX, tool panels, and the OpenClaw companion interface.

## Environment

Create `.env.development` with:

```ini
VITE_API_URL=http://127.0.0.1:8000
```

For production, the live deployment uses:

```ini
VITE_API_URL=https://api.ekachi.com
```

## Commands

```bash
npm install
npm run dev
npm run build
```

## Deployment Notes

- Production hosting: Vercel
- SPA routing rewrite: `vercel.json`
- Autodeploy target: the standalone `ekachi` GitHub repository
