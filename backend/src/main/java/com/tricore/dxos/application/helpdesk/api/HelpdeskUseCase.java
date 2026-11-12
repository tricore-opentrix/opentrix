// SPDX-FileCopyrightText: 2026 TRICORE contributors
// SPDX-License-Identifier: Apache-2.0

package com.tricore.dxos.application.helpdesk.api;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

/** Authorized Helpdesk operations; caller identity comes from CurrentPrincipal, never request fields. */
public interface HelpdeskUseCase {
    RequestView create(String title, String description);
    Page list(UUID after, int limit);
    RequestView get(UUID id);
    List<HistoryView> history(UUID id);
    RequestView triage(UUID id, long expectedVersion);
    RequestView assign(UUID id, String assigneeId, long expectedAssignmentVersion);
    RequestView start(UUID id, long expectedVersion);
    RequestView resolve(UUID id, long expectedVersion, String resolution);
    RequestView confirm(UUID id, long expectedVersion);

    record AssigneeOption(String id, String displayName) {}
    record RequestView(UUID id, String title, String description, String requestType,
            String requesterId, String assigneeId, String resolution, long assignmentVersion,
            String workflowInstanceId, String state, long version, List<String> allowedActions,
            String requesterDisplayName, String assigneeDisplayName, List<AssigneeOption> eligibleAssignees) {}
    record Page(List<RequestView> items, UUID nextCursor) {}
    record HistoryView(String transitionId, String sourceState, String targetState,
            long version, Instant occurredAt) {}
}
