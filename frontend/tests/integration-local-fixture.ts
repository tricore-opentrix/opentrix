// SPDX-FileCopyrightText: 2026 TRICORE contributors
// SPDX-License-Identifier: Apache-2.0

import type { BrowserContext } from "@playwright/test";
import { randomUUID } from "node:crypto";
import { helpdeskId, helpdeskWire } from "../src/test/helpdeskFixtures";

export const previewOrigin = "https://localhost:8443";
export const helpdeskRoot = "/mvp/helpdesk";
const base = "/bff/api/v1/mvp/requests";
const csrfToken = "browser-test-only";

/** Test process only. No fixture code is imported by the React entry point. */
export async function installIntegrationLocalFixture(
  context: BrowserContext,
  { interactive = false, assetPort = 4175 } = {},
) {
  let authenticated = !interactive;
  let nextError: 401 | 409 | undefined;
  const records = new Map([[helpdeskId, helpdeskWire()]]);
  const blocked: string[] = [];
  await context.routeWebSocket("**/*", (socket) => socket.close());
  await context.route("**/*", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const path = url.pathname;
    const method = request.method();
    const reply = (status: number, json: unknown) =>
      route.fulfill({ status, json });
    // Browser redirect chains can bypass Playwright routing after their first
    // request. A fresh document navigation keeps every request intercepted.
    const redirect = (location: string) =>
      route.fulfill({
        status: 200,
        contentType: "text/html",
        headers: { "cache-control": "no-store" },
        body: `<!doctype html><script>location.replace(${JSON.stringify(location)})</script>`,
      });
    if (url.origin !== previewOrigin) {
      blocked.push(request.url());
      await route.abort("blockedbyclient");
      return;
    }
    // These controls exist only in this Playwright context, never on a server.
    if (
      interactive &&
      method === "GET" &&
      path.startsWith("/__ui_preview__/")
    ) {
      const screen = path.slice("/__ui_preview__/".length);
      if (
        !["login", "list", "create", "detail", "reset", "401", "409"].includes(
          screen,
        )
      ) {
        await reply(404, {});
        return;
      }
      nextError = undefined;
      authenticated = screen !== "login" && screen !== "reset";
      if (screen === "reset") {
        records.clear();
        records.set(helpdeskId, helpdeskWire());
      }
      if (screen === "401" || screen === "409")
        nextError = Number(screen) as 401 | 409;
      await redirect(
        screen === "detail"
          ? `${helpdeskRoot}/${helpdeskId}`
          : screen === "create" || screen === "409"
            ? `${helpdeskRoot}/new`
            : helpdeskRoot,
      );
      return;
    }
    if (
      interactive &&
      method === "GET" &&
      path === "/oauth2/authorization/keycloak"
    ) {
      authenticated = true;
      await redirect(helpdeskRoot);
      return;
    }
    if (path === "/bff/session" && method === "GET") {
      await reply(
        200,
        authenticated
          ? { authenticated: true, csrfToken }
          : { authenticated: false },
      );
      return;
    }
    if (interactive && path === "/bff/logout" && method === "POST") {
      if (
        new URLSearchParams(request.postData() ?? "").get("_csrf") !== csrfToken
      ) {
        await reply(403, {});
        return;
      }
      authenticated = false;
      await redirect(helpdeskRoot);
      return;
    }
    if (path.startsWith("/bff/")) {
      if (!interactive) {
        await reply(
          200,
          path.endsWith("/history")
            ? []
            : path === base
              ? { items: [helpdeskWire()], nextCursor: null }
              : helpdeskWire(),
        );
        return;
      }
      if (!authenticated || nextError === 401) {
        authenticated = false;
        nextError = undefined;
        await reply(401, {});
        return;
      }
      if (
        method === "POST" &&
        request.headers()["x-csrf-token"] !== csrfToken
      ) {
        await reply(403, {});
        return;
      }
      if (method === "POST" && nextError === 409) {
        nextError = undefined;
        await reply(409, {});
        return;
      }
      if (path === base && method === "GET") {
        await reply(200, { items: [...records.values()], nextCursor: null });
        return;
      }
      if (path === base && method === "POST") {
        let body;
        try {
          body = request.postDataJSON();
        } catch {
          await reply(400, {});
          return;
        }
        if (
          typeof body?.title !== "string" ||
          !body.title.trim() ||
          body.title.length > 200 ||
          typeof body?.description !== "string" ||
          !body.description.trim() ||
          body.description.length > 4000 ||
          body.requestType !== "IT_HELPDESK"
        ) {
          await reply(400, {});
          return;
        }
        const record = helpdeskWire({
          id: randomUUID(),
          title: body.title,
          description: body.description,
          state: "SUBMITTED",
          version: 0,
          assigneeId: null,
          allowedActions: [],
        });
        records.set(record.id, record);
        await reply(201, record);
        return;
      }
      const match = path.match(
        /^\/bff\/api\/v1\/mvp\/requests\/([0-9a-f-]+)(\/history)?$/i,
      );
      const record = match && records.get(match[1]);
      if (method === "GET" && record) {
        await reply(200, match?.[2] ? [] : record);
        return;
      }
      // Assignment/workflow contracts are not invented for this UI preview.
      await reply(method === "GET" ? 404 : 403, {});
      return;
    }
    if (
      method !== "GET" ||
      !(
        path === "/" ||
        path === "/index.html" ||
        path === helpdeskRoot ||
        path.startsWith(`${helpdeskRoot}/`) ||
        path.startsWith("/assets/") ||
        path === "/favicon.ico"
      )
    ) {
      blocked.push(request.url());
      await route.abort("blockedbyclient");
      return;
    }
    // Only an explicit local static server may receive a real network request.
    const response = await route.fetch({
      url: `http://127.0.0.1:${assetPort}${path}${url.search}`,
      maxRedirects: 0,
    });
    if (response.status() >= 300 && response.status() < 400) {
      await route.abort("blockedbyclient");
      return;
    }
    await route.fulfill({ response });
  });
  return { blocked };
}
