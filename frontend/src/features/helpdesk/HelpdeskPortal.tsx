// SPDX-FileCopyrightText: 2026 TRICORE contributors
//
// SPDX-License-Identifier: Apache-2.0

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type FormEvent,
} from "react";
import {
  Link,
  Route,
  Routes,
  useNavigate,
  useParams,
  useSearchParams,
} from "react-router-dom";
import { AssignmentForm } from "../../components/AssignmentForm";
import { ArrowLeft, ArrowUpRight, Monitor, Plus } from "lucide-react";
import { Empty, ErrorState, Loading, PageHeading } from "../../components/ui";
import { usePortal } from "../../context";
import { useSessionOperation } from "../../hooks/useSessionOperation";
import { helpdeskAssignmentFormProps } from "../../services/mvp/assignmentBinding";
import {
  executeWriteOnce,
  MvpApplicationError,
} from "../../services/mvp/errors";
import type { MvpHelpdeskRequestPort } from "../../services/mvp/helpdeskPortalPort";
import { stateClassName, stateLabel } from "../../services/mvp/stateLabels";
import { useHelpdeskRead } from "./useHelpdeskRead";

const ROOT = "/mvp/helpdesk";
/** ADR-017: visible copy must match the composition (MOCK seam vs BFF-backed integration-local). */
export type HelpdeskPortalMode = "mock" | "integration-local";
const COPY = {
  mock: {
    footnote: "IT Helpdesk MVP · service kiểm thử được inject · LIVE BLOCKED",
    list: "Yêu cầu IT Support trong phiên kiểm thử.",
    empty: "Tạo yêu cầu để bắt đầu phiên kiểm thử.",
    create: "Chỉ dùng dữ liệu kiểm thử; loại yêu cầu IT_HELPDESK.",
    detail: "IT Support · dữ liệu từ service kiểm thử",
  },
  "integration-local": {
    footnote: "Môi trường demo integration-local · dữ liệu dùng một lần",
    list: "Theo dõi và quản lý các yêu cầu hỗ trợ IT.",
    empty: "Tạo yêu cầu đầu tiên để bắt đầu.",
    create: "Mô tả vấn đề bạn cần hỗ trợ. Chỉ sử dụng dữ liệu demo.",
    detail: "Thông tin và tiến trình xử lý yêu cầu hỗ trợ IT.",
  },
} as const;
const CopyContext = createContext<(typeof COPY)[HelpdeskPortalMode]>(COPY.mock);
const CREATE = "helpdesk:create";
const labels = {
  triage: "Tiếp nhận",
  start: "Bắt đầu xử lý",
  resolve: "Ghi kết quả xử lý",
  confirm: "Xác nhận hoàn thành",
} as const;
type WorkflowAction = keyof typeof labels;
const validVersion = (value: number) =>
  Number.isSafeInteger(value) && value >= 0;
const validText = (value: string, max: number) =>
  value.trim().length > 0 && value.length <= max;
const personName = (name: string | null | undefined) =>
  name || "Tên không được cung cấp";

/** Shared write lock is scoped to the provider, so navigation cannot replay a
 * pending/unknown write. Only a user-requested authoritative read releases 409.
 */
function useHelpdeskWrite(key: string) {
  const portal = usePortal();
  const captureOperation = useSessionOperation();
  const currentOperation = captureOperation();
  const invoked = useRef(false);
  const acceptRead = useCallback(() => {
    invoked.current = false;
  }, []);
  const stopped = portal.helpdeskWriteStops.get(key);
  const busy = portal.helpdeskPending.has(key);
  async function run(write: () => Promise<unknown>, after: () => void) {
    if (
      !portal.helpdeskAuthenticated ||
      stopped ||
      invoked.current ||
      !portal.beginHelpdeskWrite(key)
    )
      return;
    invoked.current = true;
    const operation = captureOperation();
    try {
      await executeWriteOnce(write);
      if (operation.canUpdate()) after();
    } catch (error) {
      // executeWriteOnce always normalizes unknown write failures.
      const failure = error as MvpApplicationError;
      // An old session cannot stop its successor. Unknown writes remain stopped
      // across navigation/logout; their outcome still needs approved recovery.
      if (
        failure.code === "COMMIT_OUTCOME_UNKNOWN" ||
        (operation.isCurrent() && failure.code !== "UNAUTHENTICATED")
      )
        portal.stopHelpdeskWrite(key, failure);
      if (failure.code === "UNAUTHENTICATED" && operation.isCurrent())
        portal.expireSession();
    } finally {
      portal.endHelpdeskWrite(key);
    }
  }
  return {
    run,
    busy,
    stopped,
    blocked: busy || Boolean(stopped),
    portal,
    acceptRead,
    isCurrent: currentOperation.canUpdate,
  };
}

