import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

istemci = TestClient(app)


def test_saglik():
    assert istemci.get("/saglik").json() == {"durum": "ok"}


def test_olustur_ve_getir():
    r = istemci.post("/gorevler", json={"baslik": "Rapor yaz", "oncelik": 2})
    assert r.status_code == 201
    gorev = r.json()
    assert gorev["durum"] == "yapilacak"
    assert istemci.get(f"/gorevler/{gorev['id']}").json()["baslik"] == "Rapor yaz"


def test_gecersiz_oncelik_422():
    r = istemci.post("/gorevler", json={"baslik": "x", "oncelik": 9})
    assert r.status_code == 422


def test_guncelle_ve_filtrele():
    gid = istemci.post("/gorevler", json={"baslik": "Test görevi"}).json()["id"]
    r = istemci.patch(f"/gorevler/{gid}", json={"durum": "tamamlandi"})
    assert r.json()["durum"] == "tamamlandi"
    liste = istemci.get("/gorevler", params={"durum": "tamamlandi"}).json()
    assert any(g["id"] == gid for g in liste)


def test_arama():
    istemci.post("/gorevler", json={"baslik": "Benzersizkelime çalış"})
    sonuc = istemci.get("/gorevler", params={"arama": "benzersizkelime"}).json()
    assert len(sonuc) == 1


def test_sil_ve_404():
    gid = istemci.post("/gorevler", json={"baslik": "Silinecek"}).json()["id"]
    assert istemci.delete(f"/gorevler/{gid}").status_code == 204
    assert istemci.get(f"/gorevler/{gid}").status_code == 404
