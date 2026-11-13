// SPDX-FileCopyrightText: 2026 TRICORE contributors
// SPDX-License-Identifier: Apache-2.0

package com.tricore.dxos.gateway.helpdesk;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.tricore.dxos.application.authorization.WorkflowAccessDecision;
import com.tricore.dxos.application.authorization.WorkflowAccessException;
import com.tricore.dxos.application.helpdesk.api.HelpdeskUseCase;
import com.tricore.dxos.gateway.workflow.WorkflowJsonConfiguration;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.springframework.http.MediaType;
import org.springframework.http.converter.HttpMessageConverter;
import org.springframework.http.converter.json.MappingJackson2HttpMessageConverter;
import org.springframework.test.json.JsonCompareMode;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Stream;

import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

class HelpdeskHttpParityTest {
    private static final String API = "/api/v1/mvp/requests";
    private static final UUID ID = UUID.fromString("f3bf54b7-fdab-4b45-85dd-94cbd8587a9d");
    private static final String CREATE = """
            {"title":"Printer","description":"Offline","requestType":"IT_HELPDESK"}
            """;
    private static final String RESPONSE = """
            {"id":"f3bf54b7-fdab-4b45-85dd-94cbd8587a9d","title":"Printer","description":"Offline",
             "requestType":"IT_HELPDESK","requesterId":"employee","assigneeId":null,"resolution":null,
             "assignmentVersion":0,"workflowInstanceId":"wf-1","state":"SUBMITTED","version":0,
             "allowedActions":["triage"]}
            """;
    private final HelpdeskUseCase service = mock(HelpdeskUseCase.class);
    private MockMvc mvc;

    @BeforeEach void configureProductionJsonConverters() {
        var mapper = new ObjectMapper().findAndRegisterModules()
                .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
        List<HttpMessageConverter<?>> converters = new ArrayList<>();
        converters.add(new MappingJackson2HttpMessageConverter(mapper));
        new WorkflowJsonConfiguration().extendMessageConverters(converters);
        mvc = MockMvcBuilders.standaloneSetup(new HelpdeskController(service))
                .setMessageConverters(converters.toArray(HttpMessageConverter<?>[]::new))
                .setControllerAdvice(new HelpdeskExceptionHandler()).build();
    }

    private static HelpdeskUseCase.RequestView view() {
        return new HelpdeskUseCase.RequestView(ID, "Printer", "Offline", "IT_HELPDESK",
                "employee", null, null, 0, "wf-1", "SUBMITTED", 0,
                List.of("triage"), null, null, null);
    }

    @Test void createKeepsLocationAndExplicitNullsWhileOmittingOnlyOptionalDetailFields() throws Exception {
        when(service.create("Printer", "Offline")).thenReturn(view());
        mvc.perform(post(API).contentType(MediaType.APPLICATION_JSON).content(CREATE))
                .andExpect(status().isCreated()).andExpect(header().string("Location", API + "/" + ID))
                .andExpect(content().json(RESPONSE, JsonCompareMode.STRICT));
        verify(service).create("Printer", "Offline");
        verifyNoMoreInteractions(service);
    }

    @Test void listKeepsPaginationAndOmissionInsideNestedItems() throws Exception {
        when(service.list(ID, 2)).thenReturn(new HelpdeskUseCase.Page(List.of(view()), ID));
        mvc.perform(get(API).param("after", ID.toString()).param("limit", "2"))
                .andExpect(status().isOk())
                .andExpect(content().json("{\"items\":[" + RESPONSE + "],\"nextCursor\":\"" + ID + "\"}",
                        JsonCompareMode.STRICT));
        when(service.list(null, 50)).thenReturn(new HelpdeskUseCase.Page(List.of(), null));
        mvc.perform(get(API)).andExpect(status().isOk())
                .andExpect(content().json("{\"items\":[],\"nextCursor\":null}", JsonCompareMode.STRICT));
        verify(service).list(ID, 2);
        verify(service).list(null, 50);
        verifyNoMoreInteractions(service);
    }

    @Test void detailKeepsDisplayNamesAndNullableCandidateNames() throws Exception {
        when(service.get(ID)).thenReturn(new HelpdeskUseCase.RequestView(ID, "Printer", "Offline", "IT_HELPDESK",
                "employee", null, null, 0, "wf-1", "TRIAGED", 1, List.of("assign"),
                "Employee", null, List.of(new HelpdeskUseCase.AssigneeOption("worker", null))));
        mvc.perform(get(API + "/" + ID)).andExpect(status().isOk())
                .andExpect(content().json("""
                        {"id":"f3bf54b7-fdab-4b45-85dd-94cbd8587a9d","title":"Printer","description":"Offline",
                         "requestType":"IT_HELPDESK","requesterId":"employee","assigneeId":null,"resolution":null,
                         "assignmentVersion":0,"workflowInstanceId":"wf-1","state":"TRIAGED","version":1,
                         "allowedActions":["assign"],"requesterDisplayName":"Employee",
                         "eligibleAssignees":[{"id":"worker","displayName":null}]}
                        """, JsonCompareMode.STRICT));
        verify(service).get(ID);
        verifyNoMoreInteractions(service);
    }