export function HelpdeskPortal({
  mode = "mock",
}: { mode?: HelpdeskPortalMode } = {}) {
  const copy = COPY[mode];
  const { helpdeskService } = usePortal();
  if (!helpdeskService)
    return (
      <Empty
        title="MVP chưa được gắn service kiểm thử"
        description="MOCK mặc định vẫn hoạt động. Tích hợp LIVE tiếp tục BLOCKED."
      />
    );
  return (
    <CopyContext.Provider value={copy}>
      <div className="helpdesk-portal">
        <Routes>
          <Route index element={<HelpdeskList service={helpdeskService} />} />
          <Route
            path="new"
            element={<HelpdeskCreate service={helpdeskService} />}
          />
          <Route
            path=":id"
            element={<DetailRoute service={helpdeskService} />}
          />
          <Route
            path="*"
            element={
              <Empty
                title="Không tìm thấy trang yêu cầu hỗ trợ IT"
                description="Chọn danh sách yêu cầu để tiếp tục."
              />
            }
          />
        </Routes>
        <p className="aside-footnote helpdesk-environment-note">
          {copy.footnote}
        </p>
      </div>
    </CopyContext.Provider>
  );
}

function HelpdeskList({ service }: { service: MvpHelpdeskRequestPort }) {
  const copy = useContext(CopyContext);
  const [params, setParams] = useSearchParams();
  const after = params.get("after") ?? undefined;
  const load = useCallback(
    () => service.list({ ...(after ? { after } : {}), limit: 20 }),
    [service, after],
  );
  const read = useHelpdeskRead(load);
  return (
    <>
      <PageHeading title="Yêu cầu hỗ trợ IT" description={copy.list}>
        <Link className="button primary" to={`${ROOT}/new`}>
          <Plus size={16} aria-hidden="true" />
          Tạo yêu cầu IT
        </Link>
      </PageHeading>
      <section className="panel helpdesk-list-panel">
        <div className="panel-heading">
          <h2>Danh sách yêu cầu</h2>
          <button
            className="text-link"
            disabled={read.loading}
            onClick={read.reload}
          >
            Tải lại danh sách
          </button>
        </div>
        {read.loading ? (
          <Loading />
        ) : read.error ? (
          <ErrorState message={read.error} onRetry={read.reload} />
        ) : !read.data?.items.length ? (
          <Empty title="Chưa có yêu cầu IT" description={copy.empty} />
        ) : (
          <div className="table-scroll">
            <table>
              <caption className="sr-only">Yêu cầu hỗ trợ IT</caption>
              <thead>
                <tr>
                  <th>Mã</th>
                  <th>Yêu cầu</th>
                  <th>Trạng thái</th>
                  <th>Người yêu cầu</th>
                  <th>Người xử lý</th>
                </tr>
              </thead>
              <tbody>
                {read.data.items.map((item) => (
                  <tr key={item.id}>
                    <td data-label="Mã" className="helpdesk-request-code">
                      <span className="request-id">{item.id}</span>
                    </td>
                    <td data-label="Yêu cầu">
                      <Link
                        className="request-title"
                        to={`${ROOT}/${encodeURIComponent(item.id)}`}
                      >
                        <strong>{item.title}</strong>
                        <ArrowUpRight size={14} aria-hidden="true" />
                      </Link>
                    </td>
                    <td data-label="Trạng thái">
                      <span className={`badge ${stateClassName(item.state)}`}>
                        {stateLabel(item.state)}
                      </span>
                    </td>
                    <td data-label="Người yêu cầu">
                      {personName(item.requesterDisplayName)}
                    </td>
                    <td data-label="Người xử lý">
                      {item.assigneeId === null
                        ? "Chưa phân công"
                        : personName(item.assigneeDisplayName)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="pagination">
          <button
            className="button secondary small"
            disabled={read.loading || !after}
            onClick={() => setParams({})}
          >
            Trang đầu
          </button>
          <button
            className="button secondary small"
            disabled={read.loading || !read.data?.nextCursor}
            onClick={() => {
              if (read.data?.nextCursor)
                setParams({ after: read.data.nextCursor });
            }}
          >
            Trang tiếp
          </button>
        </div>
      </section>
    </>
  );
}

function HelpdeskCreate({ service }: { service: MvpHelpdeskRequestPort }) {
  const copy = useContext(CopyContext);
  const navigate = useNavigate();
  const write = useHelpdeskWrite(CREATE);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [invalid, setInvalid] = useState(false);
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (write.blocked) return;
    if (!validText(title, 200) || !validText(description, 4000)) {
      setInvalid(true);
      return;
    }
    let id: string | undefined;
    await write.run(
      async () => {
        id = (await service.create({ title, description })).id;
      },
      () => {
        // Return to the authoritative list; the new resource can be opened there.
        if (id) navigate(ROOT);
      },
    );
  }
  return (
    <>
      <Link className="back-link" to={ROOT}>
        <ArrowLeft size={14} aria-hidden="true" />
        Danh sách yêu cầu IT
      </Link>
      <PageHeading title="Tạo yêu cầu IT Support" description={copy.create} />
      <div className="form-layout">
        <form
          className="panel request-form"
          aria-label="Tạo yêu cầu IT"
          onSubmit={submit}
        >
          <fieldset disabled={write.blocked}>
            <legend>Thông tin yêu cầu</legend>
            {copy === COPY["integration-local"] && (
              <div className="helpdesk-request-type">
                <Monitor size={20} aria-hidden="true" />
                <div>
                  <span>Loại yêu cầu</span>
                  <strong>Hỗ trợ IT</strong>
                </div>
              </div>
            )}
            <label className="field">
              <span>
                Tiêu đề yêu cầu{" "}
                <span className="helpdesk-required" aria-hidden="true">
                  *
                </span>
              </span>
              <input
                required
                maxLength={200}
                placeholder="Ví dụ: Máy in phòng B1 báo kẹt giấy"
                value={title}
                onChange={(event) => setTitle(event.target.value)}
              />
            </label>
            <label className="field">
              <span>
                Mô tả chi tiết{" "}
                <span className="helpdesk-required" aria-hidden="true">
                  *
                </span>
              </span>
              <textarea
                required
                maxLength={4000}
                rows={5}
                placeholder="Bạn gặp lỗi gì, ở đâu, từ khi nào?"
                value={description}
                onChange={(event) => setDescription(event.target.value)}
              />
            </label>
          </fieldset>
          {invalid && (
            <p className="field-error" role="alert">
              Tiêu đề và mô tả không được để trống.
            </p>
          )}
          {write.stopped && <ErrorState message={write.stopped.message} />}
          <div className="form-actions">
            <Link to={ROOT} className="button secondary">
              Xem danh sách và đối soát
            </Link>
            <button className="button primary" disabled={write.blocked}>
              {write.busy ? "Đang gửi…" : "Gửi yêu cầu IT"}
            </button>
          </div>
        </form>
        {copy === COPY["integration-local"] && (
          <aside className="panel helpdesk-form-guide">
            <h2>Mô tả tốt giúp xử lý nhanh hơn</h2>
            <ol>
              <li>Thiết bị hoặc phòng gặp sự cố</li>
              <li>Lỗi hiện ra thế nào, thông báo gì</li>
              <li>Bắt đầu từ khi nào</li>
              <li>Bạn đã thử cách nào chưa</li>
            </ol>
            <p>
              Sau khi gửi, theo dõi trạng thái trong danh sách yêu cầu và xác
              nhận khi sự cố đã được xử lý.
            </p>
          </aside>
        )}
      </div>
    </>
  );
}

function DetailRoute({ service }: { service: MvpHelpdeskRequestPort }) {
  const { id = "" } = useParams();
  return <HelpdeskDetail key={id} id={id} service={service} />;
}

function HelpdeskDetail({
  id,
  service,
}: {
  id: string;
  service: MvpHelpdeskRequestPort;
}) {
  const copy = useContext(CopyContext);
  const write = useHelpdeskWrite(id);
  const [resolution, setResolution] = useState("");
  const [invalid, setInvalid] = useState(false);
  const [reloadIntent, setReloadIntent] = useState(false);
  const load = useCallback(async () => {
    const [detail, history] = await Promise.all([
      service.detail(id),
      service.history(id),
    ]);
    return { detail, history };
  }, [service, id]);
  const read = useHelpdeskRead(load);
  useEffect(() => {
    if (read.data) write.acceptRead();
  }, [read.data, write.acceptRead]);
  useEffect(() => {
    if (reloadIntent && read.data) {
      write.portal.releaseHelpdeskReadStop(id);
      setReloadIntent(false);
    }
  }, [reloadIntent, read.data, id, write.portal.releaseHelpdeskReadStop]);
  function reload() {
    if (!write.busy) {
      setReloadIntent(true);
      read.reload();
    }
  }
  if (read.loading) return <Loading />;
  if (read.error || !read.data)
    return (
      <ErrorState
        message={
          read.error ?? "Không tìm thấy yêu cầu hoặc yêu cầu không khả dụng."
        }
        onRetry={reload}
      />
    );
  const { detail, history } = read.data;
  if (
    write.stopped?.code === "FORBIDDEN" ||
    write.stopped?.code === "NOT_FOUND"
  ) {
    return <ErrorState message={write.stopped.message} onRetry={reload} />;
  }
  const actions = (Object.keys(labels) as WorkflowAction[]).filter((action) =>
    detail.allowedActions.includes(action),
  );
  const blocked = write.blocked || !validVersion(detail.version);
  const assignment = helpdeskAssignmentFormProps(
    detail,
    service,
    () => {
      if (write.isCurrent()) read.reload();
    },
    write.isCurrent,
  );
  const binding = assignment?.submission;
  // The APP-11 binding owns ID membership, assignment guard and Detail reload.
  // Wrap only its invocation to share the Portal's pending/uncertain write stop.
  const assignmentSubmission =
    binding?.status === "ready"
      ? {
          ...binding,
          submitAssignment: async (
            selected: Parameters<typeof binding.submitAssignment>[0],
          ) => {
            await write.run(
              () => binding.submitAssignment(selected),
              () => {},
            );
          },
        }
      : binding;
  async function transition(action: WorkflowAction) {
    if (blocked || !detail.allowedActions.includes(action)) return;
    if (action === "resolve" && !validText(resolution, 4000)) {
      setInvalid(true);
      return;
    }
    setInvalid(false);
    await write.run(
      () =>
        action === "resolve"
          ? service.resolve(id, { expectedVersion: detail.version, resolution })
          : service[action](id, { expectedVersion: detail.version }),
      () => {
        setResolution("");
        read.reload();
      },
    );
  }
  return (
    <>
      <Link className="back-link" to={ROOT}>
        <ArrowLeft size={14} aria-hidden="true" />
        Danh sách yêu cầu IT
      </Link>
      <PageHeading
        eyebrow={detail.id}
        title={detail.title}
        description={copy.detail}
      >
        <span className={`badge ${stateClassName(detail.state)}`}>
          {stateLabel(detail.state)}
        </span>
      </PageHeading>
      <div className="detail-layout">
        <div>
          <section className="panel detail-content">
            <div className="panel-heading">
              <h2>Nội dung yêu cầu</h2>
            </div>
            <p className="request-description">{detail.description}</p>
            {detail.resolution !== null && (
              <div className="helpdesk-resolution">
                <h2>Kết quả xử lý</h2>
                <p>{detail.resolution}</p>
              </div>
            )}
          </section>
          <section className="panel detail-timeline" aria-label="Lịch sử xử lý">
            <div className="panel-heading">
              <h2>Lịch sử xử lý</h2>
            </div>
            {!history.length ? (
              <Empty
                title="Chưa có lịch sử được cung cấp"
                description="Lịch sử xử lý sẽ hiển thị tại đây."
              />
            ) : (
              <ol className="timeline">
                {history.map((entry, index) => (
                  <li key={index}>
                    <span className="timeline-dot" aria-hidden="true" />
                    <div>
                      <div className="timeline-title">
                        <strong>{entry.transitionId}</strong>
                        <span>{entry.occurredAt}</span>
                      </div>
                      <p>
                        {stateLabel(entry.sourceState)} →{" "}
                        {stateLabel(entry.targetState)}
                      </p>
                    </div>
                  </li>
                ))}
              </ol>
            )}
          </section>
        </div>
        <aside>
          <section className="panel metadata">
            <div className="panel-heading">
              <h2>Thông tin yêu cầu</h2>
            </div>
            <dl>
              <dt>Trạng thái</dt>
              <dd data-testid="mvp-state">
                <span className={`badge ${stateClassName(detail.state)}`}>
                  {stateLabel(detail.state)}
                </span>
              </dd>
              <dt>Phiên bản phân công</dt>
              <dd data-testid="mvp-assignment-version">
                {detail.assignmentVersion ?? "Chưa được cung cấp"}
              </dd>
              <dt>Người yêu cầu</dt>
              <dd>{personName(detail.requesterDisplayName)}</dd>
              <dt>Mã người yêu cầu</dt>
              <dd>{detail.requesterId}</dd>
              <dt>Người xử lý</dt>
              <dd>
                {detail.assigneeId === null
                  ? "Chưa phân công"
                  : personName(detail.assigneeDisplayName)}
              </dd>
              {detail.assigneeId !== null && (
                <>
                  <dt>Mã người xử lý</dt>
                  <dd>{detail.assigneeId}</dd>
                </>
              )}
            </dl>
          </section>
          <section className="panel action-panel">
            <h2>Thao tác xử lý</h2>
            {write.stopped && <ErrorState message={write.stopped.message} />}
            {!actions.length && !assignment && (
              <p>Bạn không có thao tác xử lý ở trạng thái hiện tại.</p>
            )}
            <fieldset disabled={blocked}>
              <legend className="sr-only">Thao tác trạng thái</legend>
              {actions.includes("resolve") && (
                <label className="field">
                  Kết quả xử lý
                  <textarea
                    maxLength={4000}
                    rows={4}
                    value={resolution}
                    onChange={(event) => setResolution(event.target.value)}
                  />
                </label>
              )}
              {invalid && (
                <p className="field-error" role="alert">
                  Kết quả xử lý không được để trống.
                </p>
              )}
              {actions.map((action) => (
                <button
                  type="button"
                  className="button primary"
                  key={action}
                  disabled={blocked}
                  onClick={(event) => {
                    if (event.detail <= 1) transition(action);
                  }}
                >
                  {labels[action]}
                </button>
              ))}
            </fieldset>
            <button
              className="text-link"
              disabled={write.busy}
              onClick={reload}
            >
              Tải lại chi tiết và lịch sử
            </button>
          </section>
          {assignment && (
            <fieldset disabled={write.blocked} aria-label="Phân công yêu cầu">
              <legend className="sr-only">Assignment</legend>
              <AssignmentForm
                key={read.revision}
                {...assignment}
                loading={write.busy}
                submission={
                  write.stopped
                    ? { status: "blocked", reason: write.stopped.message }
                    : assignmentSubmission
                }
              />
            </fieldset>
          )}
        </aside>
      </div>
    </>
  );
}
