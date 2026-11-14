// SPDX-FileCopyrightText: 2026 TRICORE contributors
//
// SPDX-License-Identifier: Apache-2.0

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { helpdeskId, helpdeskWire } from "../../test/helpdeskFixtures";
import LocalHelpdeskIntegration from "./LocalHelpdeskIntegration";

beforeEach(() => vi.stubGlobal("location", new URL("https://localhost:8443")));
afterEach(() => {
  document
    .querySelectorAll('form[action$="/bff/logout"]')
    .forEach((form) => form.remove());
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});
function mount(path = "/mvp/helpdesk") {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <LocalHelpdeskIntegration />
    </MemoryRouter>,
  );
}

it("posts session CSRF through browser logout navigation and offers login after returning", async () => {
  const submit = vi
    .spyOn(HTMLFormElement.prototype, "submit")
    .mockImplementation(function (this: HTMLFormElement) {
      expect(this.method).toBe("post");
      expect(this.getAttribute("action")).toBe(
        "https://localhost:8443/bff/logout",
      );
      expect(new FormData(this).get("_csrf")).toBe("csrf-test");
      expect(this.isConnected).toBe(true);
    });
  const fetcher = vi
    .fn<typeof fetch>()
    .mockImplementation(async (url) =>
      Response.json(
        url === "/bff/session"
          ? { authenticated: true, csrfToken: "csrf-test" }
          : { items: [], nextCursor: null },
      ),
    );
  vi.stubGlobal("fetch", fetcher);
  const view = mount();
  expect(
    screen.queryByRole("button", { name: "Đăng xuất" }),
  ).not.toBeInTheDocument();
  const logout = await screen.findByRole("button", { name: "Đăng xuất" });
  await userEvent.dblClick(logout);
  expect(submit).toHaveBeenCalledTimes(1);
  expect(logout).toBeDisabled();
  // Keep the form connected until navigation; removing it cancels browser POST.
  expect(
    document.querySelector('form[action$="/bff/logout"]'),
  ).toBeInTheDocument();
  // Simulate the provider returning to the app with the BFF session ended.
  view.unmount();
  fetcher.mockResolvedValue(Response.json({ authenticated: false }));
  mount();
  expect(
    await screen.findByRole("link", { name: "Đăng nhập" }),
  ).toHaveAttribute("href", "/oauth2/authorization/keycloak");
  expect(
    screen.queryByRole("button", { name: "Đăng xuất" }),
  ).not.toBeInTheDocument();
  expect(document.querySelectorAll("h1")).toHaveLength(1);
  expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
    "Yêu cầu hỗ trợ IT",
  );
  expect(document.querySelector("h1 h1")).toBeNull();
});

it("reports a failed logout submission without pretending the session ended", async () => {
  vi.spyOn(HTMLFormElement.prototype, "submit").mockImplementation(() => {
    throw new Error("blocked");
  });
  vi.stubGlobal(
    "fetch",
    vi
      .fn<typeof fetch>()
      .mockImplementation(async (url) =>
        Response.json(
          url === "/bff/session"
            ? { authenticated: true, csrfToken: "csrf-test" }
            : { items: [], nextCursor: null },
        ),
      ),
  );
  mount();
  await userEvent.click(
    await screen.findByRole("button", { name: "Đăng xuất" }),
  );
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Không thể đăng xuất",
  );
  expect(screen.getByRole("button", { name: "Đăng xuất" })).toBeEnabled();
  expect(
    screen.queryByRole("link", { name: "Đăng nhập" }),
  ).not.toBeInTheDocument();
});

it("requires the real BFF session even when a demo persona is set", async () => {
  sessionStorage.setItem("dxos-demo-role", "processor");
  const fetcher = vi
    .fn<typeof fetch>()
    .mockResolvedValue(Response.json({ authenticated: false }));
  vi.stubGlobal("fetch", fetcher);
  mount();
  expect(
    await screen.findByRole("link", { name: "Đăng nhập" }),
  ).toHaveAttribute("href", "/oauth2/authorization/keycloak");
  expect(
    screen.queryByRole("button", { name: "Đăng xuất" }),
  ).not.toBeInTheDocument();
  expect(fetcher).toHaveBeenCalledTimes(1);
});

it("creates once through BFF without a demo role and renders only the returned request", async () => {
  const fetcher = vi
    .fn<typeof fetch>()
    .mockImplementation(async (url, init) => {
      if (url === "/bff/session")
        return Response.json({ authenticated: true, csrfToken: "csrf-test" });
      if (init?.method === "POST")
        return Response.json(helpdeskWire(), { status: 201 });
      if (String(url).includes("?limit="))
        return Response.json({ items: [helpdeskWire()], nextCursor: null });
      if (String(url).endsWith("/history")) return Response.json([]);
      return Response.json(helpdeskWire());
    });
  vi.stubGlobal("fetch", fetcher);
  mount("/mvp/helpdesk/new");
  const user = userEvent.setup();
  await user.type(
    await screen.findByLabelText(/Tiêu đề/),
    "Disposable integration test",
  );
  await user.type(
    screen.getByLabelText(/Mô tả/),
    "Disposable test description",
  );
  await user.click(screen.getByRole("button", { name: "Gửi yêu cầu IT" }));
  await waitFor(() =>
    expect(
      fetcher.mock.calls.filter(([, init]) => init?.method === "POST"),
    ).toHaveLength(1),
  );
  expect(sessionStorage.getItem("dxos-demo-role")).toBeNull();
  expect(
    fetcher.mock.calls.find(([, init]) => init?.method === "POST"),
  ).toEqual([
    "/bff/api/v1/mvp/requests",
    expect.objectContaining({
      headers: expect.objectContaining({ "X-CSRF-TOKEN": "csrf-test" }),
    }),
  ]);
  expect(await screen.findByText(helpdeskId)).toBeInTheDocument();
});

