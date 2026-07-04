# Frontend - Zirkus Mond

This folder contains the frontend build setup (Vue.js + Vite + Tailwind CSS).

**Note:** This is a temporary setup. It will be replaced with Next.js in the coming months.

## Structure

```
frontend/
├── src/
│   ├── components/          # Vue components
│   │   └── qr-scanner/      # QR scanner component
│   ├── design.css           # Original CSS
│   └── tailwind.css         # Generated Tailwind CSS
├── public/
│   └── fonts/               # Web fonts
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## Build Process

The built assets are output to `../backend/static/media/dist/` and served by Django.

### Commands

```bash
# Install dependencies
npm install

# Watch and rebuild Tailwind CSS
npm run tailwind

# Build for production
npm run build

# Dev server
npm run dev
```

## Migration to Next.js

When migrating to Next.js:

1. Replace this `frontend/` folder with the Next.js project
2. Update template references if build output paths change
3. Convert Vue components to React components
4. Merge Tailwind config with Next.js setup

## Contributing

1. Create a branch off `main` for your change.
2. Run `npm install` and `npm run dev` to work locally.
3. Keep commits focused and use clear, descriptive messages.
4. Open a pull request against `main` and wait for CI to pass.
5. Request a review before merging.
