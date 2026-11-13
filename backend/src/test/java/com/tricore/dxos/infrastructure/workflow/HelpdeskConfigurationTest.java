// SPDX-FileCopyrightText: 2026 TRICORE contributors
//
// SPDX-License-Identifier: Apache-2.0

package com.tricore.dxos.infrastructure.workflow;

import org.junit.jupiter.api.Test;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;
import com.tricore.dxos.gateway.helpdesk.HelpdeskController;
import com.tricore.dxos.application.helpdesk.api.HelpdeskUseCase;
import com.tricore.dxos.application.identity.CurrentPrincipal;
import org.springframework.core.env.MapPropertySource;
import java.util.Map;
import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

class HelpdeskConfigurationTest {
    @Test void disabledByDefault() {
        try(var context=new AnnotationConfigApplicationContext(HelpdeskConfiguration.class,HelpdeskController.class)) {
            assertThat(context.getBeansOfType(HelpdeskService.class)).isEmpty();
            assertThat(context.getBeansOfType(HelpdeskUseCase.class)).isEmpty();
            assertThat(context.getBeansOfType(HelpdeskController.class)).isEmpty();
        }
    }
    @Test void enabledCandidateInjectsTheModuleApiWithoutInvokingIt() {
        CurrentPrincipal principal = mock(CurrentPrincipal.class);
        try (var context = new AnnotationConfigApplicationContext()) {
            context.getEnvironment().getPropertySources().addFirst(new MapPropertySource("candidate", Map.of(
                    "dxos.helpdesk.enabled", "true",
                    "dxos.helpdesk.jdbc-url", "jdbc:postgresql://127.0.0.1:55439/helpdesk_disposable_test",
                    "dxos.helpdesk.username", "helpdesk_runtime_test",
                    "dxos.helpdesk.password", "unused-fixture-password",
                    "dxos.helpdesk.schema", "helpdesk_test",
                    "dxos.helpdesk.tenant", "tenant-a",
                    "server.address", "127.0.0.1")));
            context.registerBean(CurrentPrincipal.class, () -> principal);
            context.register(HelpdeskConfiguration.class, HelpdeskController.class);
            context.refresh();
            assertThat(context.getBean(HelpdeskUseCase.class)).isSameAs(context.getBean(HelpdeskService.class));
            assertThat(context.getBean(HelpdeskController.class)).isNotNull();
            verifyNoInteractions(principal);
        }
    }
    @Test void candidateCannotTargetSharedDatabaseOrPublicListener() {
        HelpdeskConfiguration.requireDisposable("jdbc:postgresql://127.0.0.1:55439/helpdesk_disposable_test","helpdesk_runtime_test","127.0.0.1");
        for(String url:new String[]{"jdbc:postgresql://shared.example:5432/helpdesk_disposable_test","jdbc:postgresql://127.0.0.1:5432/postgres",
                "jdbc:postgresql://127.0.0.1:55439/helpdesk_disposable_test?options=anything"})
            assertThatThrownBy(() -> HelpdeskConfiguration.requireDisposable(url,"helpdesk_runtime_test","127.0.0.1")).isInstanceOf(IllegalArgumentException.class);
        assertThatThrownBy(() -> HelpdeskConfiguration.requireDisposable("jdbc:postgresql://127.0.0.1:55439/helpdesk_disposable_test","postgres","127.0.0.1")).isInstanceOf(IllegalArgumentException.class);
        assertThatThrownBy(() -> HelpdeskConfiguration.requireDisposable("jdbc:postgresql://127.0.0.1:55439/helpdesk_disposable_test","helpdesk_runtime_test","0.0.0.0")).isInstanceOf(IllegalArgumentException.class);
    }
}