it("expires the local session on API 401 and removes the request UI", async () => {
  const fetcher = vi
    .fn<typeof fetch>()
    .mockResolvedValueOnce(
      Response.json({ authenticated: true, csrfToken: "csrf-test" }),
    )
    .mockResolvedValueOnce(new Response("", { status: 401 }));
  vi.stubGlobal("fetch", fetcher);
  mount();
  expect(
    await screen.findByRole("link", { name: "Đăng nhập" }),
  ).toBeInTheDocument();
  expect(
    screen.queryByRole("link", { name: "Tạo yêu cầu IT" }),
  ).not.toBeInTheDocument();
  expect(
    screen.queryByRole("button", { name: "Đăng xuất" }),
  ).not.toBeInTheDocument();
  expect(fetcher).toHaveBeenCalledTimes(2);
});

it("shows a session network error without falling back to mocks", async () => {
  const fetcher = vi
    .fn<typeof fetch>()
    .mockRejectedValue(new TypeError("offline"));
  vi.stubGlobal("fetch", fetcher);
  mount();
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Không thể kiểm tra phiên BFF",
  );
  expect(
    screen.queryByRole("button", { name: "Đăng xuất" }),
  ).not.toBeInTheDocument();
  expect(fetcher).toHaveBeenCalledTimes(1);
});

it("keeps an unknown create blocked after navigation without replay", async () => {
  const fetcher = vi
    .fn<typeof fetch>()
    .mockImplementation(async (url, init) => {
      if (url === "/bff/session")
        return Response.json({ authenticated: true, csrfToken: "csrf-test" });
      if (init?.method === "POST")
        return Response.json(
          { code: "COMMIT_OUTCOME_UNKNOWN" },
          { status: 503 },
        );
      return Response.json({ items: [], nextCursor: null });
    });
  vi.stubGlobal("fetch", fetcher);
  mount("/mvp/helpdesk/new");
  const user = userEvent.setup();
  await user.type(
    await screen.findByLabelText(/Tiêu đề/),
    "Disposable unknown write",
  );
  await user.type(
    screen.getByLabelText(/Mô tả/),
    "Connection lost after commit",
  );
  await user.click(screen.getByRole("button", { name: "Gửi yêu cầu IT" }));
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Chưa xác định kết quả ghi",
  );
  expect(screen.getByRole("button", { name: "Gửi yêu cầu IT" })).toBeDisabled();
  await user.click(screen.getByRole("link", { name: "Danh sách Helpdesk" }));
  await user.click(await screen.findByRole("link", { name: "Tạo yêu cầu IT" }));
  expect(screen.getByRole("button", { name: "Gửi yêu cầu IT" })).toBeDisabled();
  expect(
    fetcher.mock.calls.filter(([, init]) => init?.method === "POST"),
  ).toHaveLength(1);
});

it.each([
  "/mvp/helpdesk",
  "/mvp/helpdesk/new",
  `/mvp/helpdesk/${helpdeskId}`,
  "/mvp/helpdesk/unknown/route",
])(
  "labels integration-local and excludes Facility on route %s",
  async (path) => {
    const fetcher = vi.fn<typeof fetch>().mockImplementation(async (url) => {
      if (url === "/bff/session")
        return Response.json({ authenticated: true, csrfToken: "csrf-test" });
      if (String(url).endsWith("/history")) return Response.json([]);
      if (String(url).includes("?limit="))
        return Response.json({ items: [helpdeskWire()], nextCursor: null });
      return Response.json(helpdeskWire());
    });
    vi.stubGlobal("fetch", fetcher);
    mount(path);
    const badge = screen.getByLabelText("Chế độ demo: integration-local");
    expect(badge).toHaveTextContent("integration-local");
    await waitFor(() => {
      expect(
        screen.queryByText("Đang kiểm tra phiên…"),
      ).not.toBeInTheDocument();
    });
    expect(
      await screen.findByText(
        "Môi trường demo integration-local · dữ liệu dùng một lần",
      ),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "OpenTrix" })).toBeVisible();
    expect(document.body).not.toHaveTextContent(/service\s*desk/i);
    expect(document.body).not.toHaveTextContent(/DX-OS|MVP|University/);
    if (path.endsWith("unknown/route"))
      expect(
        screen.getByText("Không tìm thấy trang yêu cầu hỗ trợ IT"),
      ).toBeVisible();
    if (path.endsWith(helpdeskId))
      expect(
        await screen.findByText(
          "Thông tin và tiến trình xử lý yêu cầu hỗ trợ IT.",
        ),
      ).toBeInTheDocument();
    expect(
      screen.queryByText(/service kiểm thử|phiên kiểm thử/),
    ).not.toBeInTheDocument();
    expect(screen.queryByText(/Cơ sở vật chất/i)).not.toBeInTheDocument();
    expect(
      screen.queryByRole("link", { name: /Facility/i }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("radio", { name: /Facility|Cơ sở vật chất/i }),
    ).not.toBeInTheDocument();
  },
);
