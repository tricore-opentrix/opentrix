// SPDX-FileCopyrightText: 2026 TRICORE contributors
//
// SPDX-License-Identifier: Apache-2.0

import { act, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  BffSessionClient,
  type BffSessionScope,
} from "../../services/mvp/bff/BffSessionClient";
import LocalHelpdeskIntegration from "./LocalHelpdeskIntegration";

// Exercise the real composition, BFF session and transport. Mock only the
// presentation child to avoid unrelated list network requests.
vi.mock("./HelpdeskPortal", () => ({
  HelpdeskPortal: () => <p data-testid="r33-mounted-helpdesk">Helpdesk mounted</p>,
}));

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((res) => {
    resolve = res;
  });
  return { promise, resolve };
}

function mount() {
  return render(
    <MemoryRouter initialEntries={["/mvp/helpdesk"]}>
      <LocalHelpdeskIntegration />
    </MemoryRouter>,
  );
}

function stubOrigin(origin: string) {
  vi.stubGlobal("location", new URL(origin));
}

function authenticated(csrfToken = "csrf-test") {
  return Response.json({ authenticated: true, csrfToken });
}

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("R33 local Portal composition security regressions (Y-R33-01)", () => {
  it.each([
    "http://localhost:8443",
    "http://127.0.0.1:8443",
    "https://portal.example.test",
    "https://127.0.0.2:8443",
  ])("blocks origin %s before any BFF session fetch", async (origin) => {
    stubOrigin(origin);
    const fetcher = vi.fn<typeof fetch>();
    vi.stubGlobal("fetch", fetcher);

    mount();

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Không thể kiểm tra phiên BFF",
    );
    expect(fetcher).not.toHaveBeenCalled();
    expect(screen.queryByTestId("r33-mounted-helpdesk")).not.toBeInTheDocument();
  });

  it.each([
    "https://localhost:8443",
    "https://127.0.0.1:8443",
    "https://[::1]:8443",
  ])("loads only on approved HTTPS loopback origin %s", async (origin) => {
    stubOrigin(origin);
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(authenticated());
    vi.stubGlobal("fetch", fetcher);

    mount();

    expect(await screen.findByTestId("r33-mounted-helpdesk")).toBeVisible();
    expect(fetcher).toHaveBeenCalledExactlyOnceWith(
      "/bff/session",
      expect.objectContaining({
        method: "GET",
        mode: "same-origin",
        credentials: "same-origin",
        redirect: "error",
        cache: "no-store",
      }),
    );
  });

  it("cannot mount a Portal for an anonymous BFF session", async () => {
    stubOrigin("https://localhost:8443");
    const fetcher = vi
      .fn<typeof fetch>()
      .mockResolvedValue(Response.json({ authenticated: false }));
    vi.stubGlobal("fetch", fetcher);

    mount();

    expect(
      await screen.findByRole("link", { name: "Đăng nhập Keycloak" }),
    ).toHaveAttribute("href", "/oauth2/authorization/keycloak");
    expect(screen.queryByTestId("r33-mounted-helpdesk")).not.toBeInTheDocument();
    expect(fetcher).toHaveBeenCalledTimes(1);
  });

  it("invalidates the real captured BFF scope on unmount", async () => {
    stubOrigin("https://localhost:8443");
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(authenticated());
    vi.stubGlobal("fetch", fetcher);
    const capture = vi.spyOn(BffSessionClient.prototype, "capture");

    const page = mount();
    expect(await screen.findByTestId("r33-mounted-helpdesk")).toBeVisible();
    expect(capture).toHaveBeenCalledTimes(1);
    const scope: BffSessionScope = capture.mock.results[0].value;
    expect(() => scope.assertActive()).not.toThrow();

    page.unmount();

    expect(() => scope.assertActive()).toThrow("STALE_SESSION");
    expect(fetcher).toHaveBeenCalledTimes(1);
  });

  it("does not compose an authenticated Portal from a late load after unmount", async () => {
    stubOrigin("https://localhost:8443");
    const pending = deferred<Response>();
    const fetcher = vi.fn<typeof fetch>().mockReturnValue(pending.promise);
    vi.stubGlobal("fetch", fetcher);
    const capture = vi.spyOn(BffSessionClient.prototype, "capture");

    const page = mount();
    expect(fetcher).toHaveBeenCalledTimes(1);
    page.unmount();

    await act(async () => {
      pending.resolve(authenticated("csrf-retired"));
    });

    expect(capture).not.toHaveBeenCalled();
    expect(screen.queryByTestId("r33-mounted-helpdesk")).not.toBeInTheDocument();
    expect(fetcher).toHaveBeenCalledTimes(1);
  });

  it("does not let a previous mount overwrite an authenticated successor", async () => {
    stubOrigin("https://localhost:8443");
    const oldResponse = deferred<Response>();
    const fetcher = vi
      .fn<typeof fetch>()
      .mockReturnValueOnce(oldResponse.promise)
      .mockResolvedValueOnce(authenticated("csrf-current"));
    vi.stubGlobal("fetch", fetcher);
    const capture = vi.spyOn(BffSessionClient.prototype, "capture");

    const previous = mount();
    previous.unmount();

    const current = mount();
    expect(await screen.findByTestId("r33-mounted-helpdesk")).toBeVisible();
    expect(capture).toHaveBeenCalledTimes(1);
    const currentScope: BffSessionScope = capture.mock.results[0].value;

    await act(async () => {
      oldResponse.resolve(authenticated("csrf-retired"));
    });

    expect(capture).toHaveBeenCalledTimes(1);
    expect(() => currentScope.assertActive()).not.toThrow();
    expect(screen.getAllByTestId("r33-mounted-helpdesk")).toHaveLength(1);
    expect(fetcher).toHaveBeenCalledTimes(2);
    current.unmount();
    expect(() => currentScope.assertActive()).toThrow("STALE_SESSION");
  });

  it("rejects a late session body completion after unmount", async () => {
    stubOrigin("https://localhost:8443");
    const pendingBody = deferred<string>();
    const response = authenticated();
    vi.spyOn(response, "text").mockReturnValue(pendingBody.promise);
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(response);
    vi.stubGlobal("fetch", fetcher);
    const capture = vi.spyOn(BffSessionClient.prototype, "capture");

    const page = mount();
    expect(fetcher).toHaveBeenCalledTimes(1);
    page.unmount();

    await act(async () => {
      pendingBody.resolve(
        JSON.stringify({ authenticated: true, csrfToken: "csrf-retired" }),
      );
    });

    expect(capture).not.toHaveBeenCalled();
    expect(screen.queryByTestId("r33-mounted-helpdesk")).not.toBeInTheDocument();
  });
});
