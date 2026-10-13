from decimal import Decimal
from tests.conftest import client, sample_loan  # noqa: F401
from app.loans import calculate_emi


def test_health(client):
    assert client.get("/health").json() == {"status": "UP"}


def test_root_branding(client):
    assert client.get("/").json()["service"] == "LoanBoard API"


def test_create_loan_returns_emi(client):
    r = client.post("/api/loans", json=sample_loan())
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["status"] == "submitted"
    expected = calculate_emi(Decimal("500000"), Decimal("8.5"), 120)
    assert Decimal(str(body["emi"])) == expected


def test_emi_known_value():
    # P=100000, 12% annual, 12 months -> r=0.01 -> EMI ≈ 8884.88
    assert calculate_emi(Decimal("100000"), Decimal("12"), 12) == Decimal("8884.88")


def test_get_update_delete_loan(client):
    created = client.post("/api/loans", json=sample_loan()).json()
    lid = created["id"]
    assert client.get(f"/api/loans/{lid}").status_code == 200
    upd = client.put(f"/api/loans/{lid}", json={"tenure_months": 60})
    assert upd.status_code == 200
    assert upd.json()["emi"] != created["emi"]
    assert client.delete(f"/api/loans/{lid}").status_code == 204
    assert client.get(f"/api/loans/{lid}").status_code == 404


def test_loan_404(client):
    assert client.get("/api/loans/9999").status_code == 404


def test_valid_status_flow(client):
    lid = client.post("/api/loans", json=sample_loan()).json()["id"]
    assert client.patch(f"/api/loans/{lid}/status", json={"status": "under_review"}).status_code == 200
    assert client.patch(f"/api/loans/{lid}/status", json={"status": "approved"}).status_code == 200
    assert client.patch(f"/api/loans/{lid}/status", json={"status": "disbursed"}).status_code == 200


def test_invalid_status_transition_returns_400(client):
    lid = client.post("/api/loans", json=sample_loan()).json()["id"]
    r = client.patch(f"/api/loans/{lid}/status", json={"status": "approved"})
    assert r.status_code == 400
    assert "Invalid status transition" in r.json()["detail"]


def test_terminal_state_rejected(client):
    lid = client.post("/api/loans", json=sample_loan()).json()["id"]
    client.patch(f"/api/loans/{lid}/status", json={"status": "under_review"})
    client.patch(f"/api/loans/{lid}/status", json={"status": "rejected"})
    r = client.patch(f"/api/loans/{lid}/status", json={"status": "approved"})
    assert r.status_code == 400


def test_validation_failures(client):
    assert client.post("/api/loans", json=sample_loan(principal_amount="0")).status_code == 422
    assert client.post("/api/loans", json=sample_loan(tenure_months=5)).status_code == 422
    assert client.post("/api/loans", json=sample_loan(tenure_months=400)).status_code == 422
    assert client.post("/api/loans", json=sample_loan(annual_interest_rate="0.5")).status_code == 422
    assert client.post("/api/loans", json=sample_loan(annual_interest_rate="45")).status_code == 422
    assert client.post("/api/loans", json=sample_loan(email="not-an-email")).status_code == 422
    assert client.post("/api/loans", json=sample_loan(loan_type="boat")).status_code == 422


def test_list_filters(client):
    client.post("/api/loans", json=sample_loan(loan_type="home"))
    client.post("/api/loans", json=sample_loan(email="b@example.com", loan_type="auto"))
    assert len(client.get("/api/loans").json()) == 2
    assert len(client.get("/api/loans", params={"loan_type": "auto"}).json()) == 1
    assert len(client.get("/api/loans", params={"status": "submitted"}).json()) == 2
    assert client.get("/api/loans", params={"status": "approved"}).json() == []


def test_stats(client):
    client.post("/api/loans", json=sample_loan(principal_amount="100000"))
    lid2 = client.post("/api/loans", json=sample_loan(email="c@example.com", principal_amount="200000")).json()["id"]
    client.patch(f"/api/loans/{lid2}/status", json={"status": "under_review"})
    client.patch(f"/api/loans/{lid2}/status", json={"status": "approved"})
    client.patch(f"/api/loans/{lid2}/status", json={"status": "disbursed"})
    body = client.get("/api/loans/stats").json()
    assert body["total"] == 2
    assert body["approved"] == 0  # approved moved on to disbursed
    assert body["pending"] == 1
    assert Decimal(str(body["disbursed_total"])) == Decimal("200000")
    assert Decimal(str(body["average_loan_size"])) == Decimal("150000")

