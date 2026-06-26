import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///C:/tmp/phase3_specialized_ai_test.db"
os.environ["FINDNA_BASE_URL"] = "http://127.0.0.1:1"

db_path = Path("C:/tmp/phase3_specialized_ai_test.db")
if db_path.exists():
    db_path.unlink()

from services.findna.app.main import (
    AICreditEngineRequest,
    BankStatementAnalysisRequest,
    BankStatementTransaction,
    Base as FindnaBase,
    SessionLocal as FindnaSessionLocal,
    ai_credit_engine,
    analyze_bank_statement,
    engine as findna_engine,
)
from services.gold.app.main import (
    AuctionCreate,
    Base as GoldBase,
    GoldLoanCreate,
    OrnamentCreate,
    PurityTestRequest,
    SessionLocal as GoldSessionLocal,
    VaultPacketCreate,
    catalog_ornament,
    create_auction_case,
    create_gold_loan,
    engine as gold_engine,
    get_customer_receipt,
    record_purity_test,
    startup as gold_startup,
    store_in_vault,
)
from services.los.app import main as los_main
from services.los.app.main import (
    Base as LosBase,
    LoanApplicationCreate,
    SessionLocal as LosSessionLocal,
    create_application,
    engine as los_engine,
    startup as los_startup,
    submit_application,
    underwrite_application,
)
from services.treasury.app.main import (
    Base as TreasuryBase,
    CashInventoryAdjust,
    ExchangeRateCreate,
    ForexTransactionCreate,
    SessionLocal as TreasurySessionLocal,
    adjust_cash_inventory,
    create_forex_transaction,
    engine as treasury_engine,
    startup as treasury_startup,
    upsert_exchange_rate,
)


def run(coro):
    return asyncio.run(coro)


def test_findna_bank_statement_and_ai_credit_engine():
    FindnaBase.metadata.drop_all(bind=findna_engine)
    FindnaBase.metadata.create_all(bind=findna_engine)
    db = FindnaSessionLocal()
    try:
        statement = run(
            analyze_bank_statement(
                BankStatementAnalysisRequest(
                    customer_id="customer-1",
                    application_id="app-1",
                    transactions=[
                        BankStatementTransaction(
                            transaction_date=datetime(2026, 1, 1),
                            description="Salary",
                            amount=90000,
                            transaction_type="credit",
                            balance_after=120000,
                        ),
                        BankStatementTransaction(
                            transaction_date=datetime(2026, 1, 5),
                            description="Rent",
                            amount=30000,
                            transaction_type="debit",
                            balance_after=90000,
                        ),
                        BankStatementTransaction(
                            transaction_date=datetime(2026, 1, 15),
                            description="Utility debit",
                            amount=7000,
                            transaction_type="debit",
                            balance_after=83000,
                        ),
                    ],
                ),
                db,
            )
        )
        assert statement["average_balance"] > 0
        assert statement["monthly_income"] > 0

        decision = run(
            ai_credit_engine(
                AICreditEngineRequest(
                    customer_id="customer-1",
                    application_id="app-1",
                    requested_amount=200000,
                    tenure_months=24,
                    declared_monthly_income=90000,
                    credit_score=760,
                ),
                db,
            )
        )
        assert decision["recommendation"] in {"approve", "review", "decline"}
        assert decision["ai_risk_score"] > 0
        assert decision["risk_grade"] in {"A", "B", "C", "D"}
    finally:
        db.close()


def test_los_underwriting_persists_ai_credit_fields():
    LosBase.metadata.drop_all(bind=los_engine)
    run(los_startup())
    db = LosSessionLocal()
    original = los_main.get_ai_credit_decision
    los_main.get_ai_credit_decision = lambda application: {
        "ai_risk_score": 81.5,
        "recommendation": "approve",
        "risk_grade": "A",
        "reasons": ["Strong bank statement liquidity."],
    }
    try:
        application = run(
            create_application(
                LoanApplicationCreate(
                    customer_id="customer-1",
                    product_code="PERSONAL_LOAN",
                    applied_amount=200000,
                    tenure_months=24,
                ),
                db,
            )
        )
        run(submit_application(application.id, db))
        scorecard = run(underwrite_application(application.id, db))
        assert scorecard.ai_risk_score == 81.5
        assert scorecard.ai_recommendation == "approve"
        assert scorecard.recommendation == "approve"
    finally:
        los_main.get_ai_credit_decision = original
        db.close()


def test_gold_loan_ornament_vault_receipt_and_auction_flow():
    GoldBase.metadata.drop_all(bind=gold_engine)
    run(gold_startup())
    db = GoldSessionLocal()
    try:
        application = run(
            create_gold_loan(
                GoldLoanCreate(
                    customer_id="customer-1",
                    branch_id="branch-1",
                    requested_amount=150000,
                    gold_rate_per_gram=6000,
                ),
                db,
            )
        )
        ornament = run(
            catalog_ornament(
                application.id,
                OrnamentCreate(
                    ornament_type="necklace",
                    gross_weight_grams=40,
                    stone_weight_grams=2,
                    purity_karat=22,
                ),
                db,
            )
        )
        assert ornament.net_weight_grams == 38
        retested = run(record_purity_test(ornament.id, PurityTestRequest(purity_karat=21.5), db))
        assert retested.purity_percent < 91.7

        packet = run(
            store_in_vault(
                application.id,
                VaultPacketCreate(
                    vault_location="vault-a/shelf-2",
                    sealed_by_user_id="employee-1",
                    seal_reference="SEAL-1",
                ),
                db,
            )
        )
        assert packet.packet_number.startswith("GLP-")

        receipt = run(get_customer_receipt(application.id, db))
        assert receipt["vault_packet"].packet_number == packet.packet_number

        auction = run(
            create_auction_case(
                application.id,
                AuctionCreate(
                    trigger_reason="90+ DPD",
                    auction_date=datetime.utcnow() + timedelta(days=30),
                ),
                db,
            )
        )
        assert auction.status == "scheduled"
    finally:
        db.close()


def test_treasury_exchange_rate_cash_inventory_and_forex_flow():
    TreasuryBase.metadata.drop_all(bind=treasury_engine)
    run(treasury_startup())
    db = TreasurySessionLocal()
    try:
        rate = run(
            upsert_exchange_rate(
                ExchangeRateCreate(
                    base_currency="USD",
                    quote_currency="INR",
                    buy_rate=82.5,
                    sell_rate=84.0,
                ),
                db,
            )
        )
        assert rate.sell_rate >= rate.buy_rate

        inventory = run(
            adjust_cash_inventory(
                CashInventoryAdjust(
                    branch_id="branch-1",
                    currency="INR",
                    amount=100000,
                    movement_type="inflow",
                ),
                db,
            )
        )
        assert inventory.cash_on_hand == 100000

        transaction = run(
            create_forex_transaction(
                ForexTransactionCreate(
                    branch_id="branch-1",
                    customer_id="customer-1",
                    transaction_type="buy",
                    base_currency="USD",
                    quote_currency="INR",
                    base_amount=100,
                    reference="FX-1",
                ),
                db,
            )
        )
        assert transaction.quote_amount == 8250
        assert transaction.rate_applied == 82.5
    finally:
        db.close()
