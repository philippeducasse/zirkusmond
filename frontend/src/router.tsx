import { createRouter as createTanStackRouter } from "@tanstack/react-router";
import { setupRouterSsrQueryIntegration } from "@tanstack/react-router-ssr-query";
import { QueryClient } from "@tanstack/react-query";
import { routeTree } from "./routeTree.gen";

export const getRouter = () => {
  // Single QueryClient per request (SSR) / per app (browser). It holds the
  // TanStack Query cache that loaders write to and components read from.
  const queryClient = new QueryClient();

  const router = createTanStackRouter({
    routeTree,
    // Exposes the QueryClient to every route loader via `context.queryClient`
    // (typed in the RouterContext interface in routes/__root.tsx).
    context: { queryClient },
    scrollRestoration: true,
    defaultPreload: "intent",
    defaultPreloadStaleTime: 0,
  });

  // Bridges TanStack Router SSR and TanStack Query: queries fetched in loaders
  // on the server are dehydrated into the HTML and rehydrated in the browser,
  // so the client renders from cache instead of refetching on first load.
  setupRouterSsrQueryIntegration({
    router,
    queryClient,
  });

  return router;
};

declare module "@tanstack/react-router" {
  interface Register {
    router: ReturnType<typeof getRouter>;
  }
}
