import { build } from "esbuild";
import { mkdir } from "node:fs/promises";

await mkdir("src/mathblocks/static", { recursive: true });
await build({
  entryPoints: ["frontend/src/index.ts"],
  outfile: "src/mathblocks/static/index.js",
  bundle: true,
  format: "esm",
  platform: "browser",
  target: ["es2022"],
  sourcemap: true,
});
console.log("Built MathBlocks frontend into src/mathblocks/static/");
