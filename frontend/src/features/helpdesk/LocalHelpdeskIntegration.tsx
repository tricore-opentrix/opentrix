// SPDX-FileCopyrightText: 2026 TRICORE contributors
//
// SPDX-License-Identifier: Apache-2.0

import { useEffect, useRef, useState } from "react";
import { Link, NavLink, Navigate, Route, Routes } from "react-router-dom";
import { ArrowRight, Check, ListTodo, LogOut, Plus } from "lucide-react";
import { PortalProvider, usePortal } from "../../context";
import cloverLogo from "../../assets/opentrix-clover.svg";
import { HelpdeskRequestService } from "../../services/mvp/HelpdeskRequestService";
import { HelpdeskApiClient } from "../../services/mvp/http/HelpdeskApiClient";
import {
  bootstrapHelpdeskSession,
  logoutHelpdeskSession,
  sameOriginHelpdeskTransport,
} from "../../services/mvp/http/sameOriginTransport";
import { HelpdeskPortal } from "./HelpdeskPortal";
import "./helpdesk-local.css";

function RequestIllustration() {
  return (
    <div className="helpdesk-illustration" aria-hidden="true">
      <span />
      <span />
      <span />
      <i>
        <Check size={32} strokeWidth={3} />
      </i>
    </div>
  );
}

function Login({ sessionExpired = false }: { sessionExpired?: boolean }) {
  return (
    <section
      className="panel helpdesk-login-card"
      aria-labelledby="helpdesk-login-title"
    >
      <div className="helpdesk-login-story">
        <RequestIllustration />
        <p>
          Gửi yêu cầu, theo dõi tiến độ và xác nhận khi sự cố đã được xử lý —
          một nơi duy nhất cho hỗ trợ IT nội bộ.
        </p>
      </div>
      <div className="helpdesk-login-form">
        <p className="helpdesk-kicker">Chào mừng đến OpenTrix</p>
        <h1 id="helpdesk-login-title">Yêu cầu hỗ trợ IT</h1>
        {sessionExpired ? (
          <p role="status">
            Phiên hỗ trợ đã hết hạn. Phiên Keycloak có thể vẫn đang hoạt động;
            đăng nhập lại có thể quay về tài khoản cũ. Để đổi vai trò, hãy đăng
            xuất khỏi Keycloak trước khi đăng nhập bằng tài khoản khác.
          </p>
        ) : (
          <p>Đăng nhập bằng tài khoản tổ chức để tiếp tục.</p>
        )}
        <a className="button primary" href="/oauth2/authorization/keycloak">
          Đăng nhập <ArrowRight size={16} aria-hidden="true" />
        </a>
        <p className="helpdesk-login-note">
          Xác thực qua tài khoản tổ chức. OpenTrix không lưu mật khẩu của bạn.
        </p>
      </div>
    </section>
  );
}

function SessionPortal() {
  const { sessionExpired } = usePortal();
  if (sessionExpired) return <Login sessionExpired />;
  return (
    <Routes>
      <Route
        path="/mvp/helpdesk/*"
        element={<HelpdeskPortal mode="integration-local" />}
      />
      <Route path="*" element={<Navigate to="/mvp/helpdesk" replace />} />
    </Routes>
  );
}

/** Separate local composition: no demo persona or mock service grants access. */
export default function LocalHelpdeskIntegration() {
  const [session, setSession] = useState<
    | "loading"
    | "anonymous"
    | "expired"
    | "failed"
    | { service: HelpdeskRequestService; csrfToken: string }
  >("loading");
  const logoutStarted = useRef(false);
  const [loggingOut, setLoggingOut] = useState(false);
  const [logoutError, setLogoutError] = useState("");
  function logout() {
    if (typeof session === "string" || logoutStarted.current) return;
    logoutStarted.current = true;
    setLoggingOut(true);
    setLogoutError("");
    try {
      logoutHelpdeskSession(session.csrfToken);
    } catch {
      logoutStarted.current = false;
      setLoggingOut(false);
      setLogoutError("Không thể đăng xuất. Vui lòng thử lại.");
    }
  }
  useEffect(() => {
    let active = true;
    bootstrapHelpdeskSession()
      .then((result) => {
        if (!active) return;
        setSession(
          result
            ? {
                csrfToken: result.csrfToken,
                service: new HelpdeskRequestService(
                  new HelpdeskApiClient(
                    sameOriginHelpdeskTransport(result.csrfToken),
                    () => {
                      if (active) setSession("expired");
                    },
                  ),
                ),
              }
            : "anonymous",
        );
      })
      .catch(() => {
        if (active) setSession("failed");
      });
    return () => {
      active = false;
    };
  }, []);
  return (
    <div className="helpdesk-local">
      <a href="#main-content" className="skip-link">
        Đến nội dung chính
      </a>
      <header className="helpdesk-header">
        <Link to="/mvp/helpdesk" className="helpdesk-brand" aria-label="OpenTrix IT Helpdesk">
          <img
            className="helpdesk-brand-mark"
            src={cloverLogo}
            alt=""
            width="40"
            height="40"
          />
          <span className="helpdesk-brand-name">OpenTrix</span>
          <span className="helpdesk-brand-product">IT Helpdesk</span>
        </Link>
        <span
          className="environment"
          aria-label="Chế độ demo: integration-local"
        >
          <span />
          integration-local
        </span>
        {typeof session !== "string" && (
          <button
            className="button secondary"
            disabled={loggingOut}
            onClick={logout}
          >
            <LogOut size={16} aria-hidden="true" />
            {loggingOut ? "Đang đăng xuất…" : "Đăng xuất"}
          </button>
        )}
      </header>
      <div
        className={`helpdesk-workspace ${typeof session === "string" ? "helpdesk-workspace-public" : ""}`}
      >
        {typeof session !== "string" && (
          <aside className="helpdesk-navigation">
            <nav aria-label="Điều hướng Helpdesk">
              <NavLink to="/mvp/helpdesk" end>
                <ListTodo size={18} aria-hidden="true" />
                Danh sách Helpdesk
              </NavLink>
              <NavLink to="/mvp/helpdesk/new">
                <Plus size={18} aria-hidden="true" />
                Tạo yêu cầu
              </NavLink>
            </nav>
            <p>Hỗ trợ IT nội bộ</p>
          </aside>
        )}
        <main id="main-content" className="helpdesk-content" tabIndex={-1}>
          {logoutError && (
            <p className="inline-notice" role="alert">
              {logoutError}
            </p>
          )}
          {session === "loading" ? (
            <p role="status">Đang kiểm tra phiên…</p>
          ) : session === "failed" ? (
            <p role="alert">
              Không thể kiểm tra phiên BFF. Kiểm tra HTTPS và kết nối, sau đó
              tải lại trang.
            </p>
          ) : typeof session === "string" ? (
            <Login sessionExpired={session === "expired"} />
          ) : (
            <PortalProvider helpdeskService={session.service} helpdeskSession>
              <SessionPortal />
            </PortalProvider>
          )}
        </main>
      </div>
      <footer className="helpdesk-footer">
        OpenTrix · mã nguồn mở Apache-2.0 ·{" "}
        <a href="https://github.com/tricore-opentrix/opentrix">GitHub</a>
      </footer>
    </div>
  );
}
