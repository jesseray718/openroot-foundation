import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from openroot_canon import coord, derive, newton


def test_r1_zero():
    assert coord(6, 1, 1.0) == 0.0
    assert coord(36, 2, 1.0) == 0.0


def test_newton_gamma():
    hits = newton("what is gamma")
    assert hits and hits[0]["id"] == "N02"


def test_solana_is_n10():
    d = derive("put it on Solana so it exists")
    assert d["path"] == "Newton"
    assert any(h["id"] == "N10" for h in d["hits"])


if __name__ == "__main__":
    test_r1_zero()
    test_newton_gamma()
    test_solana_is_n10()
    print("ok")
