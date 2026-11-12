// SPDX-FileCopyrightText: 2026 TRICORE contributors
//
// SPDX-License-Identifier: Apache-2.0

package com.tricore.dxos.gateway.helpdesk;

import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.tricore.dxos.gateway.workflow.dto.WorkflowVersionDeserializer;
import com.tricore.dxos.application.helpdesk.api.HelpdeskUseCase;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.net.URI;
import java.util.List;
import java.util.UUID;

@RestController
@ConditionalOnProperty(name = "dxos.helpdesk.enabled", havingValue = "true")
@RequestMapping("/api/v1/mvp/requests")
public class HelpdeskController {
    private final HelpdeskUseCase service;
    public HelpdeskController(HelpdeskUseCase service) { this.service = service; }

    public record Create(@NotBlank @Size(max = 200) String title,
                         @NotBlank @Size(max = 4000) String description,
                         @NotNull @Pattern(regexp = "IT_HELPDESK") String requestType) {
        @JsonAnySetter public void unknown(String field, Object value) { throw new IllegalArgumentException("Unknown field"); }
    }
    public record Version(@NotNull @PositiveOrZero
                          @JsonDeserialize(using = WorkflowVersionDeserializer.class) Long expectedVersion) {
        @JsonAnySetter public void unknown(String field, Object value) { throw new IllegalArgumentException("Unknown field"); }
    }
    public record Assign(@NotBlank @Size(max = 1024) String assigneeId,
                         @NotNull @PositiveOrZero @JsonDeserialize(using = WorkflowVersionDeserializer.class) Long expectedAssignmentVersion) {
        @JsonAnySetter public void unknown(String field, Object value) { throw new IllegalArgumentException("Unknown field"); }
    }
    public record Resolve(@NotNull @PositiveOrZero @JsonDeserialize(using = WorkflowVersionDeserializer.class) Long expectedVersion,
                          @NotBlank @Size(max = 4000) String resolution) {
        @JsonAnySetter public void unknown(String field, Object value) { throw new IllegalArgumentException("Unknown field"); }
    }

    @PostMapping
    public ResponseEntity<HelpdeskUseCase.RequestView> create(@Valid @RequestBody Create input) {
        var result = service.create(input.title(), input.description());
        return ResponseEntity.created(URI.create("/api/v1/mvp/requests/" + result.id())).body(result);
    }
    @GetMapping public HelpdeskUseCase.Page list(@RequestParam(required = false) UUID after,
            @RequestParam(defaultValue = "50") @Min(1) @Max(100) int limit) { return service.list(after, limit); }
    @GetMapping("/{id}") public HelpdeskUseCase.RequestView get(@PathVariable UUID id) { return service.get(id); }
    @GetMapping("/{id}/history") public List<HelpdeskUseCase.HistoryView> history(@PathVariable UUID id) { return service.history(id); }
    @PostMapping("/{id}/triage") public HelpdeskUseCase.RequestView triage(@PathVariable UUID id, @Valid @RequestBody Version input) {
        return service.triage(id, input.expectedVersion());
    }
    @PostMapping("/{id}/assign") public HelpdeskUseCase.RequestView assign(@PathVariable UUID id, @Valid @RequestBody Assign input) {
        return service.assign(id, input.assigneeId(), input.expectedAssignmentVersion());
    }
    @PostMapping("/{id}/start") public HelpdeskUseCase.RequestView start(@PathVariable UUID id, @Valid @RequestBody Version input) {
        return service.start(id, input.expectedVersion());
    }
    @PostMapping("/{id}/resolve") public HelpdeskUseCase.RequestView resolve(@PathVariable UUID id, @Valid @RequestBody Resolve input) {
        return service.resolve(id, input.expectedVersion(), input.resolution());
    }
    @PostMapping("/{id}/confirm") public HelpdeskUseCase.RequestView confirm(@PathVariable UUID id, @Valid @RequestBody Version input) {
        return service.confirm(id, input.expectedVersion());
    }
}
