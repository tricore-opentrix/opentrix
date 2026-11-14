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

test("list: complete UUIDs stay inside their cells without covering titles (intercepted BFF)", async ({
  page,
}) => {
  const ids = [helpdeskId, "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"];
  const titles = [helpdeskWire().title, "Yêu cầu " + "x".repeat(192)];
  await page.route("**/bff/api/v1/mvp/requests?*", (route) =>
    route.fulfill({
      json: {
        items: ids.map((id, i) => helpdeskWire({ id, title: titles[i] })),
        nextCursor: null,
      },
    }),
  );
  await page.goto("/mvp/helpdesk");
  const rows = page.locator(".helpdesk-list-panel tbody tr");
  await expect(rows).toHaveCount(ids.length);
  for (const width of [1920, 1440, 1280, 1024, 768, 600, 390, 320]) {
    await page.setViewportSize({ width, height: 1000 });
    await page.evaluate(() => document.fonts.ready);
    for (let i = 0; i < ids.length; i++) {
      const row = rows.nth(i);
      await expect(row.locator(".request-id")).toHaveText(ids[i]);
      await expect(row.getByRole("link")).toHaveAttribute(
        "href",
        `/mvp/helpdesk/${ids[i]}`,
      );
      const fits = await row.evaluate((element) => {
        const code = element.querySelector(".request-id")!;
        const cell = code.closest("td")!.getBoundingClientRect();
        const title = element
          .querySelector(".request-title")!
          .getBoundingClientRect();
        const range = document.createRange();
        range.selectNodeContents(code);
        const fragments = Array.from(range.getClientRects());
        return (
          fragments.length > 0 &&
          fragments.every(
            (rect) =>
              rect.left >= cell.left - 1 &&
              rect.right <= cell.right + 1 &&
              rect.top >= cell.top - 1 &&
              rect.bottom <= cell.bottom + 1 &&
              (rect.right <= title.left ||
                rect.left >= title.right ||
                rect.bottom <= title.top ||
                rect.top >= title.bottom),
          )
        );
      });
      expect(fits, `UUID row ${i + 1} at ${width}px`).toBe(true);
    }
    await page.screenshot({
      path: test.info().outputPath(`list-uuid-${width}.png`),
      fullPage: true,
    });
  }
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
      const logoSvg = await page.evaluate(
        async (src) => (await fetch(src)).text(),
        (await logo.getAttribute("src")) as string,
      );
      // Three closed leaf paths and a separate open stem; no fourth leaf.
      expect(
        (logoSvg.match(/fill="#(?:c4f3df|8fe3c2|a8ecd0)"/g) ?? []).length,
      ).toBe(3);
      expect(logoSvg).toContain("rotate(120 20 21)");
      expect(logoSvg).toContain("rotate(240 20 21)");
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
