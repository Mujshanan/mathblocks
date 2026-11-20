import { fileURLToPath } from "node:url";
import { resolve } from "node:path";
import { defineConfig } from "vite";

const projectRoot = fileURLToPath(new URL(".", import.meta.url));

export default defineConfig({
  root: resolve(projectRoot, "frontend/dev"),
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
  },
  build: {
    outDir: resolve(projectRoot, "src/mathblocks/static"),
    emptyOutDir: true,
    sourcemap: true,
    lib: {
      entry: resolve(projectRoot, "frontend/src/index.ts"),
      formats: ["es"],
      fileName: () => "index.js",
    },
    rolldownOptions: {
      output: {
        codeSplitting: false,
      },
    },
  },
});
