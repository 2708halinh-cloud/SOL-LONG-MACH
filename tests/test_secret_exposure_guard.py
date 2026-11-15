import unittest

from security.secret_exposure_guard import PATTERNS


def detected_categories(sample):
    return {
        category
        for category, pattern in PATTERNS.items()
        if pattern.search(sample)
    }


class SecretExposureGuardTests(unittest.TestCase):
    def test_detects_authorization_bearer_header_in_network_dump(self):
        header = "author" + "ization"
        credential = "SYNTHETIC" + "-CREDENTIAL-" + "0123456789ABCDEFGHIJK"
        sample = f"{header}\nBearer {credential}"
        self.assertIn("authorization_header_credential", detected_categories(sample))

    def test_detects_cookie_header_and_session_cookie_value(self):
        header = "cook" + "ie"
        cookie_name = "__Secure-next-auth." + "session-token.0"
        cookie_value = "SYNTHETIC" + "_SESSION_VALUE_" + "0123456789"
        sample = f"{header}\n{cookie_name}={cookie_value}"
        found = detected_categories(sample)
        self.assertIn("cookie_header_value", found)
        self.assertIn("session_cookie_value", found)

    def test_detects_inline_authorization_header(self):
        header = "author" + "ization"
        credential = "SYNTHETIC" + "-INLINE-CREDENTIAL-" + "0123456789"
        sample = f"{header}: Bearer {credential}"
        self.assertIn("authorization_header_credential", detected_categories(sample))

    def test_detects_inline_cookie_header(self):
        header = "cook" + "ie"
        cookie_name = "__Secure-next-auth." + "session-token.0"
        cookie_value = "SYNTHETIC" + "_INLINE_SESSION_VALUE_" + "0123456789"
        sample = f"{header}: {cookie_name}={cookie_value}"
        self.assertIn("cookie_header_value", detected_categories(sample))
        self.assertIn("session_cookie_value", detected_categories(sample))

    def test_detects_inline_account_identifier_header(self):
        header = "chatgpt-account" + "-id"
        synthetic_id = "12345678-1234-1234-1234-123456789abc"
        sample = f"{header}: {synthetic_id}"
        self.assertIn("account_identifier_header", detected_categories(sample))

    def test_detects_chatgpt_account_identifier_header(self):
        header = "chatgpt-account" + "-id"
        synthetic_id = "12345678-1234-1234-1234-123456789abc"
        sample = f"{header}\n{synthetic_id}"
        self.assertIn("account_identifier_header", detected_categories(sample))

    def test_redacted_network_dump_does_not_trigger_new_header_rules(self):
        sample = "\n".join([
            "authorization",
            "Bearer [REDACTED: authentication credential]",
            "cookie",
            "[REDACTED: session or security cookie]",
            "chatgpt-account-id",
            "[REDACTED: account identifier]",
        ])
        found = detected_categories(sample)
        self.assertNotIn("authorization_header_credential", found)
        self.assertNotIn("cookie_header_value", found)
        self.assertNotIn("session_cookie_value", found)
        self.assertNotIn("account_identifier_header", found)

        inline_redacted = "\n".join([
            "authorization: Bearer [REDACTED: authentication credential]",
            "cookie: [REDACTED: session or security cookie]",
            "chatgpt-account-id: [REDACTED: account identifier]",
        ])
        inline_found = detected_categories(inline_redacted)
        self.assertNotIn("authorization_header_credential", inline_found)
        self.assertNotIn("cookie_header_value", inline_found)
        self.assertNotIn("session_cookie_value", inline_found)
        self.assertNotIn("account_identifier_header", inline_found)


if __name__ == "__main__":
    unittest.main()
