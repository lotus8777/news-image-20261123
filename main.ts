// Entry point for the news-image-20261123 poster.
//
// The poster is pre-built and committed as entry.png next to this file.
// All this program does is check that image and copy it, byte for byte,
// to the output directory the grader names. It never draws, rebuilds or
// re-encodes anything, so the two grader runs always write identical bytes.

import { copyFileSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const MAX_BYTES = 1048576;
const MAX_EDGE = 1024;

// First eight bytes of every PNG file.
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function fail(message: string): never {
  console.error("entry failed: " + message);
  process.exit(1);
}

function main(): void {
  const here = dirname(fileURLToPath(import.meta.url));
  const source = join(here, "entry.png");

  let bytes: Buffer;
  try {
    bytes = readFileSync(source);
  } catch {
    fail("entry.png not found next to main.ts");
  }

  if (bytes.length > MAX_BYTES) {
    fail(`entry.png is ${bytes.length} bytes, over the 1 MiB limit`);
  }
  if (bytes.length < 33 || !bytes.subarray(0, 8).equals(PNG_MAGIC)) {
    fail("entry.png does not start with the PNG signature");
  }
  if (bytes.toString("ascii", 12, 16) !== "IHDR") {
    fail("entry.png has no IHDR chunk where one belongs");
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width > MAX_EDGE || height > MAX_EDGE) {
    fail(`entry.png is ${width}x${height}, over the 1024x1024 limit`);
  }

  const outDir = process.env.MAKEFUN_OUTPUT_DIR || here;
  mkdirSync(outDir, { recursive: true });
  const dest = join(outDir, "entry.png");
  copyFileSync(source, dest);

  const written = statSync(dest).size;
  if (written !== bytes.length) {
    fail(`copy came out ${written} bytes, expected ${bytes.length}`);
  }
  console.log(`copied entry.png (${width}x${height}, ${written} bytes) to ${dest}`);
}

main();
