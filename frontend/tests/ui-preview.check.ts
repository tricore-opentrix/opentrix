// SPDX-FileCopyrightText: 2026 TRICORE contributors
// SPDX-License-Identifier: Apache-2.0
import { test, expect } from "@playwright/test";
import { helpdeskId, helpdeskWire } from "../src/test/helpdeskFixtures";
import {
  helpdeskRoot,
  installIntegrationLocalFixture,
  previewOrigin,
} from "./integration-local-fixture";

test("four real screens, create, logout, reload and fail-closed network", async ({
  context,
  page,
}) => {
  const fixture = await installIntegrationLocalFixture(context, {
    interactive: true,
    assetPort: 4176,
  });
  await page.goto(helpdeskRoot);
  await expect(page.locator(".helpdesk-login-story")).toBeVisible();
  await page.getByRole("link", { name: "Đăng nhập", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Yêu cầu hỗ trợ IT", exact: true }),
  ).toBeVisible();
  await page.getByRole("link", { name: helpdeskWire().title }).click();
  await expect(
    page.getByRole("heading", { name: helpdeskWire().title, exact: true }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Tạo yêu cầu", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Tạo yêu cầu IT Support" }),
  ).toBeVisible();
  await page.getByLabel("Tiêu đề yêu cầu").fill("Preview create check");
  await page
    .getByLabel("Mô tả chi tiết")
    .fill("Test-only request in Playwright memory");
  await page.getByRole("button", { name: "Gửi yêu cầu IT" }).click();
  await page.getByRole("link", { name: "Preview create check" }).click();
  await expect(
    page.getByRole("heading", { name: "Preview create check" }),
  ).toBeVisible();
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Preview create check" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Đăng xuất", exact: true }).click();
  await expect(page.locator(".helpdesk-login-story")).toBeVisible();
  for (const screen of ["login", "list", "create", "detail"]) {
    await page.goto(`/__ui_preview__/${screen}`);
    await expect(page.locator(".helpdesk-login-story")).toHaveCount(
      screen === "login" ? 1 : 0,
    );
    await expect(page).toHaveURL(
      `${previewOrigin}${helpdeskRoot}${screen === "create" ? "/new" : screen === "detail" ? `/${helpdeskId}` : ""}`,
    );
  }
  const statuses = await page.evaluate(async () => {
    const external = await fetch("https://example.com/blocked-preview").then(
      () => false,
      () => true,
    );
    const unapproved = await fetch("/api/blocked-preview", {
      method: "POST",
    }).then(
      () => false,
      () => true,
    );
    const csrf = await fetch("/bff/api/v1/mvp/requests", {
      method: "POST",
      body: "{}",
    });
    return { external, unapproved, csrf: csrf.status };
  });
  expect(statuses).toEqual({ external: true, unapproved: true, csrf: 403 });
  expect(fixture.blocked).toHaveLength(2);
  await page.goto("/__ui_preview__/reset");
  await page.getByRole("link", { name: "Đăng nhập", exact: true }).click();
  await expect(
    page.getByRole("link", { name: "Preview create check" }),
  ).toHaveCount(0);
});

test("synthetic 401 and 409 exercise unchanged application error handling", async ({
  context,
  page,
}) => {
  await installIntegrationLocalFixture(context, {
    interactive: true,
    assetPort: 4176,
  });
  await page.goto("/__ui_preview__/401");
  await expect(page.locator(".helpdesk-login-story")).toBeVisible();
  await page.goto("/__ui_preview__/409");
  await page.getByLabel("Tiêu đề yêu cầu").fill("Conflict preview check");
  await page
    .getByLabel("Mô tả chi tiết")
    .fill("This record must not be created");
  const reply = page.waitForResponse(
    (response) =>
      response.url().endsWith("/bff/api/v1/mvp/requests") &&
      response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Gửi yêu cầu IT" }).click();
  expect((await reply).status()).toBe(409);
  await expect(
    page.getByRole("button", { name: "Gửi yêu cầu IT" }),
  ).toBeDisabled();
  await page.goto("/__ui_preview__/list");
  await expect(
    page.getByRole("heading", { name: "Yêu cầu hỗ trợ IT", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Conflict preview check" }),
  ).toHaveCount(0);
});