    @Test void historyKeepsItsFieldsAndConfiguredTimestampFormat() throws Exception {
        when(service.history(ID)).thenReturn(List.of(new HelpdeskUseCase.HistoryView(
                "triage", "SUBMITTED", "TRIAGED", 1, Instant.parse("2026-11-12T00:00:00Z"))));
        mvc.perform(get(API + "/" + ID + "/history")).andExpect(status().isOk())
                .andExpect(content().json("""
                        [{"transitionId":"triage","sourceState":"SUBMITTED","targetState":"TRIAGED",
                          "version":1,"occurredAt":"2026-11-12T00:00:00Z"}]
                        """, JsonCompareMode.STRICT));
        verify(service).history(ID);
        verifyNoMoreInteractions(service);
    }

    static Stream<Arguments> commands() {
        return Stream.of(
                Arguments.of("triage", "{\"expectedVersion\":1}",
                        (Function<HelpdeskUseCase, HelpdeskUseCase.RequestView>) api -> api.triage(ID, 1)),
                Arguments.of("assign", "{\"assigneeId\":\"worker\",\"expectedAssignmentVersion\":2}",
                        (Function<HelpdeskUseCase, HelpdeskUseCase.RequestView>) api -> api.assign(ID, "worker", 2)),
                Arguments.of("start", "{\"expectedVersion\":3}",
                        (Function<HelpdeskUseCase, HelpdeskUseCase.RequestView>) api -> api.start(ID, 3)),
                Arguments.of("resolve", "{\"expectedVersion\":4,\"resolution\":\"Fixed\"}",
                        (Function<HelpdeskUseCase, HelpdeskUseCase.RequestView>) api -> api.resolve(ID, 4, "Fixed")),
                Arguments.of("confirm", "{\"expectedVersion\":5}",
                        (Function<HelpdeskUseCase, HelpdeskUseCase.RequestView>) api -> api.confirm(ID, 5)));
    }

    @ParameterizedTest @MethodSource("commands")
    void eachCommandCallsOnlyItsApplicationOperation(String action, String input,
            Function<HelpdeskUseCase, HelpdeskUseCase.RequestView> call) throws Exception {
        when(call.apply(service)).thenReturn(view());
        mvc.perform(post(API + "/" + ID + "/" + action).contentType(MediaType.APPLICATION_JSON).content(input))
                .andExpect(status().isOk()).andExpect(content().json(RESPONSE, JsonCompareMode.STRICT));
        call.apply(verify(service));
        verifyNoMoreInteractions(service);
    }

    static Stream<Arguments> invalidInputs() {
        return Stream.of(
                Arguments.of("", "{\"title\":\"\",\"description\":\"Offline\",\"requestType\":\"IT_HELPDESK\"}"),
                Arguments.of("", CREATE.replace("IT_HELPDESK", "FACILITY")),
                Arguments.of("", CREATE.strip().replace("}", ",\"actorId\":\"forged\"}")),
                Arguments.of("", CREATE + "{}"),
                Arguments.of("/" + ID + "/triage", "{\"expectedVersion\":-1}"),
                Arguments.of("/" + ID + "/triage", "{\"expectedVersion\":\"0\"}"),
                Arguments.of("/" + ID + "/triage", "{\"expectedVersion\":0.0}"),
                Arguments.of("/" + ID + "/triage", "{\"expectedVersion\":9223372036854775808}"),
                Arguments.of("/" + ID + "/assign", "{\"assigneeId\":\"\",\"expectedAssignmentVersion\":0}"),
                Arguments.of("/" + ID + "/resolve", "{\"expectedVersion\":0,\"resolution\":\"\"}"));
    }

    @ParameterizedTest @MethodSource("invalidInputs")
    void invalidInputNeverInvokesTheApplication(String suffix, String input) throws Exception {
        mvc.perform(post(API + suffix).contentType(MediaType.APPLICATION_JSON).content(input))
                .andExpect(status().isBadRequest());
        verifyNoInteractions(service);
    }

    static Stream<Arguments> deniedOutcomes() {
        return Stream.of(Arguments.of(WorkflowAccessDecision.FORBIDDEN, 403, "FORBIDDEN"),
                Arguments.of(WorkflowAccessDecision.HIDDEN, 404, "NOT_FOUND"),
                Arguments.of(WorkflowAccessDecision.UNAVAILABLE, 503, "AUTHORIZATION_UNAVAILABLE"));
    }

    @ParameterizedTest @MethodSource("deniedOutcomes")
    void denialKeepsTheErrorContractWithoutRetry(WorkflowAccessDecision decision, int status, String code)
            throws Exception {
        when(service.get(ID)).thenThrow(new WorkflowAccessException(decision));
        mvc.perform(get(API + "/" + ID)).andExpect(status().is(status))
                .andExpect(jsonPath("$.code").value(code)).andExpect(jsonPath("$.status").value(status));
        verify(service).get(ID);
        verifyNoMoreInteractions(service);
    }
}
