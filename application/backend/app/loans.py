from decimal import Decimal, ROUND_HALF_UP, getcontext

getcontext().prec = 28

TWOPLACES = Decimal("0.01")

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "submitted": {"under_review"},
    "under_review": {"approved", "rejected"},
    "approved": {"disbursed"},
    "rejected": set(),
    "disbursed": set(),
}

VALID_STATUSES = ("submitted", "under_review", "approved", "rejected", "disbursed")
VALID_LOAN_TYPES = ("personal", "home", "auto", "education")


def calculate_emi(principal: Decimal, annual_rate: Decimal, tenure_months: int) -> Decimal:
    """Reducing-balance EMI: P*r*(1+r)^n / ((1+r)^n - 1), r = annual_rate/12/100."""
    p = Decimal(principal)
    n = int(tenure_months)
    r = Decimal(annual_rate) / Decimal(12) / Decimal(100)
    if r == 0:
        emi = p / n
    else:
        factor = (Decimal(1) + r) ** n
        emi = p * r * factor / (factor - Decimal(1))
    return emi.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def next_states(status: str) -> list[str]:
    return sorted(ALLOWED_TRANSITIONS.get(status, set()))


def validate_transition(current: str, target: str) -> None:
    from fastapi import HTTPException

    if target not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status '{target}'.")
    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        if not allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Loan is '{current}' and cannot transition to '{target}'. Terminal state.",
            )
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition from '{current}' to '{target}'. Allowed: {', '.join(sorted(allowed))}.",
        )
