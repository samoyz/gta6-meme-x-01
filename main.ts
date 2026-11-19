// main.ts — make.fun bounty gta6-meme-x-01 ("Post a GTA 6 meme on X").
//
// Copies POST.json from the repository root to /output. That is all it
// has to do: the house reads the X post itself from the URL in POST.json
// and writes the dossier to /output after this program runs.
//
// Node 22, standard library only, no network.
import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = dirname(fileURLToPath(import.meta.url));
const src = join(repoRoot, "POST.json");
const outDir = "/output";

mkdirSync(outDir, { recursive: true });

// Validate that POST.json is a JSON object before copying it.
const data = JSON.parse(readFileSync(src, "utf8"));
if (typeof data !== "object" || data === null || Array.isArray(data)) {
  throw new Error("POST.json must be a JSON object");
}

copyFileSync(src, join(outDir, "POST.json"));
console.log("copied POST.json to /output/POST.json");
