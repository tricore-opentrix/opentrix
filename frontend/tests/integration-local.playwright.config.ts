// SPDX-FileCopyrightText: 2026 TRICORE contributors
//
// SPDX-License-Identifier: Apache-2.0

import { defineConfig } from "@playwright/test";
import { resolve } from "node:path";

// Run build:integration-local first. Exercise the real production entry with
// intercepted BFF responses; this suite does not establish OIDC/LIVE acceptance.
export default defineConfig({
  testDir: ".",
  testMatch: "integration-local.spec.ts",
  workers: 1,
  reporter: "list",
  outputDir: "../playwright-report/issue-233",
  use: {
    baseURL: "https://localhost:9443",
    serviceWorkers: "block",
    trace: "retain-on-failure",
  },
  projects: [
    { name: "integration-local", metadata: { integrationLocalUI: true } },
  ],
  webServer: {
    cwd: resolve(import.meta.dirname, ".."),
    command:
      "node node_modules/vite/bin/vite.js preview --host 127.0.0.1 --port 4175 --strictPort",
    url: "http://127.0.0.1:4175",
    reuseExistingServer: false,
  },
});
