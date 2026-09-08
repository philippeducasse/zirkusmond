import { defineConfig } from "vite";
import { devtools } from "@tanstack/devtools-vite";
import { nitro } from "nitro/vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import { sentryTanstackStart } from "@sentry/tanstackstart-react/vite";

import viteReact from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

const config = defineConfig({
  resolve: { tsconfigPaths: true },
  server: {
    proxy: {
      // In staging/prod, nginx serves /media/ directly from disk (see
      // deploy/nginx.default). Locally there's no nginx, so proxy it to
      // Django directly instead.
      "/media": process.env.API_URL ?? "http://localhost:8000",
    },
  },
  plugins: [
    devtools(),
    tailwindcss(),
    tanstackStart(),
    nitro(),
    viteReact(),
    sentryTanstackStart({
      org: process.env.SENTRY_ORG,
      project: process.env.SENTRY_PROJECT,
      authToken: process.env.SENTRY_AUTH_TOKEN,
    }),
  ],
});

export default config;
