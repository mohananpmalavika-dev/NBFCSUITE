"""
Interest Engine
Handles all interest calculations: Simple, Compound, Multiple payout frequencies
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from typing import Dict, Any, List, Tuple
from enum import Enum
import math


class InterestMethod(str, Enum):
    SIMPLE = "SIMPLE"
    COMPOUND_MONTHLY = "COMPOUND_MONTHLY"
    COMPOUND_QUARTERLY = "COMPOUND_QUARTERLY"
    COMPOUND_HALF_YEARLY = "COMPOUND_HALF_YEARLY"
    COMPOUND_YEARLY = "COMPOUND_YEARLY"


class PayoutFrequency(str, Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    HALF_YEARLY = "HALF_YEARLY"
    YEARLY = "YEARLY"
    ON_MATURITY = "ON_MATURITY"
    CUMULATIVE = "CUMULATIVE"


class InterestEngine:
    """
    Advanced Interest Calculation Engine
    Supports banking-grade interest calculations
    """
    
    @staticmethod
    def calculate_simple_interest(
        principal: Decimal,
        rate: Decimal,
        days: int
    ) -> Dict[str, Any]:
        """
        Calculate simple interest
        Formula: (P × R × T) / 36500
        where T is in days
        """
        principal = Decimal(str(principal))
        rate = Decimal(str(rate))
        days = Decimal(str(days))
        
        # Simple interest formula
        interest = (principal * rate * days) / Decimal('36500')
        interest = interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        maturity_amount = principal + interest
        
        return {
            "method": "SIMPLE",
            "principal": float(principal),
            "rate": float(rate),
            "days": int(days),
            "years": float(days / Decimal('365')),
            "interest": float(interest),
            "maturity_amount": float(maturity_amount),
            "calculation": f"({principal} × {rate} × {days}) / 36500 = {interest}"
        }
    
    @staticmethod
    def calculate_compound_interest(
        principal: Decimal,
        rate: Decimal,
        days: int,
        compounding_frequency: int = 4  # Quarterly by default
    ) -> Dict[str, Any]:
        """
        Calculate compound interest
        Formula: A = P(1 + r/n)^(nt)
        
        compounding_frequency:
        - 1: Yearly
        - 2: Half-yearly
        - 4: Quarterly
        - 12: Monthly
        """
        principal = Decimal(str(principal))
        rate = Decimal(str(rate)) / Decimal('100')  # Convert percentage
        years = Decimal(str(days)) / Decimal('365')
        n = Decimal(str(compounding_frequency))
        
        # Compound interest formula
        # A = P(1 + r/n)^(n*t)
        rate_per_period = rate / n
        num_periods = n * years
        
        # Convert to float for power calculation
        amount = float(principal) * math.pow(
            (1 + float(rate_per_period)),
            float(num_periods)
        )
        
        maturity_amount = Decimal(str(amount)).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )
        interest = maturity_amount - principal
        
        return {
            "method": "COMPOUND",
            "principal": float(principal),
            "rate": float(rate * 100),
            "days": days,
            "years": float(years),
            "compounding_frequency": compounding_frequency,
            "interest": float(interest),
            "maturity_amount": float(maturity_amount),
            "calculation": f"P(1 + r/n)^(n*t) = {principal}(1 + {float(rate_per_period):.6f})^{float(num_periods):.2f}"
        }
    
    @staticmethod
    def calculate_interest(
        principal: Decimal,
        rate: Decimal,
        days: int,
        method: InterestMethod = InterestMethod.SIMPLE
    ) -> Dict[str, Any]:
        """
        Universal interest calculator
        Routes to appropriate calculation method
        """
        compounding_map = {
            InterestMethod.SIMPLE: None,
            InterestMethod.COMPOUND_MONTHLY: 12,
            InterestMethod.COMPOUND_QUARTERLY: 4,
            InterestMethod.COMPOUND_HALF_YEARLY: 2,
            InterestMethod.COMPOUND_YEARLY: 1
        }
        
        if method == InterestMethod.SIMPLE:
            return InterestEngine.calculate_simple_interest(principal, rate, days)
        else:
            frequency = compounding_map[method]
            return InterestEngine.calculate_compound_interest(
                principal, rate, days, frequency
            )
    
    @staticmethod
    def calculate_periodic_interest(
        principal: Decimal,
        rate: Decimal,
        from_date: date,
        to_date: date,
        method: InterestMethod = InterestMethod.SIMPLE
    ) -> Dict[str, Any]:
        """
        Calculate interest for a specific period
        Used for interest posting and periodic payouts
        """
        days = (to_date - from_date).days
        
        result = InterestEngine.calculate_interest(
            principal, rate, days, method
        )
        
        result["from_date"] = from_date.isoformat()
        result["to_date"] = to_date.isoformat()
        result["period_days"] = days
        
        return result
    
    @staticmethod
    def generate_interest_schedule(
        principal: Decimal,
        rate: Decimal,
        open_date: date,
        maturity_date: date,
        payout_frequency: PayoutFrequency,
        method: InterestMethod = InterestMethod.SIMPLE
    ) -> List[Dict[str, Any]]:
        """
        Generate complete interest payment schedule
        For monthly/quarterly/yearly payouts
        """
        schedule = []
        current_date = open_date
        
        # Determine period increment
        period_map = {
            PayoutFrequency.MONTHLY: 30,
            PayoutFrequency.QUARTERLY: 90,
            PayoutFrequency.HALF_YEARLY: 180,
            PayoutFrequency.YEARLY: 365
        }
        
        if payout_frequency in [PayoutFrequency.ON_MATURITY, PayoutFrequency.CUMULATIVE]:
            # Single payout at maturity
            days = (maturity_date - open_date).days
            interest_data = InterestEngine.calculate_interest(
                principal, rate, days, method
            )
            schedule.append({
                "period": 1,
                "from_date": open_date.isoformat(),
                "to_date": maturity_date.isoformat(),
                "days": days,
                "interest": interest_data["interest"],
                "payout_date": maturity_date.isoformat()
            })
            return schedule
        
        period_days = period_map[payout_frequency]
        period = 1
        
        while current_date < maturity_date:
            next_date = current_date + timedelta(days=period_days)
            if next_date > maturity_date:
                next_date = maturity_date
            
            days = (next_date - current_date).days
            interest_data = InterestEngine.calculate_interest(
                principal, rate, days, method
            )
            
            schedule.append({
                "period": period,
                "from_date": current_date.isoformat(),
                "to_date": next_date.isoformat(),
                "days": days,
                "interest": interest_data["interest"],
                "payout_date": next_date.isoformat()
            })
            
            current_date = next_date
            period += 1
        
        return schedule
    
    @staticmethod
    def calculate_tds(
        interest_amount: Decimal,
        tds_rate: Decimal,
        pan_available: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate TDS on interest
        Higher rate if PAN not available
        """
        if not pan_available:
            tds_rate = Decimal('20.0')  # 20% without PAN
        
        tds_amount = (interest_amount * tds_rate / Decimal('100')).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )
        
        net_interest = interest_amount - tds_amount
        
        return {
            "interest_amount": float(interest_amount),
            "tds_rate": float(tds_rate),
            "tds_amount": float(tds_amount),
            "net_interest": float(net_interest),
            "pan_available": pan_available
        }
    
    @staticmethod
    def calculate_step_up_interest(
        principal: Decimal,
        rate_schedule: List[Dict[str, Any]],
        open_date: date,
        maturity_date: date
    ) -> Dict[str, Any]:
        """
        Calculate interest for step-up FDs
        Different rates for different periods
        
        rate_schedule: [
            {"from_days": 0, "to_days": 180, "rate": 6.5},
            {"from_days": 181, "to_days": 365, "rate": 7.0}
        ]
        """
        total_interest = Decimal('0')
        calculation_details = []
        
        for slab in rate_schedule:
            from_days = slab["from_days"]
            to_days = slab["to_days"]
            rate = Decimal(str(slab["rate"]))
            
            period_days = to_days - from_days + 1
            
            interest_data = InterestEngine.calculate_simple_interest(
                principal, rate, period_days
            )
            
            period_interest = Decimal(str(interest_data["interest"]))
            total_interest += period_interest
            
            calculation_details.append({
                "period": f"Day {from_days} to {to_days}",
                "days": period_days,
                "rate": float(rate),
                "interest": float(period_interest)
            })
        
        maturity_amount = principal + total_interest
        
        return {
            "method": "STEP_UP",
            "principal": float(principal),
            "total_days": (maturity_date - open_date).days,
            "total_interest": float(total_interest),
            "maturity_amount": float(maturity_amount),
            "rate_slabs": calculation_details
        }
    
    @staticmethod
    def calculate_effective_yield(
        principal: Decimal,
        maturity_amount: Decimal,
        days: int
    ) -> Decimal:
        """
        Calculate effective annualized yield
        Useful for comparing different deposit schemes
        """
        if days == 0:
            return Decimal('0')
        
        returns = maturity_amount - principal
        return_percentage = (returns / principal) * Decimal('100')
        
        # Annualize
        effective_yield = (return_percentage * Decimal('365')) / Decimal(str(days))
        
        return effective_yield.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
