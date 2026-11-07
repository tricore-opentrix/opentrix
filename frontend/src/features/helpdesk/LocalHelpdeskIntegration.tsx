// SPDX-FileCopyrightText: 2026 TRICORE contributors
//
// SPDX-License-Identifier: Apache-2.0

import { useEffect, useState } from "react";
import { Link, Navigate, Route, Routes } from "react-router-dom";
import { PortalProvider, usePortal } from "../../context";
import { HelpdeskRequestService } from "../../services/mvp/HelpdeskRequestService";
import { HelpdeskApiClient } from "../../services/mvp/http/HelpdeskApiClient";
import { BffSessionClient } from "../../services/mvp/bff/BffSessionClient";
import { createHelpdeskBffTransport } from "../../services/mvp/bff/createHelpdeskBffTransport";
import { HelpdeskPortal } from "./HelpdeskPortal";

function Login() {
  return (
    <p role="status">
      Phiên chưa được xác thực hoặc đã hết hạn.{" "}
      <a href="/oauth2/authorization/keycloak">Đăng nhập Keycloak</a>
    </p>
  );
}

function SessionPortal() {
  const { sessionExpired } = usePortal();
  if (sessionExpired) return <Login />;
  return (
    <Routes>
      <Route path="/mvp/helpdesk/*" element={<HelpdeskPortal />} />
      <Route path="*" element={<Navigate to="/mvp/helpdesk" replace />} />
    </Routes>
  );
}

function requireLocalHttps() {
  if (
    location.protocol !== "https:" ||
    !["localhost", "127.0.0.1", "[::1]"].includes(location.hostname)
  )
    throw new Error("Helpdesk integration requires a trusted local HTTPS origin.");
}

/**
 * Integration-local composition only. MOCK remains the default entry point.
 * This local mode is not authorization for public LIVE/APISIX integration.
 * The BFF owns OIDC credentials; the browser holds only per-session CSRF in memory.
 */
export default function LocalHelpdeskIntegration() {
  const [session, setSession] = useState<
    "loading" | "anonymous" | "expired" | "failed" | HelpdeskRequestService
  >("loading");

  useEffect(() => {
    let active = true;
    const bffSession = new BffSessionClient((path, init) => fetch(path, init));
    try {
      requireLocalHttps();
    } catch {
      setSession("failed");
      return () => {
        active = false;
        bffSession.invalidate();
      };
    }

    bffSession
      .load()
      .then((state) => {
        if (!active) return;
        if (!state.authenticated) {
          setSession("anonymous");
          return;
        }
        setSession(
          new HelpdeskRequestService(
            new HelpdeskApiClient(
              createHelpdeskBffTransport(bffSession, (path, init) =>
                fetch(path, init),
              ),
              () => {
                if (!active) return;
                bffSession.invalidate();
                setSession("expired");
              },
            ),
          ),
        );
      })
      .catch(() => {
        if (active) setSession("failed");
      });

    return () => {
      active = false;
      bffSession.invalidate();
    };
  }, []);

  return (
    <main id="main-content" className="page">
      <header>
        <h1>DX-OS · Helpdesk integration local</h1>
        <Link to="/mvp/helpdesk">Danh sách Helpdesk</Link>
      </header>
      {session === "loading" ? (
        <p role="status">Đang kiểm tra phiên…</p>
      ) : session === "failed" ? (
        <p role="alert">
          Không thể kiểm tra phiên BFF. Kiểm tra HTTPS và kết nối, sau đó tải
          lại trang.
        </p>
      ) : typeof session === "string" ? (
        <Login />
      ) : (
        <PortalProvider helpdeskService={session} helpdeskSession>
          <SessionPortal />
        </PortalProvider>
      )}
    </main>
  );
}
