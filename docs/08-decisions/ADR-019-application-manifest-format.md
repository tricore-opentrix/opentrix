<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# ADR-019 - Application manifest format (v1)

**Status:** PROPOSED — becomes ACCEPTED on merge with approval from @lexuanbao258-collab, per `GOVERNANCE.md`

**Decision date:** 2026-11-25

**Author:** @phanyen06ym-ien · **Reviewer:** @lexuanbao258-collab

**Tracking:** [#274](https://github.com/tricore-opentrix/opentrix/issues/274)

**AS-IS baseline:** `main@e7cd26a6eac38bbd15ed5855ca1d5259b287b65d`

## Tóm tắt

Mỗi ứng dụng được định nghĩa bằng một file `apps/<app-id>/app.json`. **Chỉ phần khung** của manifest là định dạng riêng của OpenTrix, và khung này được mô tả hình thức bằng **JSON Schema 2020-12** (`schemas/app-manifest/v1/app-manifest.schema.json`). Mọi phần bên trong dùng lại chuẩn có sẵn: kiểu dữ liệu của entity là JSON Schema 2020-12, quy trình là BPMN 2.0, phiên bản là SemVer, giấy phép là SPDX, nhãn đa ngôn ngữ dùng thẻ BCP 47. ADR này chỉ quyết định định dạng; việc nạp manifest thuộc [#275](https://github.com/tricore-opentrix/opentrix/issues/275).

## Context

AS-IS on `main`, the only application is IT Helpdesk and it is hard-coded:

- Java code lives in the package `com.tricore.dxos.application.helpdesk`.
- Its database objects are SQL files under `backend/src/main/resources/db/helpdesk/`.
- Workflow runs on a self-written engine persisted in the `workflow_definition_*` tables (Flyway migrations `V3`, `V4`).

Adding a second application therefore means new Java code and new SQL. The platform needs an application model in which an application is data that the core reads, so that the format can be reviewed and tested on its own. The format must not invent rules where an established standard exists.

## Decision

1. **One manifest per application:** `apps/<app-id>/app.json`, a JSON document ([RFC 8259](https://www.rfc-editor.org/rfc/rfc8259)).
2. **The frame is the only OpenTrix-specific part and is formally described** by JSON Schema 2020-12 at `schemas/app-manifest/v1/app-manifest.schema.json`. Its `$id` contains `v1`; an incompatible change creates `v2/` beside it and a new ADR.
3. **Top-level keys** (`additionalProperties: false`; no other key is allowed):

   | Key           | Required | Content                                                                                      |
   | ------------- | -------- | -------------------------------------------------------------------------------------------- |
   | `id`          | yes      | Lowercase letters, digits and hyphens, starting with a letter                                |
   | `version`     | yes      | SemVer 2.0.0, using the regular expression published at semver.org                           |
   | `license`     | no       | SPDX License Identifier, checked by pattern only                                             |
   | `name`        | yes      | Object keyed by BCP 47 language tag, string values; `en` is required                         |
   | `description` | no       | Same shape as `name`                                                                         |
   | `entities`    | yes      | Object keyed by entity name; each value must itself be a valid JSON Schema 2020-12 document  |
   | `roles`       | no       | Object keyed by role name; each value has a multilingual `name`                              |
   | `workflow`    | no       | `bpmn` (relative path to a BPMN 2.0 file) and `processKey` (id of the BPMN process)          |

4. **Entities reuse the meta-schema.** The value of each entity is validated with `$ref: "https://json-schema.org/draft/2020-12/schema"`. OpenTrix defines no data-type syntax of its own; an entity with `"type": "text"` is rejected because `text` is not a JSON Schema type.
5. **Workflow stays in BPMN.** The manifest only points to the `.bpmn` file and names the process. States, steps and transitions are not described in JSON.
6. **Validation errors** will be reported with [RFC 6901](https://www.rfc-editor.org/rfc/rfc6901) JSON Pointers by the loader in #275.
7. **Test fixtures** in `backend/src/test/resources/manifests/` hold one valid manifest (reduced IT Helpdesk) and three invalid ones (missing `version`, entity with `"type": "text"`, unknown top-level key). `AppManifestSchemaTest` checks that the schema is valid against the 2020-12 meta-schema, that the valid manifest passes and that the invalid ones are rejected.

### Standards reused

| Standard                                | Used for                                                                                                          | Source                                       |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| JSON, RFC 8259                          | Manifest syntax                                                                                                   | <https://www.rfc-editor.org/rfc/rfc8259>     |
| JSON Schema 2020-12 (Core + Validation) | Description of the manifest frame; syntax of every entity                                                         | <https://json-schema.org/draft/2020-12>      |
| OpenAPI Specification 3.1               | Reference for API descriptions derived from entities; OAS 3.1 uses JSON Schema 2020-12 for its schema objects     | <https://spec.openapis.org/oas/v3.1.1>       |
| BPMN 2.0.2 / ISO/IEC 19510:2013         | Workflow definition file referenced by `workflow.bpmn`                                                            | <https://www.omg.org/spec/BPMN/2.0.2/>       |
| CloudEvents 1.0.2                       | Event envelope for platform events; not a key in format v1                                                        | <https://github.com/cloudevents/spec>        |
| Semantic Versioning 2.0.0               | `version`                                                                                                         | <https://semver.org/spec/v2.0.0.html>        |
| SPDX License List                       | `license`                                                                                                         | <https://spdx.org/licenses/>                 |
| BCP 47                                  | Language tags in `name` and `description`                                                                         | <https://www.rfc-editor.org/info/bcp47>      |
| RFC 6901, JSON Pointer                  | Locating errors in a manifest (#275)                                                                              | <https://www.rfc-editor.org/rfc/rfc6901>     |

## Consequences

- **Benefits:** the frame is machine-checkable by any JSON Schema 2020-12 validator; entity syntax needs no OpenTrix-specific documentation; workflow definitions can be edited with standard BPMN tools; a manifest error is found before the application starts.
- **Costs:** BPMN needs a runtime that executes it; the existing self-written engine is not changed by this ADR. `license` is checked by pattern only, so a well-formed but unknown identifier passes. Because unknown keys are rejected, adding a key needs a schema change and a new format version.
- **Dependency:** the test uses `com.networknt:json-schema-validator` 3.0.9 (Apache-2.0) as a `testImplementation` dependency. It is not on the runtime classpath, so the generated `THIRD-PARTY-NOTICES.md` is unchanged.
- **Out of scope here:** loading manifests, creating tables or code from entities, migrating the current Helpdesk to a manifest, and any change to the workflow engine (#275 and later issues).
- **Open point:** issue #274 lists an `events` key (CloudEvents types) in its scope. Format v1 as decided here has no `events` key; it can be added in a later schema version.

## Alternatives considered

| Option                                              | Reason not selected                                                                                                                  |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| CNCF Serverless Workflow 1.0 for the workflow       | No stable Java runtime supporting version 1.0 was available for the backend                                                          |
| Generate dedicated DDL tables per application       | Ties each application to a schema migration; the manifest would describe tables instead of data and could not be validated on its own |
| Define OpenTrix's own data-type syntax for entities | A second type system to specify, document and maintain, with no benefit over JSON Schema 2020-12                                     |

## References

- [#274](https://github.com/tricore-opentrix/opentrix/issues/274), [#275](https://github.com/tricore-opentrix/opentrix/issues/275)
- [ADR-009](ADR-009-modular-monolith-flowable.md) · [ADR-017](ADR-017-helpdesk-first-scope.md)
- Schema: [`schemas/app-manifest/v1/app-manifest.schema.json`](../../schemas/app-manifest/v1/app-manifest.schema.json)
