from backend.phonology.segre_transcriber import transcribe


def test_central_basic():
    out = transcribe("llengua", dialect="central")[0]
    assert "ʎ" in out


def test_balearic_basic():
    out = transcribe("conyac", dialect="balearic")[0]
    assert any(sym in out for sym in ["ɲ", "ʎ"])  # demo rule coverage


def test_valencian_basic():
    out = transcribe("taxi", dialect="valencian")[0]
    assert "ks" in out  # from char_map


