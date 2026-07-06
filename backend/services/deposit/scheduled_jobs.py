"""
Scheduled Jobs for Deposit Management

Background jobs that run automatically:
- Daily interest posting
- Monthly MIS payouts
- Maturity processing
- Dormancy checks
- Penalty application
- Notification sending
"""

from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import date, datetime, timedelta
import logging

from backend.shared.database.connection import get_db
from .batch_service import BatchProcessingService
from .notification_service import NotificationService
from .standing_instructions_service import StandingInstructionService

logger = logging.getLogger(__name__)


class DepositScheduledJobs:
    """Scheduled jobs for deposit management"""
    
    def __init__(self, tenant_id: int, user_id: int = 1):
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    def run_daily_jobs(self, db: Session) -> Dict[str, Any]:
        """
        Run daily scheduled jobs
        
        Should be scheduled via cron/scheduler to run every day at specific time
        """
        logger.info(f"Starting daily jobs for tenant {self.tenant_id}")
        
        results = {
            "job_date": date.today().isoformat(),
            "tenant_id": self.tenant_id,
            "jobs": []
        }
        
        try:
            # 1. Process maturity queue
            batch_service = BatchProcessingService(db, self.tenant_id, self.user_id)
            maturity_result = batch_service.process_maturity_batch(days_ahead=0)
            results["jobs"].append({
                "job": "maturity_processing",
                "status": "completed",
                "result": maturity_result
            })
            logger.info(f"Maturity processing: {maturity_result['processed']} accounts processed")
        
        except Exception as e:
            logger.error(f"Maturity processing failed: {str(e)}")
            results["jobs"].append({
                "job": "maturity_processing",
                "status": "failed",
                "error": str(e)
            })
        
        try:
            # 2. Execute auto-debit instructions
            si_service = StandingInstructionService(db, self.tenant_id, self.user_id)
            auto_debit_result = si_service.execute_auto_debit_instructions()
            results["jobs"].append({
                "job": "auto_debit_execution",
                "status": "completed",
                "result": auto_debit_result
            })
            logger.info(f"Auto-debit: {auto_debit_result['executed']} executed")
        
        except Exception as e:
            logger.error(f"Auto-debit execution failed: {str(e)}")
            results["jobs"].append({
                "job": "auto_debit_execution",
                "status": "failed",
                "error": str(e)
            })
        
        try:
            # 3. Execute sweep instructions
            sweep_result = si_service.execute_sweep_instructions()
            results["jobs"].append({
                "job": "sweep_execution",
                "status": "completed",
                "result": sweep_result
            })
            logger.info(f"Sweep: {sweep_result['executed']} executed")
        
        except Exception as e:
            logger.error(f"Sweep execution failed: {str(e)}")
            results["jobs"].append({
                "job": "sweep_execution",
                "status": "failed",
                "error": str(e)
            })
        
        try:
            # 4. Send maturity reminders (30 days before)
            notification_service = NotificationService(db, self.tenant_id, self.user_id)
            maturity_reminders = notification_service.send_maturity_reminders(days_before=30)
            results["jobs"].append({
                "job": "maturity_reminders",
                "status": "completed",
                "result": {"sent": maturity_reminders['accounts_notified']}
            })
            logger.info(f"Maturity reminders: {maturity_reminders['accounts_notified']} sent")
        
        except Exception as e:
            logger.error(f"Maturity reminders failed: {str(e)}")
            results["jobs"].append({
                "job": "maturity_reminders",
                "status": "failed",
                "error": str(e)
            })
        
        try:
            # 5. Send RD installment reminders (3 days before)
            rd_reminders = notification_service.send_rd_installment_reminders(days_before=3)
            results["jobs"].append({
                "job": "rd_reminders",
                "status": "completed",
                "result": {"sent": rd_reminders['accounts_notified']}
            })
            logger.info(f"RD reminders: {rd_reminders['accounts_notified']} sent")
        
        except Exception as e:
            logger.error(f"RD reminders failed: {str(e)}")
            results["jobs"].append({
                "job": "rd_reminders",
                "status": "failed",
                "error": str(e)
            })
        
        logger.info(f"Daily jobs completed for tenant {self.tenant_id}")
        return results
    
    def run_monthly_jobs(self, db: Session) -> Dict[str, Any]:
        """
        Run monthly scheduled jobs
        
        Should be scheduled to run on 1st of every month
        """
        logger.info(f"Starting monthly jobs for tenant {self.tenant_id}")
        
        results = {
            "job_date": date.today().isoformat(),
            "tenant_id": self.tenant_id,
            "jobs": []
        }
        
        try:
            # 1. Process MIS payouts
            batch_service = BatchProcessingService(db, self.tenant_id, self.user_id)
            mis_result = batch_service.process_mis_payout_batch()
            results["jobs"].append({
                "job": "mis_payout",
                "status": "completed",
                "result": mis_result
            })
            logger.info(f"MIS payout: {mis_result['accounts_processed']} processed")
        
        except Exception as e:
            logger.error(f"MIS payout failed: {str(e)}")
            results["jobs"].append({
                "job": "mis_payout",
                "status": "failed",
                "error": str(e)
            })
        
        try:
            # 2. Post interest for savings accounts
            interest_result = batch_service.schedule_interest_posting(
                posting_date=date.today(),
                account_type='savings'
            )
            results["jobs"].append({
                "job": "interest_posting",
                "status": "completed",
                "result": interest_result
            })
            logger.info(f"Interest posting: {interest_result['accounts_processed']} processed")
        
        except Exception as e:
            logger.error(f"Interest posting failed: {str(e)}")
            results["jobs"].append({
                "job": "interest_posting",
                "status": "failed",
                "error": str(e)
            })
        
        try:
            # 3. Apply minimum balance penalties
            penalty_result = batch_service.apply_penalties_batch(penalty_type='min_balance')
            results["jobs"].append({
                "job": "min_balance_penalties",
                "status": "completed",
                "result": penalty_result
            })
            logger.info(f"Min balance penalties: {penalty_result['penalties_applied']} applied")
        
        except Exception as e:
            logger.error(f"Min balance penalties failed: {str(e)}")
            results["jobs"].append({
                "job": "min_balance_penalties",
                "status": "failed",
                "error": str(e)
            })
        
        try:
            # 4. Apply RD missed installment penalties
            rd_penalty_result = batch_service.apply_penalties_batch(penalty_type='rd_missed')
            results["jobs"].append({
                "job": "rd_penalties",
                "status": "completed",
                "result": rd_penalty_result
            })
            logger.info(f"RD penalties: {rd_penalty_result['penalties_applied']} applied")
        
        except Exception as e:
            logger.error(f"RD penalties failed: {str(e)}")
            results["jobs"].append({
                "job": "rd_penalties",
                "status": "failed",
                "error": str(e)
            })
        
        try:
            # 5. Send minimum balance alerts
            notification_service = NotificationService(db, self.tenant_id, self.user_id)
            min_balance_alerts = notification_service.send_minimum_balance_alerts()
            results["jobs"].append({
                "job": "min_balance_alerts",
                "status": "completed",
                "result": {"sent": min_balance_alerts['accounts_notified']}
            })
            logger.info(f"Min balance alerts: {min_balance_alerts['accounts_notified']} sent")
        
        except Exception as e:
            logger.error(f"Min balance alerts failed: {str(e)}")
            results["jobs"].append({
                "job": "min_balance_alerts",
                "status": "failed",
                "error": str(e)
            })
        
        logger.info(f"Monthly jobs completed for tenant {self.tenant_id}")
        return results
    
    def run_quarterly_jobs(self, db: Session, financial_year: str, quarter: int) -> Dict[str, Any]:
        """
        Run quarterly scheduled jobs
        
        Should be scheduled to run at end of each quarter
        """
        logger.info(f"Starting quarterly jobs for tenant {self.tenant_id}")
        
        results = {
            "job_date": date.today().isoformat(),
            "tenant_id": self.tenant_id,
            "financial_year": financial_year,
            "quarter": quarter,
            "jobs": []
        }
        
        try:
            # 1. Calculate TDS for quarter
            batch_service = BatchProcessingService(db, self.tenant_id, self.user_id)
            tds_result = batch_service.calculate_tds_batch(
                financial_year=financial_year,
                quarter=quarter
            )
            results["jobs"].append({
                "job": "tds_calculation",
                "status": "completed",
                "result": tds_result
            })
            logger.info(f"TDS calculation: {tds_result['accounts_processed']} processed")
        
        except Exception as e:
            logger.error(f"TDS calculation failed: {str(e)}")
            results["jobs"].append({
                "job": "tds_calculation",
                "status": "failed",
                "error": str(e)
            })
        
        try:
            # 2. Post quarterly interest for FD accounts
            interest_result = batch_service.schedule_interest_posting(
                posting_date=date.today(),
                account_type='fd'
            )
            results["jobs"].append({
                "job": "quarterly_interest_posting",
                "status": "completed",
                "result": interest_result
            })
            logger.info(f"Quarterly interest: {interest_result['accounts_processed']} processed")
        
        except Exception as e:
            logger.error(f"Quarterly interest failed: {str(e)}")
            results["jobs"].append({
                "job": "quarterly_interest_posting",
                "status": "failed",
                "error": str(e)
            })
        
        logger.info(f"Quarterly jobs completed for tenant {self.tenant_id}")
        return results
    
    def run_annual_jobs(self, db: Session) -> Dict[str, Any]:
        """
        Run annual scheduled jobs
        
        Should be scheduled to run at end of financial year
        """
        logger.info(f"Starting annual jobs for tenant {self.tenant_id}")
        
        results = {
            "job_date": date.today().isoformat(),
            "tenant_id": self.tenant_id,
            "jobs": []
        }
        
        try:
            # 1. Check dormant accounts (24 months inactive)
            batch_service = BatchProcessingService(db, self.tenant_id, self.user_id)
            dormancy_result = batch_service.check_dormant_accounts(inactive_months=24)
            results["jobs"].append({
                "job": "dormancy_check",
                "status": "completed",
                "result": dormancy_result
            })
            logger.info(f"Dormancy check: {dormancy_result['marked_count']} marked dormant")
        
        except Exception as e:
            logger.error(f"Dormancy check failed: {str(e)}")
            results["jobs"].append({
                "job": "dormancy_check",
                "status": "failed",
                "error": str(e)
            })
        
        try:
            # 2. Send dormancy warnings (18 months inactive)
            notification_service = NotificationService(db, self.tenant_id, self.user_id)
            dormancy_warnings = notification_service.send_dormancy_warnings(inactive_months=18)
            results["jobs"].append({
                "job": "dormancy_warnings",
                "status": "completed",
                "result": {"sent": dormancy_warnings['accounts_notified']}
            })
            logger.info(f"Dormancy warnings: {dormancy_warnings['accounts_notified']} sent")
        
        except Exception as e:
            logger.error(f"Dormancy warnings failed: {str(e)}")
            results["jobs"].append({
                "job": "dormancy_warnings",
                "status": "failed",
                "error": str(e)
            })
        
        logger.info(f"Annual jobs completed for tenant {self.tenant_id}")
        return results


