#!/usr/bin/env node
/**
 * Arranca n8n con auth básica y carpeta de datos local.
 * Tras el tunnel, actualizá WEBHOOK_URL con la URL pública.
 */
import { spawn } from "node:child_process";
import { existsSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
process.chdir(root);

function loadEnvFile(path) {
  if (!existsSync(path)) return;
  for (const line of readFileSync(path, "utf8").split("\n")) {
    const t = line.trim();
    if (!t || t.startsWith("#")) continue;
    const i = t.indexOf("=");
    if (i < 0) continue;
    const k = t.slice(0, i).trim();
    let v = t.slice(i + 1).trim();
    if (
      (v.startsWith('"') && v.endsWith('"')) ||
      (v.startsWith("'") && v.endsWith("'"))
    ) {
      v = v.slice(1, -1);
    }
    if (!(k in process.env)) process.env[k] = v;
  }
}

loadEnvFile(join(root, ".env"));

const port = process.env.N8N_PORT || "5678";
const dataDir = join(root, process.env.N8N_USER_FOLDER || "./data");
mkdirSync(dataDir, { recursive: true });

process.env.N8N_PORT = port;
process.env.N8N_LISTEN_ADDRESS = process.env.N8N_LISTEN_ADDRESS || "127.0.0.1";
process.env.N8N_USER_FOLDER = dataDir;
process.env.N8N_BASIC_AUTH_ACTIVE = process.env.N8N_BASIC_AUTH_ACTIVE || "true";
process.env.N8N_BASIC_AUTH_USER = process.env.N8N_BASIC_AUTH_USER || "yoryo";
process.env.N8N_BASIC_AUTH_PASSWORD =
  process.env.N8N_BASIC_AUTH_PASSWORD || "cambia-esto-ya";
process.env.N8N_DIAGNOSTICS_ENABLED = "false";
process.env.N8N_PERSONALIZATION_ENABLED = "false";

const bin = join(root, "node_modules", "n8n", "bin", "n8n");
if (!existsSync(bin)) {
  console.error("Falta n8n. Corré: npm install");
  process.exit(1);
}

console.log(`n8n → http://127.0.0.1:${port}`);
console.log(`data → ${dataDir}`);
console.log("Luego: bash scripts/tunnel.sh  (URL para el celular)");

const child = spawn(process.execPath, [bin, "start"], {
  stdio: "inherit",
  env: process.env,
});
child.on("exit", (code) => process.exit(code ?? 1));
