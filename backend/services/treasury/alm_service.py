"""
ALM (Asset Liability Management) Service
Business logic for maturity ladder, gap analysis, liquidity ratios, interest rate risk
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException

from backend.shared.database.alm_models import (
    MaturityLadder, GapAnalysis, LiquidityRatio, InterestRateRisk,
    QuarterlyReturn, ALMLimits, ALMAlert,
    MaturityBucket, GapType, RiskLevel, InterestRateScenario
)
from . import alm_schemas as schemas


class MaturityLadderService:
    """Service for Maturity Ladder Management"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    def create_maturity_ladder(self, data: schemas.MaturityLadderCreate) -> MaturityLadder:
        """Create new maturity ladder entry"""
        # Check if entry already exists
        existing = self.db.query(MaturityLadder).filter(
            and_(
                MaturityLadder.tenant_id == self.tenant_id,
                MaturityLadder.report_date == data.report_date,
                MaturityLadder.bucket == data.bucket
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Maturity ladder entry already exists for {data.report_date} - {data.bucket}"
            )
        
        # Calculate totals
        total_assets = (
            data.cash_and_bank_balance + data.investments +
            data.loans_and_advances + data.fixed_assets + data.other_assets
        )

        
        total_liabilities = (
            data.deposits + data.borrowings +
            data.debt_securities + data.other_liabilities
        )
        
        gap_amount = total_assets - total_liabilities
        
        # Calculate cumulative gap
        cumulative_gap = self._calculate_cumulative_gap(data.report_date, data.bucket, gap_amount)
        
        # Calculate gap percentage
        gap_percentage = None
        if total_assets > 0:
            gap_percentage = (gap_amount / total_assets) * 100
        
        # Calculate interest rate gap
        interest_rate_gap = data.interest_sensitive_assets - data.interest_sensitive_liabilities
        
        # Calculate duration gap
        duration_gap = None
        if data.avg_asset_duration and data.avg_liability_duration:
            duration_gap = data.avg_asset_duration - data.avg_liability_duration
        
        # Create entry
        entry = MaturityLadder(
            tenant_id=self.tenant_id,
            report_date=data.report_date,
            bucket=data.bucket,
            cash_and_bank_balance=data.cash_and_bank_balance,
            investments=data.investments,
            loans_and_advances=data.loans_and_advances,
            fixed_assets=data.fixed_assets,
            other_assets=data.other_assets,
            total_assets=total_assets,
            deposits=data.deposits,
            borrowings=data.borrowings,
            debt_securities=data.debt_securities,
            other_liabilities=data.other_liabilities,
            total_liabilities=total_liabilities,
            gap_amount=gap_amount,
            cumulative_gap=cumulative_gap,
            gap_percentage=gap_percentage,
            interest_sensitive_assets=data.interest_sensitive_assets,
            interest_sensitive_liabilities=data.interest_sensitive_liabilities,
            interest_rate_gap=interest_rate_gap,
            avg_asset_duration=data.avg_asset_duration,
            avg_liability_duration=data.avg_liability_duration,
            duration_gap=duration_gap,
            notes=data.notes,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        
        # Check for limit breaches
        self._check_maturity_ladder_limits(entry)
        
        return entry
    
    def _calculate_cumulative_gap(self, report_date: date, current_bucket: MaturityBucket, gap_amount: Decimal) -> Decimal:
        """Calculate cumulative gap up to current bucket"""
        bucket_order = [
            MaturityBucket.UPTO_1_DAY,
            MaturityBucket.UPTO_7_DAYS,
            MaturityBucket.UPTO_14_DAYS,
            MaturityBucket.UPTO_1_MONTH,
            MaturityBucket.UPTO_2_MONTHS,
            MaturityBucket.UPTO_3_MONTHS,
            MaturityBucket.UPTO_6_MONTHS,
            MaturityBucket.UPTO_1_YEAR,
            MaturityBucket.UPTO_2_YEARS,
            MaturityBucket.UPTO_3_YEARS,
            MaturityBucket.UPTO_5_YEARS,
            MaturityBucket.ABOVE_5_YEARS
        ]
        
        current_index = bucket_order.index(current_bucket)
        previous_buckets = bucket_order[:current_index]
        
        previous_gap = self.db.query(func.sum(MaturityLadder.gap_amount)).filter(
            and_(
                MaturityLadder.tenant_id == self.tenant_id,
                MaturityLadder.report_date == report_date,
                MaturityLadder.bucket.in_(previous_buckets)
            )
        ).scalar() or Decimal("0.00")
        
        return previous_gap + gap_amount

    
    def _check_maturity_ladder_limits(self, entry: MaturityLadder):
        """Check if maturity ladder breaches any limits"""
        limits = self.db.query(ALMLimits).filter(
            and_(
                ALMLimits.tenant_id == self.tenant_id,
                ALMLimits.is_active == True,
                ALMLimits.limit_type == "maturity_gap",
                or_(
                    ALMLimits.maturity_bucket == entry.bucket,
                    ALMLimits.maturity_bucket.is_(None)
                ),
                ALMLimits.effective_from <= entry.report_date,
                or_(
                    ALMLimits.effective_to.is_(None),
                    ALMLimits.effective_to >= entry.report_date
                )
            )
        ).all()
        
        for limit in limits:
            breach = False
            deviation = None
            
            if limit.maximum_value and entry.gap_percentage:
                if entry.gap_percentage > limit.maximum_value:
                    breach = True
                    deviation = entry.gap_percentage - limit.maximum_value
            
            if limit.minimum_value and entry.gap_percentage:
                if entry.gap_percentage < limit.minimum_value:
                    breach = True
                    deviation = limit.minimum_value - entry.gap_percentage
            
            if breach:
                self._create_alert(
                    alert_date=entry.report_date,
                    alert_type="maturity_gap_breach",
                    severity=RiskLevel.HIGH if abs(deviation) > 10 else RiskLevel.MEDIUM,
                    metric_name=f"Maturity Gap - {entry.bucket}",
                    metric_value=entry.gap_percentage,
                    limit_value=limit.maximum_value or limit.minimum_value,
                    deviation=deviation,
                    alert_message=f"Maturity gap for {entry.bucket} breached limit",
                    maturity_ladder_id=entry.id
                )

    
    def get_maturity_ladder(self, report_date: date) -> List[MaturityLadder]:
        """Get maturity ladder for a specific date"""
        entries = self.db.query(MaturityLadder).filter(
            and_(
                MaturityLadder.tenant_id == self.tenant_id,
                MaturityLadder.report_date == report_date
            )
        ).order_by(MaturityLadder.bucket).all()
        
        return entries
    
    def get_maturity_ladder_summary(self, report_date: date) -> schemas.MaturityLadderSummary:
        """Get maturity ladder summary"""
        entries = self.get_maturity_ladder(report_date)
        
        if not entries:
            raise HTTPException(status_code=404, detail="No maturity ladder data found")
        
        total_assets = sum(e.total_assets for e in entries)
        total_liabilities = sum(e.total_liabilities for e in entries)
        overall_gap = total_assets - total_liabilities
        
        # Calculate gaps by term
        short_term_buckets = [
            MaturityBucket.UPTO_1_DAY, MaturityBucket.UPTO_7_DAYS,
            MaturityBucket.UPTO_14_DAYS, MaturityBucket.UPTO_1_MONTH,
            MaturityBucket.UPTO_2_MONTHS, MaturityBucket.UPTO_3_MONTHS,
            MaturityBucket.UPTO_6_MONTHS, MaturityBucket.UPTO_1_YEAR
        ]
        medium_term_buckets = [MaturityBucket.UPTO_2_YEARS, MaturityBucket.UPTO_3_YEARS]
        
        short_term_gap = sum(e.gap_amount for e in entries if e.bucket in short_term_buckets)
        medium_term_gap = sum(e.gap_amount for e in entries if e.bucket in medium_term_buckets)
        long_term_gap = sum(e.gap_amount for e in entries if e.bucket not in short_term_buckets + medium_term_buckets)
        
        # Find largest gap
        largest_gap_entry = max(entries, key=lambda e: abs(e.gap_amount))
        
        # Assess risk level
        risk_level = self._assess_maturity_risk(entries)
        
        return schemas.MaturityLadderSummary(
            report_date=report_date,
            total_assets=total_assets,
            total_liabilities=total_liabilities,
            overall_gap=overall_gap,
            short_term_gap=short_term_gap,
            medium_term_gap=medium_term_gap,
            long_term_gap=long_term_gap,
            risk_level=risk_level,
            largest_gap_bucket=largest_gap_entry.bucket,
            largest_gap_amount=largest_gap_entry.gap_amount
        )

    
    def _assess_maturity_risk(self, entries: List[MaturityLadder]) -> RiskLevel:
        """Assess overall maturity risk level"""
        max_gap_pct = max((abs(e.gap_percentage) for e in entries if e.gap_percentage), default=0)
        
        if max_gap_pct > 30:
            return RiskLevel.CRITICAL
        elif max_gap_pct > 20:
            return RiskLevel.HIGH
        elif max_gap_pct > 10:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def update_maturity_ladder(self, entry_id: int, data: schemas.MaturityLadderUpdate) -> MaturityLadder:
        """Update maturity ladder entry"""
        entry = self.db.query(MaturityLadder).filter(
            and_(
                MaturityLadder.id == entry_id,
                MaturityLadder.tenant_id == self.tenant_id
            )
        ).first()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Maturity ladder entry not found")
        
        # Update fields
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(entry, field, value)
        
        # Recalculate totals
        entry.total_assets = (
            entry.cash_and_bank_balance + entry.investments +
            entry.loans_and_advances + entry.fixed_assets + entry.other_assets
        )
        entry.total_liabilities = (
            entry.deposits + entry.borrowings +
            entry.debt_securities + entry.other_liabilities
        )
        entry.gap_amount = entry.total_assets - entry.total_liabilities
        entry.cumulative_gap = self._calculate_cumulative_gap(
            entry.report_date, entry.bucket, entry.gap_amount
        )
        
        if entry.total_assets > 0:
            entry.gap_percentage = (entry.gap_amount / entry.total_assets) * 100
        
        entry.interest_rate_gap = entry.interest_sensitive_assets - entry.interest_sensitive_liabilities
        
        if entry.avg_asset_duration and entry.avg_liability_duration:
            entry.duration_gap = entry.avg_asset_duration - entry.avg_liability_duration
        
        entry.updated_by = self.user_id
        entry.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(entry)
        
        return entry


class GapAnalysisService:
    """Service for Gap Analysis"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id

    
    def create_gap_analysis(self, data: schemas.GapAnalysisCreate) -> GapAnalysis:
        """Create new gap analysis entry"""
        # Check if entry exists
        existing = self.db.query(GapAnalysis).filter(
            and_(
                GapAnalysis.tenant_id == self.tenant_id,
                GapAnalysis.report_date == data.report_date,
                GapAnalysis.analysis_type == data.analysis_type,
                GapAnalysis.bucket == data.bucket
            )
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Gap analysis entry already exists")
        
        # Calculate totals
        total_inflows = data.contractual_inflows + data.behavioral_inflows
        total_outflows = data.contractual_outflows + data.behavioral_outflows
        gap_amount = total_inflows - total_outflows
        
        # Calculate cumulative gap
        cumulative_gap = self._calculate_cumulative_gap(
            data.report_date, data.analysis_type, data.bucket, gap_amount
        )
        
        # Calculate gap ratio
        gap_ratio = None
        if total_outflows > 0:
            gap_ratio = total_inflows / total_outflows
        
        # Check limit breach
        limit_breach = False
        actual_value = gap_amount
        if data.limit_value:
            if gap_amount < data.limit_value:
                limit_breach = True
        
        # Create entry
        entry = GapAnalysis(
            tenant_id=self.tenant_id,
            report_date=data.report_date,
            analysis_type=data.analysis_type,
            bucket=data.bucket,
            total_inflows=total_inflows,
            contractual_inflows=data.contractual_inflows,
            behavioral_inflows=data.behavioral_inflows,
            total_outflows=total_outflows,
            contractual_outflows=data.contractual_outflows,
            behavioral_outflows=data.behavioral_outflows,
            gap_amount=gap_amount,
            cumulative_gap=cumulative_gap,
            gap_ratio=gap_ratio,
            risk_level=data.risk_level,
            risk_score=data.risk_score,
            mitigation_required=data.mitigation_required,
            mitigation_strategy=data.mitigation_strategy,
            limit_breach=limit_breach,
            limit_value=data.limit_value,
            actual_value=actual_value,
            notes=data.notes,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        
        # Create alert if limit breach
        if limit_breach:
            self._create_gap_alert(entry)
        
        return entry

    
    def _calculate_cumulative_gap(self, report_date: date, analysis_type: GapType, 
                                   current_bucket: MaturityBucket, gap_amount: Decimal) -> Decimal:
        """Calculate cumulative gap"""
        bucket_order = [
            MaturityBucket.UPTO_1_DAY, MaturityBucket.UPTO_7_DAYS, MaturityBucket.UPTO_14_DAYS,
            MaturityBucket.UPTO_1_MONTH, MaturityBucket.UPTO_2_MONTHS, MaturityBucket.UPTO_3_MONTHS,
            MaturityBucket.UPTO_6_MONTHS, MaturityBucket.UPTO_1_YEAR, MaturityBucket.UPTO_2_YEARS,
            MaturityBucket.UPTO_3_YEARS, MaturityBucket.UPTO_5_YEARS, MaturityBucket.ABOVE_5_YEARS
        ]
        
        current_index = bucket_order.index(current_bucket)
        previous_buckets = bucket_order[:current_index]
        
        previous_gap = self.db.query(func.sum(GapAnalysis.gap_amount)).filter(
            and_(
                GapAnalysis.tenant_id == self.tenant_id,
                GapAnalysis.report_date == report_date,
                GapAnalysis.analysis_type == analysis_type,
                GapAnalysis.bucket.in_(previous_buckets)
            )
        ).scalar() or Decimal("0.00")
        
        return previous_gap + gap_amount
    
    def _create_gap_alert(self, entry: GapAnalysis):
        """Create alert for gap limit breach"""
        alert = ALMAlert(
            tenant_id=self.tenant_id,
            alert_date=entry.report_date,
            alert_type="gap_limit_breach",
            severity=entry.risk_level or RiskLevel.HIGH,
            metric_name=f"{entry.analysis_type} - {entry.bucket}",
            metric_value=entry.gap_amount,
            limit_value=entry.limit_value,
            deviation=entry.limit_value - entry.gap_amount if entry.limit_value else None,
            alert_message=f"Gap analysis breach for {entry.analysis_type} in {entry.bucket}",
            recommendation=entry.mitigation_strategy,
            gap_analysis_id=entry.id
        )
        self.db.add(alert)
        self.db.commit()
    
    def get_gap_analysis(self, report_date: date, analysis_type: GapType) -> List[GapAnalysis]:
        """Get gap analysis for specific date and type"""
        return self.db.query(GapAnalysis).filter(
            and_(
                GapAnalysis.tenant_id == self.tenant_id,
                GapAnalysis.report_date == report_date,
                GapAnalysis.analysis_type == analysis_type
            )
        ).order_by(GapAnalysis.bucket).all()
    
    def get_gap_analysis_summary(self, report_date: date, analysis_type: GapType) -> schemas.GapAnalysisSummary:
        """Get gap analysis summary"""
        entries = self.get_gap_analysis(report_date, analysis_type)
        
        if not entries:
            raise HTTPException(status_code=404, detail="No gap analysis data found")
        
        total_gap = sum(e.gap_amount for e in entries)
        limit_breaches = sum(1 for e in entries if e.limit_breach)
        mitigation_required = any(e.mitigation_required for e in entries)
        
        # Find critical buckets (negative gaps or breaches)
        critical_buckets = [str(e.bucket) for e in entries if e.gap_amount < 0 or e.limit_breach]
        
        # Assess overall risk
        risk_scores = [e.risk_score for e in entries if e.risk_score]
        overall_risk = RiskLevel.LOW
        if risk_scores:
            avg_score = sum(risk_scores) / len(risk_scores)
            if avg_score > 75:
                overall_risk = RiskLevel.CRITICAL
            elif avg_score > 50:
                overall_risk = RiskLevel.HIGH
            elif avg_score > 25:
                overall_risk = RiskLevel.MEDIUM
        
        return schemas.GapAnalysisSummary(
            report_date=report_date,
            analysis_type=analysis_type,
            total_gap=total_gap,
            critical_buckets=critical_buckets,
            limit_breaches=limit_breaches,
            mitigation_required=mitigation_required,
            overall_risk_level=overall_risk
        )


class LiquidityRatioService:
    """Service for Liquidity Ratio Management"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id

    
    def create_liquidity_ratio(self, data: schemas.LiquidityRatioCreate) -> LiquidityRatio:
        """Create liquidity ratio entry"""
        # Check if entry exists
        existing = self.db.query(LiquidityRatio).filter(
            and_(
                LiquidityRatio.tenant_id == self.tenant_id,
                LiquidityRatio.report_date == data.report_date
            )
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Liquidity ratio entry already exists for this date")
        
        # Check SLR compliance
        slr_compliance = True
        if data.slr_ratio and data.slr_requirement:
            slr_compliance = data.slr_ratio >= data.slr_requirement
        
        # Check all ratios compliance
        breached_ratios = {}
        all_ratios_compliant = True
        
        # Get limits
        limits = self._get_liquidity_limits(data.report_date)
        
        for limit_name, limit_value in limits.items():
            ratio_value = getattr(data, limit_name, None)
            if ratio_value is not None and limit_value is not None:
                if ratio_value < limit_value:
                    breached_ratios[limit_name] = {
                        "actual": float(ratio_value),
                        "required": float(limit_value),
                        "deviation": float(limit_value - ratio_value)
                    }
                    all_ratios_compliant = False
        
        # Create entry
        entry = LiquidityRatio(
            tenant_id=self.tenant_id,
            report_date=data.report_date,
            current_ratio=data.current_ratio,
            quick_ratio=data.quick_ratio,
            cash_ratio=data.cash_ratio,
            liquidity_coverage_ratio=data.liquidity_coverage_ratio,
            net_stable_funding_ratio=data.net_stable_funding_ratio,
            liquid_assets_to_total_assets=data.liquid_assets_to_total_assets,
            liquid_assets_to_deposits=data.liquid_assets_to_deposits,
            liquid_assets_to_short_term_liabilities=data.liquid_assets_to_short_term_liabilities,
            slr_ratio=data.slr_ratio,
            slr_requirement=data.slr_requirement,
            slr_compliance=slr_compliance,
            loan_to_deposit_ratio=data.loan_to_deposit_ratio,
            deposit_concentration_ratio=data.deposit_concentration_ratio,
            large_deposits_ratio=data.large_deposits_ratio,
            stable_funding_ratio=data.stable_funding_ratio,
            core_deposit_ratio=data.core_deposit_ratio,
            volatile_liability_ratio=data.volatile_liability_ratio,
            liquidity_stress_index=data.liquidity_stress_index,
            funding_gap_ratio=data.funding_gap_ratio,
            high_quality_liquid_assets=data.high_quality_liquid_assets,
            total_net_cash_outflows=data.total_net_cash_outflows,
            available_stable_funding=data.available_stable_funding,
            required_stable_funding=data.required_stable_funding,
            all_ratios_compliant=all_ratios_compliant,
            breached_ratios=breached_ratios if breached_ratios else None,
            notes=data.notes,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        
        # Create alerts for breaches
        if not all_ratios_compliant:
            self._create_liquidity_alerts(entry, breached_ratios)
        
        return entry

    
    def _get_liquidity_limits(self, report_date: date) -> Dict[str, Decimal]:
        """Get applicable liquidity ratio limits"""
        limits = {}
        limit_entries = self.db.query(ALMLimits).filter(
            and_(
                ALMLimits.tenant_id == self.tenant_id,
                ALMLimits.is_active == True,
                ALMLimits.limit_type == "liquidity_ratio",
                ALMLimits.effective_from <= report_date,
                or_(
                    ALMLimits.effective_to.is_(None),
                    ALMLimits.effective_to >= report_date
                )
            )
        ).all()
        
        for limit in limit_entries:
            limits[limit.limit_name] = limit.minimum_value
        
        return limits
    
    def _create_liquidity_alerts(self, entry: LiquidityRatio, breached_ratios: Dict):
        """Create alerts for liquidity ratio breaches"""
        for ratio_name, breach_info in breached_ratios.items():
            severity = RiskLevel.CRITICAL if breach_info['deviation'] > 20 else RiskLevel.HIGH
            
            alert = ALMAlert(
                tenant_id=self.tenant_id,
                alert_date=entry.report_date,
                alert_type="liquidity_ratio_breach",
                severity=severity,
                metric_name=ratio_name.replace('_', ' ').title(),
                metric_value=Decimal(str(breach_info['actual'])),
                limit_value=Decimal(str(breach_info['required'])),
                deviation=Decimal(str(breach_info['deviation'])),
                deviation_percentage=Decimal(str(breach_info['deviation'] / breach_info['required'] * 100)),
                alert_message=f"Liquidity ratio {ratio_name} breached minimum requirement",
                recommendation="Increase liquid assets or reduce short-term liabilities",
                liquidity_ratio_id=entry.id
            )
            self.db.add(alert)
        
        self.db.commit()
    
    def get_liquidity_ratio(self, report_date: date) -> LiquidityRatio:
        """Get liquidity ratio for specific date"""
        entry = self.db.query(LiquidityRatio).filter(
            and_(
                LiquidityRatio.tenant_id == self.tenant_id,
                LiquidityRatio.report_date == report_date
            )
        ).first()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Liquidity ratio not found")
        
        return entry
    
    def get_liquidity_trends(self, start_date: date, end_date: date, 
                            metric_name: str) -> schemas.LiquidityRatioTrend:
        """Get liquidity ratio trends over time"""
        entries = self.db.query(LiquidityRatio).filter(
            and_(
                LiquidityRatio.tenant_id == self.tenant_id,
                LiquidityRatio.report_date >= start_date,
                LiquidityRatio.report_date <= end_date
            )
        ).order_by(LiquidityRatio.report_date).all()
        
        if not entries:
            raise HTTPException(status_code=404, detail="No data found for trend analysis")
        
        values = []
        for entry in entries:
            value = getattr(entry, metric_name, None)
            if value is not None:
                values.append({
                    "date": entry.report_date,
                    "value": float(value)
                })
        
        if not values:
            raise HTTPException(status_code=404, detail=f"No data found for metric {metric_name}")
        
        # Calculate average
        average = sum(v["value"] for v in values) / len(values)
        
        # Determine trend
        if len(values) >= 2:
            first_half_avg = sum(v["value"] for v in values[:len(values)//2]) / (len(values)//2)
            second_half_avg = sum(v["value"] for v in values[len(values)//2:]) / (len(values) - len(values)//2)
            
            if second_half_avg > first_half_avg * 1.05:
                trend = "improving"
            elif second_half_avg < first_half_avg * 0.95:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return schemas.LiquidityRatioTrend(
            metric_name=metric_name,
            values=values,
            average=Decimal(str(average)),
            trend=trend
        )


class InterestRateRiskService:
    """Service for Interest Rate Risk Management"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id

    
    def create_interest_rate_risk(self, data: schemas.InterestRateRiskCreate) -> InterestRateRisk:
        """Create interest rate risk analysis"""
        # Check if entry exists
        existing = self.db.query(InterestRateRisk).filter(
            and_(
                InterestRateRisk.tenant_id == self.tenant_id,
                InterestRateRisk.report_date == data.report_date,
                InterestRateRisk.scenario == data.scenario
            )
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Interest rate risk entry already exists")
        
        # Calculate rate sensitive gap
        rate_sensitive_gap = None
        if data.rate_sensitive_assets and data.rate_sensitive_liabilities:
            rate_sensitive_gap = data.rate_sensitive_assets - data.rate_sensitive_liabilities
        
        # Calculate cumulative repricing gap
        cumulative_repricing_gap = None
        if data.repricing_gap_1_year:
            cumulative_repricing_gap = data.repricing_gap_1_year
        
        # Check limit breach
        limit_breach = False
        if data.net_interest_income_change_pct:
            if abs(data.net_interest_income_change_pct) > 15:  # 15% threshold
                limit_breach = True
        
        # Create entry
        entry = InterestRateRisk(
            tenant_id=self.tenant_id,
            report_date=data.report_date,
            scenario=data.scenario,
            net_interest_income_base=data.net_interest_income_base,
            market_value_equity_base=data.market_value_equity_base,
            interest_rate_change_bps=data.interest_rate_change_bps,
            net_interest_income_change=data.net_interest_income_change,
            net_interest_income_change_pct=data.net_interest_income_change_pct,
            market_value_equity_change=data.market_value_equity_change,
            market_value_equity_change_pct=data.market_value_equity_change_pct,
            modified_duration_assets=data.modified_duration_assets,
            modified_duration_liabilities=data.modified_duration_liabilities,
            duration_gap=data.duration_gap,
            repricing_gap_1_month=data.repricing_gap_1_month,
            repricing_gap_3_months=data.repricing_gap_3_months,
            repricing_gap_6_months=data.repricing_gap_6_months,
            repricing_gap_1_year=data.repricing_gap_1_year,
            cumulative_repricing_gap=cumulative_repricing_gap,
            rate_sensitive_assets=data.rate_sensitive_assets,
            rate_sensitive_liabilities=data.rate_sensitive_liabilities,
            rate_sensitive_gap=rate_sensitive_gap,
            earnings_at_risk=data.earnings_at_risk,
            value_at_risk=data.value_at_risk,
            risk_level=data.risk_level,
            risk_score=data.risk_score,
            limit_breach=limit_breach,
            hedging_required=data.hedging_required,
            hedging_strategy=data.hedging_strategy,
            hedge_effectiveness=data.hedge_effectiveness,
            notes=data.notes,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        
        # Create alert if needed
        if limit_breach or data.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            self._create_irr_alert(entry)
        
        return entry

    
    def _create_irr_alert(self, entry: InterestRateRisk):
        """Create alert for interest rate risk"""
        alert = ALMAlert(
            tenant_id=self.tenant_id,
            alert_date=entry.report_date,
            alert_type="interest_rate_risk",
            severity=entry.risk_level or RiskLevel.HIGH,
            metric_name=f"Interest Rate Risk - {entry.scenario}",
            metric_value=entry.net_interest_income_change_pct or Decimal("0"),
            alert_message=f"High interest rate risk detected in scenario {entry.scenario}",
            recommendation=entry.hedging_strategy or "Consider interest rate hedging strategies",
            interest_rate_risk_id=entry.id
        )
        self.db.add(alert)
        self.db.commit()
    
    def get_interest_rate_risk(self, report_date: date) -> List[InterestRateRisk]:
        """Get all interest rate risk scenarios for a date"""
        return self.db.query(InterestRateRisk).filter(
            and_(
                InterestRateRisk.tenant_id == self.tenant_id,
                InterestRateRisk.report_date == report_date
            )
        ).order_by(InterestRateRisk.scenario).all()
    
    def get_irr_summary(self, report_date: date) -> schemas.InterestRateRiskSummary:
        """Get interest rate risk summary"""
        entries = self.get_interest_rate_risk(report_date)
        
        if not entries:
            raise HTTPException(status_code=404, detail="No interest rate risk data found")
        
        # Find base and worst case scenarios
        base_scenario = next((e for e in entries if e.scenario == InterestRateScenario.BASE), None)
        
        # Find worst case (highest absolute impact)
        worst_case = max(entries, key=lambda e: abs(e.net_interest_income_change_pct or 0))
        
        # Overall risk assessment
        max_risk = max((e.risk_level for e in entries if e.risk_level), 
                       default=RiskLevel.LOW, key=lambda r: list(RiskLevel).index(r))
        
        hedging_recommended = any(e.hedging_required for e in entries)
        
        if not base_scenario:
            raise HTTPException(status_code=404, detail="Base scenario not found")
        
        return schemas.InterestRateRiskSummary(
            report_date=report_date,
            base_scenario=schemas.InterestRateRiskResponse.from_orm(base_scenario),
            worst_case_scenario=schemas.InterestRateRiskResponse.from_orm(worst_case),
            overall_risk_level=max_risk,
            hedging_recommended=hedging_recommended
        )


class QuarterlyReturnService:
    """Service for Quarterly Returns"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id

    
    def create_quarterly_return(self, data: schemas.QuarterlyReturnCreate) -> QuarterlyReturn:
        """Create quarterly ALM return"""
        # Check if return exists
        existing = self.db.query(QuarterlyReturn).filter(
            and_(
                QuarterlyReturn.tenant_id == self.tenant_id,
                QuarterlyReturn.year == data.year,
                QuarterlyReturn.quarter == data.quarter
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"Quarterly return already exists for Q{data.quarter} {data.year}"
            )
        
        # Generate return number
        return_number = f"ALM-Q{data.quarter}-{data.year}-{self.tenant_id}"
        
        # Check compliance
        is_compliant = True
        compliance_issues = {}
        
        if data.liquidity_coverage_ratio and data.liquidity_coverage_ratio < 100:
            is_compliant = False
            compliance_issues['lcr'] = "LCR below 100%"
        
        if data.cumulative_gap_1_year_pct and abs(data.cumulative_gap_1_year_pct) > 20:
            is_compliant = False
            compliance_issues['gap'] = "Cumulative gap exceeds 20%"
        
        # Create entry
        entry = QuarterlyReturn(
            tenant_id=self.tenant_id,
            return_number=return_number,
            quarter=data.quarter,
            year=data.year,
            report_date=data.report_date,
            sls_data=data.sls_data,
            irs_data=data.irs_data,
            behavioral_data=data.behavioral_data,
            total_assets=data.total_assets,
            total_liabilities=data.total_liabilities,
            net_worth=data.net_worth,
            liquidity_coverage_ratio=data.liquidity_coverage_ratio,
            cumulative_gap_1_year=data.cumulative_gap_1_year,
            cumulative_gap_1_year_pct=data.cumulative_gap_1_year_pct,
            interest_rate_shock_impact_100bps=data.interest_rate_shock_impact_100bps,
            interest_rate_shock_impact_200bps=data.interest_rate_shock_impact_200bps,
            earnings_at_risk=data.earnings_at_risk,
            is_compliant=is_compliant,
            compliance_issues=compliance_issues if compliance_issues else None,
            attachments=data.attachments,
            notes=data.notes,
            prepared_by=self.user_id,
            prepared_at=datetime.utcnow(),
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        
        return entry
    
    def approve_quarterly_return(self, return_id: int, 
                                 approval_data: schemas.QuarterlyReturnApproval) -> QuarterlyReturn:
        """Approve quarterly return"""
        entry = self.db.query(QuarterlyReturn).filter(
            and_(
                QuarterlyReturn.id == return_id,
                QuarterlyReturn.tenant_id == self.tenant_id
            )
        ).first()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Quarterly return not found")
        
        if entry.approved_by:
            raise HTTPException(status_code=400, detail="Return already approved")
        
        entry.approved_by = self.user_id
        entry.approved_at = datetime.utcnow()
        entry.notes = approval_data.approval_notes if approval_data.approval_notes else entry.notes
        entry.updated_by = self.user_id
        entry.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(entry)
        
        return entry

    
    def file_quarterly_return(self, return_id: int, 
                             filing_data: schemas.QuarterlyReturnFiling) -> QuarterlyReturn:
        """File quarterly return with regulator"""
        entry = self.db.query(QuarterlyReturn).filter(
            and_(
                QuarterlyReturn.id == return_id,
                QuarterlyReturn.tenant_id == self.tenant_id
            )
        ).first()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Quarterly return not found")
        
        if not entry.approved_by:
            raise HTTPException(status_code=400, detail="Return must be approved before filing")
        
        if entry.filed_to_regulator:
            raise HTTPException(status_code=400, detail="Return already filed")
        
        entry.filed_to_regulator = True
        entry.filing_date = filing_data.filing_date
        entry.filing_reference = filing_data.filing_reference
        entry.updated_by = self.user_id
        entry.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(entry)
        
        return entry
    
    def get_quarterly_return(self, year: int, quarter: int) -> QuarterlyReturn:
        """Get specific quarterly return"""
        entry = self.db.query(QuarterlyReturn).filter(
            and_(
                QuarterlyReturn.tenant_id == self.tenant_id,
                QuarterlyReturn.year == year,
                QuarterlyReturn.quarter == quarter
            )
        ).first()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Quarterly return not found")
        
        return entry
    
    def list_quarterly_returns(self, skip: int = 0, limit: int = 100) -> List[QuarterlyReturn]:
        """List all quarterly returns"""
        return self.db.query(QuarterlyReturn).filter(
            QuarterlyReturn.tenant_id == self.tenant_id
        ).order_by(desc(QuarterlyReturn.year), desc(QuarterlyReturn.quarter)).offset(skip).limit(limit).all()


class ALMAlertService:
    """Service for ALM Alerts"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    def _create_alert(self, alert_date: date, alert_type: str, severity: RiskLevel,
                     metric_name: str, metric_value: Decimal, limit_value: Optional[Decimal],
                     deviation: Optional[Decimal], alert_message: str, 
                     recommendation: Optional[str] = None,
                     maturity_ladder_id: Optional[int] = None,
                     gap_analysis_id: Optional[int] = None,
                     liquidity_ratio_id: Optional[int] = None,
                     interest_rate_risk_id: Optional[int] = None):
        """Create ALM alert"""
        deviation_percentage = None
        if deviation and limit_value and limit_value != 0:
            deviation_percentage = (deviation / limit_value) * 100
        
        alert = ALMAlert(
            tenant_id=self.tenant_id,
            alert_date=alert_date,
            alert_type=alert_type,
            severity=severity,
            metric_name=metric_name,
            metric_value=metric_value,
            limit_value=limit_value,
            deviation=deviation,
            deviation_percentage=deviation_percentage,
            alert_message=alert_message,
            recommendation=recommendation,
            maturity_ladder_id=maturity_ladder_id,
            gap_analysis_id=gap_analysis_id,
            liquidity_ratio_id=liquidity_ratio_id,
            interest_rate_risk_id=interest_rate_risk_id
        )
        self.db.add(alert)
        self.db.commit()
        return alert
    
    def acknowledge_alert(self, alert_id: int, notes: Optional[str] = None) -> ALMAlert:
        """Acknowledge an alert"""
        alert = self.db.query(ALMAlert).filter(
            and_(
                ALMAlert.id == alert_id,
                ALMAlert.tenant_id == self.tenant_id
            )
        ).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        if alert.is_acknowledged:
            raise HTTPException(status_code=400, detail="Alert already acknowledged")
        
        alert.is_acknowledged = True
        alert.acknowledged_by = self.user_id
        alert.acknowledged_at = datetime.utcnow()
        alert.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def resolve_alert(self, alert_id: int, resolution_notes: str) -> ALMAlert:
        """Resolve an alert"""
        alert = self.db.query(ALMAlert).filter(
            and_(
                ALMAlert.id == alert_id,
                ALMAlert.tenant_id == self.tenant_id
            )
        ).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        if alert.is_resolved:
            raise HTTPException(status_code=400, detail="Alert already resolved")
        
        alert.is_resolved = True
        alert.resolved_by = self.user_id
        alert.resolved_at = datetime.utcnow()
        alert.resolution_notes = resolution_notes
        alert.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def list_alerts(self, is_resolved: Optional[bool] = None, 
                   severity: Optional[RiskLevel] = None,
                   skip: int = 0, limit: int = 100) -> List[ALMAlert]:
        """List ALM alerts with filters"""
        query = self.db.query(ALMAlert).filter(ALMAlert.tenant_id == self.tenant_id)
        
        if is_resolved is not None:
            query = query.filter(ALMAlert.is_resolved == is_resolved)
        
        if severity:
            query = query.filter(ALMAlert.severity == severity)
        
        return query.order_by(desc(ALMAlert.alert_date), desc(ALMAlert.created_at)).offset(skip).limit(limit).all()


class ALMDashboardService:
    """Service for ALM Dashboard"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.maturity_service = MaturityLadderService(db, tenant_id, user_id)
        self.gap_service = GapAnalysisService(db, tenant_id, user_id)
        self.liquidity_service = LiquidityRatioService(db, tenant_id, user_id)
        self.irr_service = InterestRateRiskService(db, tenant_id, user_id)
        self.alert_service = ALMAlertService(db, tenant_id, user_id)
    
    def get_dashboard(self, as_of_date: date) -> schemas.ALMDashboard:
        """Get comprehensive ALM dashboard"""
        try:
            maturity_summary = self.maturity_service.get_maturity_ladder_summary(as_of_date)
        except HTTPException:
            maturity_summary = None
        
        try:
            liquidity_gap_summary = self.gap_service.get_gap_analysis_summary(
                as_of_date, GapType.LIQUIDITY_GAP
            )
        except HTTPException:
            liquidity_gap_summary = None
        
        try:
            interest_rate_gap_summary = self.gap_service.get_gap_analysis_summary(
                as_of_date, GapType.INTEREST_RATE_GAP
            )
        except HTTPException:
            interest_rate_gap_summary = None
        
        try:
            liquidity_ratios = self.liquidity_service.get_liquidity_ratio(as_of_date)
            current_ratio = liquidity_ratios.current_ratio
            lcr = liquidity_ratios.liquidity_coverage_ratio
            nsfr = liquidity_ratios.net_stable_funding_ratio
        except HTTPException:
            current_ratio = None
            lcr = None
            nsfr = None
        
        try:
            irr_summary = self.irr_service.get_irr_summary(as_of_date)
            irr_summary_dict = {
                "base_scenario": irr_summary.base_scenario.model_dump(),
                "worst_case": irr_summary.worst_case_scenario.model_dump(),
                "overall_risk": str(irr_summary.overall_risk_level)
            }
        except HTTPException:
            irr_summary_dict = {}
        
        # Get alerts
        active_alerts = self.db.query(func.count(ALMAlert.id)).filter(
            and_(
                ALMAlert.tenant_id == self.tenant_id,
                ALMAlert.is_resolved == False
            )
        ).scalar() or 0
        
        critical_alerts = self.db.query(func.count(ALMAlert.id)).filter(
            and_(
                ALMAlert.tenant_id == self.tenant_id,
                ALMAlert.is_resolved == False,
                ALMAlert.severity == RiskLevel.CRITICAL
            )
        ).scalar() or 0
        
        # Check limits compliance
        all_limits_compliant = True
        breached_limits = []
        
        if liquidity_ratios and liquidity_ratios.breached_ratios:
            all_limits_compliant = False
            breached_limits.extend(liquidity_ratios.breached_ratios.keys())
        
        return schemas.ALMDashboard(
            as_of_date=as_of_date,
            maturity_summary=maturity_summary,
            liquidity_gap_summary=liquidity_gap_summary,
            interest_rate_gap_summary=interest_rate_gap_summary,
            current_ratio=current_ratio,
            lcr=lcr,
            nsfr=nsfr,
            interest_rate_risk_summary=irr_summary_dict,
            active_alerts=active_alerts,
            critical_alerts=critical_alerts,
            all_limits_compliant=all_limits_compliant,
            breached_limits=breached_limits
        )
