"""
Investor Portfolio Module
Manages investor portfolios and investment tracking.
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.models import Investment, User, Startup
from app.utils.logger import logger


class InvestorPortfolio:
    """Investor portfolio management service."""
    
    def get_portfolio(
        self,
        investor_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """
        Get investor portfolio with all investments.
        
        Returns:
            Portfolio data with investments, totals, and performance
        """
        logger.info(f"Getting portfolio for investor {investor_id}")
        
        # Get investor
        investor = db.query(User).filter(User.id == investor_id).first()
        if not investor:
            raise ValueError(f"Investor {investor_id} not found")
        
        # Get all investments (excluding mock transactions)
        investments = db.query(Investment).filter(
            Investment.investor_id == investor_id,
            ~Investment.tx_signature.like("mock_%")
        ).order_by(Investment.timestamp.desc()).all()
        
        # Calculate portfolio metrics
        total_invested = sum(inv.amount for inv in investments)
        investment_count = len(investments)
        
        # Group by startup
        startup_investments = {}
        for inv in investments:
            startup = db.query(Startup).filter(Startup.id == inv.startup_id).first()
            if startup:
                startup_id = startup.startup_id
                if startup_id not in startup_investments:
                    startup_investments[startup_id] = {
                        "startup_id": startup_id,
                        "startup_name": startup.name,
                        "sector": startup.sector,
                        "credibility_score": startup.credibility_score,
                        "total_invested": 0,
                        "investment_count": 0,
                        "investments": []
                    }
                
                startup_investments[startup_id]["total_invested"] += inv.amount
                startup_investments[startup_id]["investment_count"] += 1
                startup_investments[startup_id]["investments"].append({
                    "id": inv.id,
                    "amount": inv.amount,
                    "tx_signature": inv.tx_signature,
                    "timestamp": inv.timestamp.isoformat() if inv.timestamp else None,
                    "explorer_url": f"https://explorer.solana.com/tx/{inv.tx_signature}?cluster=devnet" if inv.tx_signature and not inv.tx_signature.startswith("mock_") and not inv.tx_signature.startswith("stripe:") else None
                })
        
        return {
            "investor_id": investor_id,
            "investor_name": investor.full_name,
            "wallet_address": investor.wallet_address,
            "total_invested_usdc": total_invested,
            "total_investments": investment_count,
            "startup_count": len(startup_investments),
            "startups": list(startup_investments.values()),
            "all_investments": [
                {
                    "id": inv.id,
                    "startup_id": inv.startup.startup_id if inv.startup else None,
                    "startup_name": inv.startup.name if inv.startup else "Unknown",
                    "amount": inv.amount,
                    "tx_signature": inv.tx_signature,
                    "timestamp": inv.timestamp.isoformat() if inv.timestamp else None,
                    "explorer_url": f"https://explorer.solana.com/tx/{inv.tx_signature}?cluster=devnet" if inv.tx_signature and not inv.tx_signature.startswith("mock_") and not inv.tx_signature.startswith("stripe:") else None
                }
                for inv in investments
            ]
        }
    
    def get_startup_investments(
        self,
        startup_id: str,
        db: Session
    ) -> List[Dict[str, Any]]:
        """
        Get all investments for a specific startup.
        
        Returns:
            List of investments with investor details
        """
        logger.info(f"Getting investments for startup {startup_id}")
        
        startup = db.query(Startup).filter(Startup.startup_id == startup_id).first()
        if not startup:
            raise ValueError(f"Startup {startup_id} not found")
        
        investments = db.query(Investment).filter(
            Investment.startup_id == startup.id
        ).order_by(Investment.timestamp.desc()).all()
        
        result = []
        for inv in investments:
            investor = db.query(User).filter(User.id == inv.investor_id).first()
            result.append({
                "id": inv.id,
                "investor_id": inv.investor_id,
                "investor_name": investor.full_name if investor else "Unknown",
                "investor_email": investor.email if investor else None,
                "amount": inv.amount,
                "tx_signature": inv.tx_signature,
                "timestamp": inv.timestamp.isoformat() if inv.timestamp else None,
                "explorer_url": f"https://explorer.solana.com/tx/{inv.tx_signature}?cluster=devnet" if inv.tx_signature and not inv.tx_signature.startswith("mock_") and not inv.tx_signature.startswith("stripe:") else None
            })
        
        return result

