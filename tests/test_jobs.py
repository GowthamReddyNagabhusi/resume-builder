from __future__ import annotations


def test_jobs_crud_and_validation(client, auth_headers):
    created = client.post(
        "/api/jobs",
        json={"company": "Acme", "role": "Backend Intern", "link": "", "notes": ""},
        headers=auth_headers,
    )
    assert created.status_code == 200
    app_id = created.json()["id"]

    listed = client.get("/api/jobs?page=1&per_page=20", headers=auth_headers)
    assert listed.status_code == 200
    data = listed.json()
    assert "total" in data
    assert "pages" in data

    updated = client.put(f"/api/jobs/{app_id}", json={"status": "interview"}, headers=auth_headers)
    assert updated.status_code == 200

    bad = client.put(f"/api/jobs/{app_id}", json={"status": "invalid"}, headers=auth_headers)
    assert bad.status_code == 400

    deleted = client.delete(f"/api/jobs/{app_id}", headers=auth_headers)
    assert deleted.status_code == 200


def test_jobs_require_auth(client):
    res = client.get("/api/jobs")
    assert res.status_code == 401
