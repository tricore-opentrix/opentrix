# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
"""Static guardrails for the local Keycloak login theme (not runtime acceptance)."""
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "infra/keycloak/themes/opentrix/login"
KEYCLOAK_IMAGE = "quay.io/keycloak/keycloak:26.8.0"


class KeycloakThemeContracts(unittest.TestCase):
    def test_realm_login_theme_only_is_configured(self):
        realm = json.loads((ROOT / "infra/keycloak/tricore-realm.json").read_text(encoding="utf-8"))
        self.assertEqual(realm["realm"], "tricore")
        self.assertEqual(realm["loginTheme"], "opentrix")
        self.assertFalse(any(c.get("directAccessGrantsEnabled", False) for c in realm["clients"]))
        client = next(c for c in realm["clients"] if c["clientId"] == "dxos-portal-bff-local")
        self.assertTrue(client["standardFlowEnabled"])
        self.assertEqual(client["attributes"]["pkce.code.challenge.method"], "S256")
        self.assertEqual(client["redirectUris"], ["https://localhost:8443/login/oauth2/code/keycloak"])
        # Vietnamese is the only and default locale: <html lang="vi">, no language picker.
        self.assertTrue(realm["internationalizationEnabled"])
        self.assertEqual(realm["supportedLocales"], ["vi"])
        self.assertEqual(realm["defaultLocale"], "vi")

    def test_style_only_inherited_theme(self):
        props = (THEME / "theme.properties").read_text(encoding="utf-8")
        self.assertIn("parent=keycloak.v2", props)
        self.assertIn("styles=css/styles.css css/opentrix.css", props)
        self.assertEqual(list(THEME.rglob("*.ftl")), [],
                         "Do not copy upstream Keycloak FreeMarker templates into this theme")
        self.assertFalse(any(THEME.rglob("*.js")), "Do not inject login Javascript")
        self.assertEqual((THEME / "resources/img/opentrix-clover.svg").read_bytes(),
                         (ROOT / "frontend/src/assets/opentrix-clover.svg").read_bytes())

    def test_stock_keycloak_templates_are_inherited(self):
        """Only style/messages/assets live here; Keycloak owns the form and field templates."""
        self.assertFalse((THEME / "field.ftl").exists())
        self.assertFalse((THEME / "login.ftl").exists())
        self.assertFalse((THEME / "template.ftl").exists())
        props = (THEME / "theme.properties").read_text(encoding="utf-8")
        self.assertIn("parent=keycloak.v2", props)
        compose = (ROOT / "infra/compose.demo.yml").read_text(encoding="utf-8")
        self.assertIn(KEYCLOAK_IMAGE, compose,
                      "Revalidate inherited markup and responsive CSS on Keycloak upgrades")

    def test_message_bundles_are_per_language(self):
        bundles = {}
        for lang in ("vi", "en"):
            text = (THEME / f"messages/messages_{lang}.properties").read_text(encoding="utf-8")
            bundles[lang] = dict(line.split("=", 1) for line in text.splitlines()
                                 if line and not line.startswith("#"))
        self.assertEqual(bundles["vi"]["username"], "Tên đăng nhập")
        self.assertEqual(bundles["vi"]["doLogIn"], "Đăng nhập")
        self.assertNotRegex("".join(bundles["en"].values()), r"[À-ỹ]", "English bundle must not contain Vietnamese")
        self.assertLessEqual(set(bundles["en"]), set(bundles["vi"]))
        # Same meaning as Keycloak's stock message: never reveal which field or whether the account exists.
        self.assertEqual(bundles["vi"]["invalidUserMessage"], bundles["vi"]["accountTemporarilyDisabledMessage"])

    def test_brand_panel_is_inert_markup_and_assets_are_local(self):
        """The two-column layout must stay CSS + sanitized message markup, never a second form."""
        for bundle in sorted(THEME.glob("messages/messages_*.properties")):
            messages = bundle.read_text(encoding="utf-8")
            brand = next(line for line in messages.splitlines() if line.startswith("loginTitleHtml="))
            tags = set(re.findall(r"<\s*/?\s*([a-zA-Z0-9]+)", brand))
            self.assertLessEqual(tags, {"div", "span", "p", "ul", "li"}, f"{bundle.name}: inert text markup only")
            for forbidden in ("href", "src=", "style=", "javascript:", " on", "http"):
                self.assertNotIn(forbidden, brand.lower(), bundle.name)
        self.assertTrue((THEME / "resources/img/opentrix-helpdesk-illustration.svg").is_file())
        for asset in list(THEME.rglob("*.css")) + list(THEME.rglob("*.svg")) + list(THEME.rglob("*.properties")):
            text = asset.read_text(encoding="utf-8")
            external = [u for u in re.findall(r"(?:https?:)?//[^\s\"')>]+", text) if "www.w3.org/2000/svg" not in u]
            self.assertEqual(external, [], f"{asset.name} must not load external resources")
            self.assertNotIn("@import", text)
            self.assertNotIn("<script", text.lower())

    def test_theme_does_not_hide_keycloak_feedback_or_controls(self):
        css = (THEME / "resources/css/opentrix.css").read_text(encoding="utf-8")
        rules = re.findall(r"([^{}]+)\{([^{}]*)\}", css)
        protected = ("kc-form", "input-error", "alert", "helper-text", "form__label", "password", "kc-login", "#username")
        for selector, body in rules:
            if re.search(r"display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0\s*;", body):
                self.assertFalse(any(p in selector for p in protected),
                                 f"Theme must not hide Keycloak form/feedback: {selector.strip()}")
        self.assertIsNone(re.search(r"overflow(-[xy])?\s*:\s*(hidden|clip)", css),
                          "Never clip the card: long Keycloak error messages must stay fully visible")
        self.assertIn("overflow-wrap: anywhere", css)
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn(":focus-visible", css)
        props = (THEME / "theme.properties").read_text(encoding="utf-8")
        self.assertIn("darkMode=false", props)

    def test_compose_mount_and_idempotent_existing_realm_update(self):
        compose = (ROOT / "infra/compose.demo.yml").read_text(encoding="utf-8")
        self.assertIn("./keycloak/themes/opentrix:/opt/keycloak/themes/opentrix:ro", compose)
        kc_init = (ROOT / "infra/demo/init/kc-init.sh").read_text(encoding="utf-8")
        self.assertIn('update realms/tricore --config $CFG -s "loginTheme=opentrix"', kc_init)
        self.assertIn("""-s internationalizationEnabled=true -s 'supportedLocales=["vi"]' -s defaultLocale=vi""", kc_init)
        self.assertNotIn("delete realms/tricore", kc_init)


if __name__ == "__main__":
    unittest.main()
