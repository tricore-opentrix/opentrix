// SPDX-FileCopyrightText: 2026 TRICORE contributors
//
// SPDX-License-Identifier: Apache-2.0

package com.tricore.dxos.core.manifest;

import static org.assertj.core.api.Assertions.assertThat;

import com.networknt.schema.Error;
import com.networknt.schema.InputFormat;
import com.networknt.schema.Schema;
import com.networknt.schema.SchemaLocation;
import com.networknt.schema.SchemaRegistry;
import com.networknt.schema.SpecificationVersion;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

class AppManifestSchemaTest {

    private static final String DRAFT_2020_12 = "https://json-schema.org/draft/2020-12/schema";
    private static final Path SCHEMA_FILE =
            Path.of("..", "schemas", "app-manifest", "v1", "app-manifest.schema.json");
    private static final Path MANIFESTS = Path.of("src", "test", "resources", "manifests");

    private static SchemaRegistry registry;
    private static Schema manifestSchema;

    @BeforeAll
    static void loadSchema() throws IOException {
        registry = SchemaRegistry.withDefaultDialect(SpecificationVersion.DRAFT_2020_12);
        manifestSchema = registry.getSchema(read(SCHEMA_FILE), InputFormat.JSON);
    }

    @Test
    void schemaIsValidAgainstDraft2020_12MetaSchema() throws IOException {
        Schema metaSchema = registry.getSchema(SchemaLocation.of(DRAFT_2020_12));

        List<Error> errors = metaSchema.validate(read(SCHEMA_FILE), InputFormat.JSON);

        assertThat(errors).isEmpty();
    }

    @Test
    void itHelpdeskManifestIsAccepted() throws IOException {
        assertThat(validate("valid/it-helpdesk.app.json")).isEmpty();
    }

    @Test
    void manifestWithoutVersionIsRejected() throws IOException {
        assertThat(validate("invalid/missing-version.app.json")).isNotEmpty();
    }

    @Test
    void entityWithUnknownTypeIsRejected() throws IOException {
        assertThat(validate("invalid/bad-entity-type.app.json")).isNotEmpty();
    }

    @Test
    void unknownTopLevelKeyIsRejected() throws IOException {
        assertThat(validate("invalid/unknown-top-level-key.app.json")).isNotEmpty();
    }

    private static List<Error> validate(String manifest) throws IOException {
        return manifestSchema.validate(read(MANIFESTS.resolve(manifest)), InputFormat.JSON);
    }

    private static String read(Path path) throws IOException {
        return Files.readString(path, StandardCharsets.UTF_8);
    }
}
