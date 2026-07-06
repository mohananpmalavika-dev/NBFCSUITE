"""
Bureau Manager Service
Unified interface for all credit bureau integrations

Provides:
- Single point of access for all bureaus
- Fallback mechanism (try CIBIL, then Equifax, etc.)
- Multi-bureau pull support
- Result aggregation
- Consent management
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, date
import logging

from .cibil_service import CIBILService
from .base_bureau_service import BureauServiceError
from backend.shared.database.integration_models import BureauReport, BureauConsent

logger = logging.getLogger(__name__)


class BureauManager:
    """
    Manager class for handling multiple credit bureau integrations
    
    Provides unified interface and fallback mechanism
    """
    
    def __init__(self, db: Session, tenant_id: int, config: Dict[str, Any]):
        """
        Initialize Bureau Manager
        
        Args:
            db: Database session
            tenant_id: Tenant identifier
            config: Configuration for all bureaus
        """
        self.db = db
        self.tenant_id = tenant_id
        self.config = config
        
        # Initialize bureau services
        self.bureaus = {}
        self._initialize_bureaus()
    
    def _initialize_bureaus(self) -> None:
        """Initialize all configured bureau services"""
        # CIBIL
        if 'cibil' in self.config and self.config['cibil'].get('enabled', False):
            try:
                self.bureaus['CIBIL'] = CIBILService(
                    self.db,
                    self.tenant_id,
                    self.config['cibil']
                )
                logger.info("Bureau Manager: CIBIL service initialized")
            except Exception as e:
                logger.error(f"Bureau Manager: Failed to initialize CIBIL - {str(e)}")
        
        # Equifax (placeholder - similar implementation)
        if 'equifax' in self.config and self.config['equifax'].get('enabled', False):
            logger.info("Bureau Manager: Equifax service - to be implemented")
        
        # Experian (placeholder - similar implementation)
        if 'experian' in self.config and self.config['experian'].get('enabled', False):
            logger.info("Bureau Manager: Experian service - to be implemented")
        
        # CRIF High Mark (placeholder - similar implementation)
        if 'crif' in self.config and self.config['crif'].get('enabled', False):
            logger.info("Bureau Manager: CRIF service - to be implemented")
        
        logger.info(f"Bureau Manager: Initialized {len(self.bureaus)} bureau(s)")
    
    def pull_credit_report(
        self,
        customer_id: int,
        customer_data: Dict[str, Any],
        bureau_name: Optional[str] = None,
        fallback: bool = True
    ) -> Dict[str, Any]:
        """
        Pull credit report from bureau
        
        Args:
            customer_id: Customer ID
            customer_data: Customer information
            bureau_name: Specific bureau to use (None = use preferred)
            fallback: Enable fallback to other bureaus on failure
            
        Returns:
            Credit report data with bureau information
        """
        # Check for valid consent
        consent = self._check_consent(customer_id)
        if not consent:
            raise BureauServiceError("No valid consent found for bureau pull")
        
        # Determine bureau order
        bureau_order = self._get_bureau_order(bureau_name)
        
        last_error = None
        for bureau in bureau_order:
            if bureau not in self.bureaus:
                continue
            
            try:
                logger.info(f"Bureau Manager: Attempting {bureau} for customer {customer_id}")
                
                # Pull report from bureau
                report_data = self.bureaus[bureau].pull_consumer_report(
                    customer_data,
                    consent.id
                )
                
                # Save report to database
                saved_report = self._save_report(
                    customer_id=customer_id,
                    bureau_name=bureau,
                    report_data=report_data,
                    consent_id=consent.id
                )
                
                logger.info(f"Bureau Manager: Successfully pulled {bureau} report for customer {customer_id}")
                
                return {
                    'success': True,
                    'bureau_name': bureau,
                    'report_id': saved_report.id,
                    'score': report_data.get('score'),
                    'report_date': report_data.get('report_date'),
                    'summary': report_data.get('summary'),
                    'report_data': report_data
                }
                
            except Exception as e:
                last_error = e
                logger.warning(f"Bureau Manager: {bureau} failed - {str(e)}")
                
                if not fallback:
                    raise
        
        # All bureaus failed
        error_msg = f"All bureaus failed. Last error: {str(last_error)}"
        logger.error(f"Bureau Manager: {error_msg}")
        raise BureauServiceError(error_msg)
    
    def pull_multi_bureau(
        self,
        customer_id: int,
        customer_data: Dict[str, Any],
        bureau_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Pull reports from multiple bureaus
        
        Args:
            customer_id: Customer ID
            customer_data: Customer information
            bureau_names: List of bureaus to pull from (None = all available)
            
        Returns:
            Combined results from all bureaus
        """
        if bureau_names is None:
            bureau_names = list(self.bureaus.keys())
        
        results = {
            'customer_id': customer_id,
            'pull_datetime': datetime.utcnow().isoformat(),
            'reports': {},
            'success_count': 0,
            'failure_count': 0
        }
        
        for bureau_name in bureau_names:
            try:
                report = self.pull_credit_report(
                    customer_id,
                    customer_data,
                    bureau_name=bureau_name,
                    fallback=False
                )
                results['reports'][bureau_name] = report
                results['success_count'] += 1
            except Exception as e:
                results['reports'][bureau_name] = {
                    'success': False,
                    'error': str(e)
                }
                results['failure_count'] += 1
        
        # Calculate average score
        scores = [
            r.get('score') for r in results['reports'].values() 
            if r.get('success') and r.get('score')
        ]
        if scores:
            results['average_score'] = round(sum(scores) / len(scores))
        
        return results
    
    def get_latest_report(
        self,
        customer_id: int,
        bureau_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get latest bureau report from database
        
        Args:
            customer_id: Customer ID
            bureau_name: Specific bureau (None = any bureau)
            
        Returns:
            Latest report data or None
        """
        query = self.db.query(BureauReport).filter(
            BureauReport.customer_id == customer_id,
            BureauReport.tenant_id == self.tenant_id
        )
        
        if bureau_name:
            query = query.filter(BureauReport.bureau_name == bureau_name)
        
        latest_report = query.order_by(BureauReport.report_date.desc()).first()
        
        if latest_report:
            return {
                'id': latest_report.id,
                'bureau_name': latest_report.bureau_name,
                'score': latest_report.score,
                'report_date': latest_report.report_date.isoformat(),
                'report_data': latest_report.report_json
            }
        
        return None
    
    def get_report_history(
        self,
        customer_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get bureau report history for customer
        
        Args:
            customer_id: Customer ID
            limit: Maximum number of reports to return
            
        Returns:
            List of historical reports
        """
        reports = self.db.query(BureauReport).filter(
            BureauReport.customer_id == customer_id,
            BureauReport.tenant_id == self.tenant_id
        ).order_by(BureauReport.report_date.desc()).limit(limit).all()
        
        return [
            {
                'id': r.id,
                'bureau_name': r.bureau_name,
                'score': r.score,
                'report_date': r.report_date.isoformat(),
                'pulled_by': r.pulled_by
            }
            for r in reports
        ]
    
    def create_consent(
        self,
        customer_id: int,
        consent_type: str = 'credit_report',
        valid_days: int = 90
    ) -> BureauConsent:
        """
        Create bureau consent record
        
        Args:
            customer_id: Customer ID
            consent_type: Type of consent
            valid_days: Validity period in days
            
        Returns:
            Created consent record
        """
        from datetime import timedelta
        
        consent = BureauConsent(
            tenant_id=self.tenant_id,
            customer_id=customer_id,
            consent_type=consent_type,
            consent_given=True,
            consent_date=date.today(),
            valid_until=date.today() + timedelta(days=valid_days),
            created_at=datetime.utcnow()
        )
        
        self.db.add(consent)
        self.db.commit()
        self.db.refresh(consent)
        
        logger.info(f"Bureau Manager: Created consent for customer {customer_id}")
        return consent
    
    def _check_consent(self, customer_id: int) -> Optional[BureauConsent]:
        """
        Check if valid consent exists
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Valid consent record or None
        """
        consent = self.db.query(BureauConsent).filter(
            BureauConsent.customer_id == customer_id,
            BureauConsent.tenant_id == self.tenant_id,
            BureauConsent.consent_given == True,
            BureauConsent.valid_until >= date.today()
        ).order_by(BureauConsent.consent_date.desc()).first()
        
        return consent
    
    def _get_bureau_order(self, preferred_bureau: Optional[str] = None) -> List[str]:
        """
        Get bureau order for fallback mechanism
        
        Args:
            preferred_bureau: Preferred bureau to try first
            
        Returns:
            List of bureau names in priority order
        """
        if preferred_bureau and preferred_bureau in self.bureaus:
            order = [preferred_bureau]
            order.extend([b for b in self.bureaus.keys() if b != preferred_bureau])
            return order
        
        # Default order: CIBIL, Equifax, Experian, CRIF
        default_order = ['CIBIL', 'Equifax', 'Experian', 'CRIF']
        return [b for b in default_order if b in self.bureaus]
    
    def _save_report(
        self,
        customer_id: int,
        bureau_name: str,
        report_data: Dict[str, Any],
        consent_id: int
    ) -> BureauReport:
        """
        Save bureau report to database
        
        Args:
            customer_id: Customer ID
            bureau_name: Bureau name
            report_data: Report data
            consent_id: Consent ID
            
        Returns:
            Saved report record
        """
        report = BureauReport(
            tenant_id=self.tenant_id,
            customer_id=customer_id,
            bureau_name=bureau_name,
            report_type='consumer',
            score=report_data.get('score'),
            report_date=datetime.utcnow().date(),
            report_json=report_data,
            consent_id=consent_id,
            pulled_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        return report
