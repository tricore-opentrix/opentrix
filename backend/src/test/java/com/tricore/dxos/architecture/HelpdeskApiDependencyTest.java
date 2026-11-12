// SPDX-FileCopyrightText: 2026 TRICORE contributors
// SPDX-License-Identifier: Apache-2.0

package com.tricore.dxos.architecture;

import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.lang.ArchRule;
import com.tricore.dxos.application.helpdesk.api.HelpdeskUseCase;
import com.tricore.dxos.gateway.helpdesk.HelpdeskController;
import com.tricore.dxos.infrastructure.workflow.HelpdeskService;
import org.junit.jupiter.api.Test;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;
import static org.junit.jupiter.api.Assertions.*;

class HelpdeskApiDependencyTest {
    private static final ArchRule NO_INFRASTRUCTURE = noClasses().should().dependOnClassesThat()
            .resideInAPackage("com.tricore.dxos.infrastructure..");

    @Test void controllerDependsOnTheApplicationApiWithoutInfrastructureTypes() throws Exception {
        var classes = new ClassFileImporter().importClasses(HelpdeskController.class);
        assertTrue(classes.contain(HelpdeskController.class));
        assertNotNull(HelpdeskController.class.getConstructor(HelpdeskUseCase.class));
        NO_INFRASTRUCTURE.check(classes);
    }

    @Test void applicationApiAndAllResultRecordsUseOnlyJavaAndTheirOwnPackage() {
        var classes = new ClassFileImporter().importClasses(HelpdeskUseCase.class,
                HelpdeskUseCase.RequestView.class, HelpdeskUseCase.Page.class,
                HelpdeskUseCase.HistoryView.class, HelpdeskUseCase.AssigneeOption.class);
        assertEquals(5, classes.size());
        noClasses().should().dependOnClassesThat().resideOutsideOfPackages(
                "java..", "com.tricore.dxos.application.helpdesk.api..").check(classes);
    }

    @Test void theDependencyCheckRejectsTheOldConcreteServiceDependency() {
        var canary = new ClassFileImporter().importClasses(InfrastructureCoupledController.class);
        assertThrows(AssertionError.class, () -> NO_INFRASTRUCTURE.check(canary));
    }

    static class InfrastructureCoupledController {
        HelpdeskService service;
    }
}
