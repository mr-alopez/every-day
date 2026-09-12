/* Stage the web app into www/ for Capacitor to bundle.

   Two deliberate differences from the repo root, which is what GitHub Pages
   serves:

   1. sw.js is excluded. capacitor:// is a secure context, so the service worker
      registration in index.html would fire inside the WebView and then serve
      its own cache forever — every rebuild would appear to do nothing.
      index.html also guards on !window.Capacitor for the same reason.

   2. A <script src="bridge.js"> tag is injected. Only the Android bundle has
      bridge.js, so injecting here keeps the Pages copy of index.html pristine
      with nothing to 404 on. */
import { mkdir, copyFile, rm, readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const out = join(root, "www");

const ASSETS = [
  "manifest.webmanifest",
  "icon.svg",
  "icon-180.png",
  "icon-192.png",
  "icon-512.png",
];

await rm(out, { recursive: true, force: true });
await mkdir(out, { recursive: true });

for (const f of ASSETS) {
  await copyFile(join(root, f), join(out, f));
}

const TAG = '<script src="bridge.js"></script>';
let html = await readFile(join(root, "index.html"), "utf8");
if (!html.includes("</head>")) throw new Error("index.html has no </head> to inject into");
html = html.replace("</head>", `${TAG}\n</head>`);
await writeFile(join(out, "index.html"), html, "utf8");

console.log(`www/ staged: index.html (+bridge tag), ${ASSETS.join(", ")}`);
