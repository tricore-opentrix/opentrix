// SPDX-FileCopyrightText: 2026 TRICORE contributors
//
// SPDX-License-Identifier: Apache-2.0

import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { helpdeskId, helpdeskWire } from "../src/test/helpdeskFixtures";
import { installIntegrationLocalFixture } from "./integration-local-fixture";

test.beforeEach(async ({ context }) => {
  test.skip(
    !test.info().project.metadata.integrationLocalUI,
    "Requires integration-local build and integration-local.playwright.config.ts.",
  );
  await installIntegrationLocalFixture(context);
});

for (const screen of ["login", "list", "create", "detail"] as const) {
  test(`${screen}: responsive production UI and accessibility (intercepted BFF)`, async ({
    page,
  }) => {
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    if (screen === "login") {
      await page.route("**/bff/session", (route) =>
        route.fulfill({ json: { authenticated: false } }),
      );
    }
    const path =
      screen === "create"
        ? "/new"
        : screen === "detail"
          ? `/${helpdeskId}`
          : "";
    await page.goto(`/mvp/helpdesk${path}`);
    await expect(page).toHaveTitle("IT Helpdesk · OpenTrix");
    await expect(
      page.getByRole("link", {
        name: "OpenTrix IT Helpdesk",
        exact: true,
      }),
    ).toBeVisible();
    await expect(page.getByText("Đang kiểm tra phiên…")).toHaveCount(0);
    await expect(
      page.getByLabel("Chế độ demo: integration-local"),
    ).toBeVisible();
    if (screen === "login") {
      await expect(page.locator(".helpdesk-login-story")).toBeVisible();
      await expect(
        page.getByRole("navigation", { name: "Điều hướng Helpdesk" }),
      ).toHaveCount(0);
      await expect(
        page.getByRole("link", { name: "Đăng nhập", exact: true }),
      ).toHaveAttribute("href", "/oauth2/authorization/keycloak");
      await expect(page.getByRole("button", { name: "Đăng xuất" })).toHaveCount(
        0,
      );
    } else {
      await expect(
        page.getByRole("navigation", { name: "Điều hướng Helpdesk" }),
      ).toBeVisible();
      await expect(
        page.getByRole("button", { name: "Đăng xuất" }),
      ).toBeVisible();
      await expect(
        page.getByRole("heading", {
          name:
            screen === "list"
              ? "Yêu cầu hỗ trợ IT"
              : screen === "create"
                ? "Tạo yêu cầu IT Support"
                : "Không thể lưu báo cáo",
          exact: true,
        }),
      ).toBeVisible();
      if (screen !== "create")
        await expect(page.getByText("Đã tiếp nhận").first()).toBeVisible();
    }
    await expect(page.locator("body")).not.toContainText(
      /DX-OS|MVP|University|Facility|Workflow version|service\s*desk/i,
    );
    for (const width of [1440, 768, 390, 320]) {
      await page.setViewportSize({ width, height: 1000 });
      await page.evaluate(() => document.fonts.ready);
      const brand = page.getByRole("link", {
        name: "OpenTrix IT Helpdesk",
        exact: true,
      });
      await expect(brand).toContainText("OpenTrix");
      await expect(brand).toContainText("IT Helpdesk");
      const logo = brand.locator("img");
      await expect(logo).toHaveAttribute("alt", "");
      expect(
        await logo.evaluate(
          (img: HTMLImageElement) => img.complete && img.naturalWidth > 0,
        ),
      ).toBe(true);
      const logoShape = await page.evaluate(
        async (src) => {
          const svg = new DOMParser().parseFromString(
            await (await fetch(src)).text(),
            "image/svg+xml",
          );
          return {
            viewBox: svg.documentElement.getAttribute("viewBox"),
            leaves: svg.querySelectorAll('path[fill]:not([fill="none"])')
              .length,
            stems: svg.querySelectorAll('path[fill="none"][stroke]').length,
            parseErrors: svg.querySelectorAll("parsererror").length,
          };
        },
        (await logo.getAttribute("src")) as string,
      );
      expect(logoShape).toEqual({
        viewBox: "0 0 40 40",
        leaves: 3,
        stems: 1,
        parseErrors: 0,
      });
      const brandBox = await brand.boundingBox();
      const logoBox = await logo.boundingBox();
      expect(logoBox?.width).toBe(40);
      expect(logoBox?.height).toBe(40);
      expect(brandBox!.x).toBeGreaterThanOrEqual(0);
      expect(brandBox!.x + brandBox!.width).toBeLessThanOrEqual(width);
      await page.getByRole("link", { name: "Đến nội dung chính" }).focus();
      await expect(
        page.getByRole("link", { name: "Đến nội dung chính" }),
      ).toBeFocused();
      await page.keyboard.press("Tab");
      await expect(brand).toBeFocused();
      await expect(brand).toHaveCSS("outline-style", "solid");
      await brand.blur();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBe(true);
      const result = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze();
      expect(
        result.violations.map(({ id, nodes }) => ({
          id,
          targets: nodes.map(({ target }) => target),
        })),
      ).toEqual([]);
      await expect(
        page.locator(".helpdesk-local .button.primary").first(),
      ).toHaveCSS("background-color", "rgb(17, 110, 104)");
      await page.screenshot({
        path: test.info().outputPath(`${screen}-${width}.png`),
        fullPage: true,
      });
    }
    expect(errors).toEqual([]);
  });
}