# Cron job configuration examples (for documentation)
CRON_SCHEDULE = """
# Deposit Management Scheduled Jobs

# Daily jobs - Run at 6:00 AM every day
0 6 * * * python -m backend.services.deposit.run_daily_jobs

# Monthly jobs - Run at 2:00 AM on 1st of every month
0 2 1 * * python -m backend.services.deposit.run_monthly_jobs

# Quarterly jobs - Run at end of each quarter
# Q1: March 31 at 11:00 PM
0 23 31 3 * python -m backend.services.deposit.run_quarterly_jobs --fy 2024-2025 --quarter 4

# Q2: June 30 at 11:00 PM
0 23 30 6 * python -m backend.services.deposit.run_quarterly_jobs --fy 2025-2026 --quarter 1

# Q3: September 30 at 11:00 PM
0 23 30 9 * python -m backend.services.deposit.run_quarterly_jobs --fy 2025-2026 --quarter 2

# Q4: December 31 at 11:00 PM
0 23 31 12 * python -m backend.services.deposit.run_quarterly_jobs --fy 2025-2026 --quarter 3

# Annual jobs - Run at end of financial year (March 31)
0 23 31 3 * python -m backend.services.deposit.run_annual_jobs
"""


# CLI runner for scheduled jobs
def run_daily_jobs_cli():
    """CLI entry point for daily jobs"""
    from backend.shared.database.connection import SessionLocal
    
    db = SessionLocal()
    try:
        # Get all tenants (in multi-tenant setup)
        # For now, using tenant_id = 1
        jobs = DepositScheduledJobs(tenant_id=1)
        result = jobs.run_daily_jobs(db)
        print(f"Daily jobs completed: {result}")
    finally:
        db.close()


