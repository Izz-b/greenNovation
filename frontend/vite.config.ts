import path from "node:path";
import { defineConfig, loadEnv } from "vite";
import type { Plugin } from "vite";
import tailwindcss from "@tailwindcss/vite";
import tsconfigPaths from "vite-tsconfig-paths";
import react from "@vitejs/plugin-react";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";

/**
 * TanStack Start sets `environments.client.optimizeDeps` itself, so root `optimizeDeps` is ignored.
 * pptx-renderer (and echarts) often 404 or break when esbuild-prebundled into `.vite/deps` in dev.
 */
function pptxRendererOptimizeDeps(): Plugin {
  /** Pre-bundle gives CJS→ESM default export; raw `jszip/dist/jszip.min.js` has no ESM default */
  const extraExclude = ["@aiden0z/pptx-renderer", "echarts"] as const;
  const extraInclude = ["jszip"] as const;
  return {
    name: "pptx-renderer-optimize-deps",
    enforce: "post",
    config(config) {
      const od = config.environments?.client?.optimizeDeps;
      const exclude = [...new Set([...(od?.exclude ?? []), ...extraExclude])];
      const include = [...new Set([...(od?.include ?? []), ...extraInclude])];
      return {
        environments: {
          client: {
            optimizeDeps: { exclude, include },
          },
        },
      };
    },
  };
}

/**
 * Native Vite config (no @lovable.dev/vite-tanstack-config) to avoid CJS/ESM
 * issues with `lovable-tagger` on Windows + older Node.
 *
 * Default dev API target is 8001. If your backend runs elsewhere, set in .env.local:
 *   VITE_API_PROXY_TARGET=http://127.0.0.1:<your-port>
 *
 * Vite 7 recommends Node 20.19+ or 22.12+. Upgrade Node if dev still warns or fails.
 */
export default defineConfig(async ({ mode, command }) => {
  const loadedEnv = loadEnv(mode, process.cwd(), "VITE_");
  const envDefine: Record<string, string> = {};
  for (const [key, value] of Object.entries(loadedEnv)) {
    envDefine[`import.meta.env.${key}`] = JSON.stringify(value);
  }

  const apiProxyTarget = loadedEnv.VITE_API_PROXY_TARGET || "http://127.0.0.1:8001";

  const plugins: NonNullable<import("vite").UserConfig["plugins"]> = [
    tailwindcss(),
    tsconfigPaths({ projects: ["./tsconfig.json"] }),
    ...tanstackStart().filter(Boolean),
    react(),
    pptxRendererOptimizeDeps(),
  ];

  if (command === "build") {
    try {
      const { cloudflare } = await import("@cloudflare/vite-plugin");
      plugins.push(cloudflare({ viteEnvironment: { name: "ssr" } }));
    } catch {
      /* optional deploy plugin */
    }
  }

  return {
    define: envDefine,
    resolve: {
      alias: {
        "@": `${process.cwd()}/src`,
        /** Prefer CJS entry so imports match `import JSZip from "jszip"` when not yet optimized */
        jszip: path.resolve(process.cwd(), "node_modules/jszip/lib/index.js"),
      },
      dedupe: [
        "react",
        "react-dom",
        "react/jsx-runtime",
        "react/jsx-dev-runtime",
        "@tanstack/react-query",
        "@tanstack/query-core",
      ],
    },
    plugins,
    server: {
      host: "::",
      port: 8080,
      proxy: {
        "/api": { target: apiProxyTarget, changeOrigin: true },
        "/health": { target: apiProxyTarget, changeOrigin: true },
      },
    },
  };
});