// Regression for UUID cells inheriting the shared table's nowrap rule.
test("long UUID and title stay inside their cells at desktop widths", async ({
  page,
}) => {
  const record = helpdeskWire({
    title: "Yêu cầu hỗ trợ với tiêu đề rất dài ".repeat(5),
  });
  await page.route("**/bff/api/v1/mvp/requests?*", (route) =>
    route.fulfill({ json: { items: [record], nextCursor: null } }),
  );
  await page.goto("/mvp/helpdesk");
  await expect(page.locator(".helpdesk-request-code")).toHaveText(helpdeskId);
  for (const width of [1024, 1280, 1366, 1440, 1920]) {
    await page.setViewportSize({ width, height: 1000 });
    await page.evaluate(() => document.fonts.ready);
    const code = page.locator(".helpdesk-request-code");
    await expect(code).toHaveCSS("white-space", "normal");
    for (const cell of [code, page.locator('td[data-label="Yêu cầu"]')]) {
      expect(
        await cell.evaluate(
          (element) => element.scrollWidth <= element.clientWidth,
        ),
      ).toBe(true);
    }
    await page.screenshot({
      path: test.info().outputPath(`uuid-list-${width}.png`),
      fullPage: true,
    });
  }
});

for (const sample of [
  {
    label: "provided names",
    fields: {
      requesterDisplayName: "Người yêu cầu demo",
      assigneeDisplayName: "Người xử lý demo",
    },
    requester: "Người yêu cầu demo",
    assignee: "Người xử lý demo",
  },
  {
    label: "missing names",
    fields: { requesterDisplayName: null, assigneeDisplayName: null },
    requester: "Chưa có tên hiển thị",
    assignee: "Chưa có tên hiển thị",
  },
  {
    label: "blank names",
    fields: { requesterDisplayName: "   ", assigneeDisplayName: "   " },
    requester: "Chưa có tên hiển thị",
    assignee: "Chưa có tên hiển thị",
  },
  {
    label: "unassigned",
    fields: { requesterDisplayName: null, assigneeId: null },
    requester: "Chưa có tên hiển thị",
    assignee: "Chưa phân công",
  },
]) {
  test(`list displays ${sample.label} from the response`, async ({ page }) => {
    await page.route("**/bff/api/v1/mvp/requests?*", (route) =>
      route.fulfill({
        json: { items: [helpdeskWire(sample.fields)], nextCursor: null },
      }),
    );
    await page.goto("/mvp/helpdesk");
    await expect(page.locator('td[data-label="Người yêu cầu"]')).toHaveText(
      sample.requester,
    );
    await expect(page.locator('td[data-label="Người xử lý"]')).toHaveText(
      sample.assignee,
    );
  });
}
