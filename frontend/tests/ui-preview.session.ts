// SPDX-FileCopyrightText: 2026 TRICORE contributors
// SPDX-License-Identifier: Apache-2.0
import { test, expect } from "@playwright/test";
import {
  helpdeskRoot,
  installIntegrationLocalFixture,
  previewOrigin,
} from "./integration-local-fixture";

test("interactive UI Preview (close browser or Ctrl+C to stop)", async ({
  context,
  page,
}) => {
  await installIntegrationLocalFixture(context, {
    interactive: true,
    assetPort: 4176,
  });
  await page.goto(helpdeskRoot);
  await expect(page.locator(".helpdesk-login-story")).toBeVisible();
  console.log(
    `\nUI Preview ready: ${previewOrigin}${helpdeskRoot}\nUse this Playwright Chromium window. BFF/OIDC are simulated; external traffic is blocked.\nScreens: /__ui_preview__/login | list | create | detail\nReset: /__ui_preview__/reset. Close the browser or press Ctrl+C to stop.\n`,
  );
  await page.waitForEvent("close", { timeout: 0 });
});
