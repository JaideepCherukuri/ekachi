from app.application.services.secret_cipher import SecretCipher


def test_secret_cipher_round_trip():
    cipher = SecretCipher("test-secret")

    encrypted = cipher.encrypt("sk-live-value")

    assert encrypted != "sk-live-value"
    assert cipher.decrypt(encrypted) == "sk-live-value"


def test_secret_cipher_is_stable_for_same_master_key():
    value = "provider-token"

    encrypted = SecretCipher("shared-secret").encrypt(value)

    assert SecretCipher("shared-secret").decrypt(encrypted) == value
