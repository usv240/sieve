from sieve_vision import _data_url


def test_png_is_declared_as_png_and_jpeg_as_jpeg():
    assert _data_url(b"\x89PNG\r\n\x1a\nrest").startswith("data:image/png;")
    assert _data_url(b"\xff\xd8\xffrest").startswith("data:image/jpeg;")
