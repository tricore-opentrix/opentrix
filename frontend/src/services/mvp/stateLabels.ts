// SPDX-FileCopyrightText: 2026 TRICORE contributors
//
// SPDX-License-Identifier: Apache-2.0

type KnownState =
  "SUBMITTED" | "TRIAGED" | "IN_PROGRESS" | "RESOLVED" | "CONFIRMED";
const states = {
  SUBMITTED: { label: "Mới gửi", className: "state-submitted" },
  TRIAGED: { label: "Đã tiếp nhận", className: "state-triaged" },
  IN_PROGRESS: { label: "Đang xử lý", className: "state-in-progress" },
  RESOLVED: { label: "Chờ xác nhận", className: "state-resolved" },
  CONFIRMED: { label: "Hoàn thành", className: "state-confirmed" },
} satisfies Record<KnownState, { label: string; className: string }>;

function presentation(state: string) {
  return Object.hasOwn(states, state) ? states[state as KnownState] : undefined;
}

export function stateLabel(state: string) {
  return presentation(state)?.label ?? state;
}

export function stateClassName(state: string) {
  return presentation(state)?.className ?? "state-unknown";
}