def run_monthly_jobs_cli():
    """CLI entry point for monthly jobs"""
    from backend.shared.database.connection import SessionLocal
    
    db = SessionLocal()
    try:
        jobs = DepositScheduledJobs(tenant_id=1)
        result = jobs.run_monthly_jobs(db)
        print(f"Monthly jobs completed: {result}")
    finally:
        db.close()


def run_quarterly_jobs_cli(financial_year: str, quarter: int):
    """CLI entry point for quarterly jobs"""
    from backend.shared.database.connection import SessionLocal
    
    db = SessionLocal()
    try:
        jobs = DepositScheduledJobs(tenant_id=1)
        result = jobs.run_quarterly_jobs(db, financial_year, quarter)
        print(f"Quarterly jobs completed: {result}")
    finally:
        db.close()


def run_annual_jobs_cli():
    """CLI entry point for annual jobs"""
    from backend.shared.database.connection import SessionLocal
    
    db = SessionLocal()
    try:
        jobs = DepositScheduledJobs(tenant_id=1)
        result = jobs.run_annual_jobs(db)
        print(f"Annual jobs completed: {result}")
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python scheduled_jobs.py [daily|monthly|quarterly|annual]")
        sys.exit(1)
    
    job_type = sys.argv[1]
    
    if job_type == "daily":
        run_daily_jobs_cli()
    elif job_type == "monthly":
        run_monthly_jobs_cli()
    elif job_type == "quarterly":
        if len(sys.argv) < 4:
            print("Usage: python scheduled_jobs.py quarterly <FY> <quarter>")
            sys.exit(1)
        run_quarterly_jobs_cli(sys.argv[2], int(sys.argv[3]))
    elif job_type == "annual":
        run_annual_jobs_cli()
    else:
        print(f"Unknown job type: {job_type}")
        sys.exit(1)
