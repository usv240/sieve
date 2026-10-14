from sieve_core import Registry, verify_quote


def test_registry_loads_and_cites_pages():
    r = Registry()
    ev = r.get("philips-everflo")
    assert ev and ev["indicators"]
    for ind in ev["indicators"]:
        assert ind["cite"]["doc"] and ind["cite"]["page"] > 0


def test_match_everflo_from_nameplate_text():
    r = Registry()
    m = r.match(manufacturer="Philips Respironics", model="EverFlo", ref="1020000")
    assert m and m[0].device_id == "philips-everflo" and m[0].confidence >= 0.9


def test_match_devilbiss_525_from_ocr_noise():
    r = Registry()
    m = r.match(manufacturer="DeVilbiss Healthcare", model=None, ref=None, visible_text=["525DS", "Oxygen Concentrator", "115V"])
    assert m and m[0].device_id == "devilbiss-525"


def test_unknown_device_returns_low_or_no_match():
    r = Registry()
    m = r.match(manufacturer="Acme", model="Kettle 3000", ref=None, visible_text=["1.7 L", "2200 W"])
    assert not m or m[0].confidence < 0.6


def test_pick_questions_includes_patient_safety_first():
    r = Registry()
    qs = r.pick_questions("philips-everflo", ["everflo-yellow-solid-silent"])
    assert qs and qs[0]["id"] == "in_use" and len(qs) <= 3


def test_verify_quote_exact_and_normalised():
    page = "Yellow LED illuminates continuously. The Red LED is off and the Audible\nAlarm is silent. The device has detected a low oxygen condition."
    assert verify_quote("The device has detected a low oxygen condition.", page).ok
    assert verify_quote("Red LED is off and the Audible Alarm is silent", page).ok
    assert not verify_quote("The device has detected a high oxygen condition.", page).ok
    assert not verify_quote("anything", None).ok


def test_verify_quote_tolerates_pdf_artefacts():
    page = (
        "CAUTION– Operation of the DeVilbiss Oxygen Concentrator in extreme\n"
        "environments or without the air filter may damage the unit.  3.  Exhaust is\n"
        "blocked.   Check the exhaust area."
    )
    v = verify_quote("CAUTION- Operation of the DeVilbiss Oxygen Concentrator in extreme environments", page)
    assert v.ok and v.tier in ("verbatim", "normalised")
    v = verify_quote("3. Exhaust is blocked. 3. Check the exhaust area", page)
    assert v.ok and v.tier in ("normalised", "fuzzy")
    assert not verify_quote("Replace the compressor with part number 999-123 immediately", page).ok
