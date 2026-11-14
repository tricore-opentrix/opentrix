// SPDX-FileCopyrightText: 2026 TRICORE contributors
// SPDX-License-Identifier: Apache-2.0
import { defineConfig } from "@playwright/test";
import { resolve } from "node:path";

export default defineConfig({
  testDir: ".",
  workers: 1,
  timeout: 0,
  reporter: "list",
  outputDir: "../test-results/ui-preview",
  use: {
    baseURL: "https://localhost:9443",
    serviceWorkers: "block",
    viewport: null,
    trace: "off",
  },
  projects: [
    {
      name: "ui-preview",
      testMatch: "ui-preview.session.ts",
      use: { headless: false },
    },
    {
      name: "ui-preview-check",
      testMatch: "ui-preview.check.ts",
      timeout: 60_000,
      use: { headless: true, viewport: { width: 1440, height: 1000 } },
    },
  ],
  webServer: {
    cwd: resolve(import.meta.dirname, ".."),
    command:
      "node node_modules/typescript/bin/tsc --noEmit && node node_modules/vite/bin/vite.js build --mode integration-local --outDir .ui-preview-dist && node node_modules/vite/bin/vite.js preview --outDir .ui-preview-dist --host 127.0.0.1 --port 4176 --strictPort",
    url: "http://127.0.0.1:4176",
    reuseExistingServer: false,
    timeout: 120_000,
  },
});
