"""
SCB Morning Briefing Agent
Generates personalized N=1 morning briefing for SCB EASY app users.
Uses real SCBX public data enriched with customer-specific context.

Architecture:
  Customer Data (Digital Twin) -> Agent Pipeline -> Personalized JSON -> UI Renderer

Modules:
  1. Financial Health Scorer   – computes 4-pillar wellness score
  2. Nudge Generator           – "For You" lifestyle + financial nudges
  3. Task Prioritizer           – today's actionable tasks
  4. Insight Engine             – spending, portfolio, savings insights
  5. Savings Advisor            – "Ways to Save" recommendations
  6. Alert Engine               – bill due dates, anomaly detection
  7. Morning Brief Composer     – orchestrates all modules into final output
"""

import json
import datetime
import random
from dataclasses import dataclass, field, asdict
from typing import Optional


# ---------------------------------------------------------------------------
# Real SCBX/SCB Public Data (sourced from 2025 annual report & public filings)
# ---------------------------------------------------------------------------
SCBX_CONTEXT = {
    "bank_name": "SCB",
    "group_name": "SCBX",
    "app_name": "SCB EASY",
    "net_profit_2025_mthb": 47488,
    "total_assets_bthb": 3300,
    "total_loans_bthb": 2353.9,
    "cost_to_income_pct": 40.5,
    "npl_ratio_pct": 3.29,
    "car_pct": 18.9,
    "easy_app_users_mn": 15.4,
    "monthly_transactions_mn": 400,
    "set_index": 1485,
    "set_index_ytd_pct": 3.2,
    "policy_rate_pct": 2.25,
    "fd_rate_12m_pct": 1.30,
    "subsidiaries": {
        "CardX": "Credit cards, personal loans, nano finance",
        "AutoX": "Auto financing",
        "PointX": "Unified loyalty rewards platform",
        "SCB_TechX": "Technology and digital infrastructure",
        "Purple_Ventures": "Digital lifestyle platforms (Robinhood)",
        "SCB_WEALTH": "Wealth management",
        "MONIX": "Micro-lending, digital lending",
    },
    "pointx": {
        "earn_rate": "1 point per 25 THB on CardX",
        "redemption": "QR payments, X Store, airline miles, cashback",
    },
}

# Thai market context for realistic nudges
THAI_MARKET_DATA = {
    "set_index_current": 1485.16,
    "set_index_prev_close": 1477.41,
    "set_change_pct": 0.52,
    "gold_thb_per_baht": 44350,
    "gold_change_pct": 1.8,
    "usd_thb": 33.85,
    "usd_change_pct": -0.3,
    "top_set_gainers": ["DELTA", "GULF", "BDMS"],
    "top_set_losers": ["PTT", "AOT", "CPALL"],
}


# ---------------------------------------------------------------------------
# Customer Digital Twin
# ---------------------------------------------------------------------------
@dataclass
class SpendingCategory:
    name: str
    amount_thb: float
    pct_of_total: float
    mom_change_pct: float
    color: str = "#7b5ea7"


@dataclass
class Account:
    type: str
    name: str
    number_masked: str
    balance_thb: float
    institution: str = "SCB"


@dataclass
class CreditCard:
    name: str
    number_masked: str
    issuer: str
    credit_limit_thb: float
    current_balance_thb: float
    minimum_payment_thb: float
    due_date: str
    points_balance: int
    interest_rate_pct: float = 16.0


@dataclass
class Investment:
    name: str
    type: str
    value_thb: float
    return_pct: float
    benchmark_return_pct: float


@dataclass
class CustomerProfile:
    name: str
    nickname: str
    age: int
    occupation: str
    segment: str
    monthly_income_thb: float
    accounts: list = field(default_factory=list)
    credit_cards: list = field(default_factory=list)
    investments: list = field(default_factory=list)
    spending_categories: list = field(default_factory=list)
    total_savings_thb: float = 0
    savings_rate_pct: float = 0
    savings_mom_change_thb: float = 0
    financial_goals: list = field(default_factory=list)
    interests: list = field(default_factory=list)
    recent_behaviors: list = field(default_factory=list)
    recurring_bills: list = field(default_factory=list)
    location: str = "Bangkok"


# ---------------------------------------------------------------------------
# Realistic demo persona using real SCB products
# ---------------------------------------------------------------------------
def create_demo_persona() -> CustomerProfile:
    return CustomerProfile(
        name="Khun Eva Suthirak",
        nickname="Eva",
        age=31,
        occupation="Marketing Manager",
        segment="Wealth Potential",
        monthly_income_thb=65000,
        total_savings_thb=348500,
        savings_rate_pct=22,
        savings_mom_change_thb=2540,
        accounts=[
            Account("savings", "SCB Easy Savings", "XXX-XXX596-3", 185400),
            Account("savings", "SCB Goal Save", "XXX-XXX847-1", 163100),
        ],
        credit_cards=[
            CreditCard(
                name="SCB WEALTH Credit Card by CardX",
                number_masked="XXXX-XXXX-XXXX-4624",
                issuer="CardX",
                credit_limit_thb=150000,
                current_balance_thb=22300,
                minimum_payment_thb=1115,
                due_date="2026-04-25",
                points_balance=18750,
                interest_rate_pct=16.0,
            ),
        ],
        investments=[
            Investment("SCB SET Index Fund", "Equity Fund", 120000, 4.8, 3.2),
            Investment("S&P500 DCA", "Foreign Equity", 85000, 8.2, 7.1),
            Investment("SCB Income Plus", "Bond Fund", 45000, 3.1, 2.8),
            Investment("SCB Gold Fund", "Commodity", 15000, 12.4, 11.0),
        ],
        spending_categories=[
            SpendingCategory("Dining", 12800, 32, 8.0, "#e74c3c"),
            SpendingCategory("Transport", 9600, 24, -2.1, "#3498db"),
            SpendingCategory("Shopping", 7200, 18, 5.3, "#9b59b6"),
            SpendingCategory("Groceries", 4800, 12, 1.2, "#2ecc71"),
            SpendingCategory("Entertainment", 3200, 8, -4.5, "#f1c40f"),
            SpendingCategory("Health & Fitness", 2400, 6, -15.0, "#e67e22"),
        ],
        financial_goals=[
            {"name": "Emergency Fund", "target_thb": 195000, "current_thb": 163100, "pct": 84},
            {"name": "Japan Trip 2027", "target_thb": 80000, "current_thb": 32000, "pct": 40},
            {"name": "Down Payment (Condo)", "target_thb": 500000, "current_thb": 85000, "pct": 17},
        ],
        interests=["pilates", "skincare", "travel", "coffee", "investing"],
        recent_behaviors=[
            "Browsed Pilates class schedules on ClassPass",
            "Searched skincare products on Beautrium",
            "Booked Singapore weekend flight on Traveloka",
            "Worked late 4 nights this week (from SCB Easy login times)",
            "Increased DCA contribution last month",
        ],
        recurring_bills=[
            {"name": "AIS Phone Bill", "amount_thb": 899, "due_day": 15, "auto_pay": False},
            {"name": "Netflix", "amount_thb": 419, "due_day": 8, "auto_pay": True},
            {"name": "Condo Maintenance", "amount_thb": 3500, "due_day": 5, "auto_pay": True},
            {"name": "BTS Rabbit Card Top-up", "amount_thb": 1400, "due_day": None, "auto_pay": False},
        ],
        location="Bangkok",
    )


# ---------------------------------------------------------------------------
# Module 1: Financial Health Scorer
# ---------------------------------------------------------------------------
class FinancialHealthScorer:
    """Computes a 0-100 financial wellness score across 4 pillars."""

    @staticmethod
    def score(customer: CustomerProfile) -> dict:
        total_investments = sum(i.value_thb for i in customer.investments)
        total_credit_balance = sum(c.current_balance_thb for c in customer.credit_cards)
        total_credit_limit = sum(c.credit_limit_thb for c in customer.credit_cards)

        # Liquidity: savings / (6 months expenses)
        monthly_expenses = customer.monthly_income_thb * (1 - customer.savings_rate_pct / 100)
        liquidity_months = customer.total_savings_thb / monthly_expenses if monthly_expenses > 0 else 0
        liquidity_score = min(100, int(liquidity_months / 6 * 100))
        liquidity_label = "Good" if liquidity_score >= 70 else "Average" if liquidity_score >= 40 else "Low"

        # Investment: portfolio diversity + returns vs benchmark
        avg_alpha = 0
        if customer.investments:
            avg_alpha = sum(i.return_pct - i.benchmark_return_pct for i in customer.investments) / len(customer.investments)
        invest_ratio = total_investments / (customer.monthly_income_thb * 12) if customer.monthly_income_thb > 0 else 0
        investment_score = min(100, int(invest_ratio * 100 + avg_alpha * 10))
        investment_label = "Good" if investment_score >= 70 else "Below Average" if investment_score < 50 else "Average"

        # Borrowing: credit utilization
        utilization = total_credit_balance / total_credit_limit if total_credit_limit > 0 else 0
        borrowing_score = max(0, int((1 - utilization) * 100))
        borrowing_label = "Good" if borrowing_score >= 80 else "Average" if borrowing_score >= 50 else "High Risk"

        # Insurance: simplified heuristic
        insurance_score = 55
        insurance_label = "Average"

        overall = int(0.30 * liquidity_score + 0.25 * investment_score + 0.25 * borrowing_score + 0.20 * insurance_score)
        peer_percentile = min(95, max(5, overall + random.randint(-8, 12)))

        return {
            "overall_score": overall,
            "overall_label": "Good" if overall >= 60 else "Fair" if overall >= 40 else "Needs Attention",
            "peer_percentile": peer_percentile,
            "pillars": {
                "investment": {"score": investment_score, "label": investment_label},
                "borrowing": {"score": borrowing_score, "label": borrowing_label},
                "insurance": {"score": insurance_score, "label": insurance_label},
                "liquidity": {"score": liquidity_score, "label": liquidity_label},
            },
            "message": f"{customer.nickname}, you're on track! A few tweaks can strengthen your financial wellness.",
        }


# ---------------------------------------------------------------------------
# Module 2: Nudge Generator ("For You")
# ---------------------------------------------------------------------------
class NudgeGenerator:
    """Generates personalized lifestyle + financial nudges based on behavior signals."""

    @staticmethod
    def generate(customer: CustomerProfile) -> list:
        nudges = []

        for behavior in customer.recent_behaviors:
            if "pilates" in behavior.lower() or "classpass" in behavior.lower():
                nudges.append({
                    "icon": "fitness",
                    "text": "You haven't been to Pilates in 2 weeks? ClassPass is offering 30% off your next 5 classes!",
                    "category": "lifestyle",
                    "action_url": "#classpass",
                })
            if "skincare" in behavior.lower() or "beautrium" in behavior.lower():
                nudges.append({
                    "icon": "beauty",
                    "text": "Running out of sunscreen? Beautrium is having summer sales - up to 40% off!",
                    "category": "lifestyle",
                    "action_url": "#beautrium",
                })
            if "singapore" in behavior.lower() or "flight" in behavior.lower():
                nudges.append({
                    "icon": "travel",
                    "text": "Upcoming weekend in Singapore - see which airport lounges are available with your CardX!",
                    "category": "travel",
                    "action_url": "#lounges",
                })
            if "worked late" in behavior.lower():
                nudges.append({
                    "icon": "wellness",
                    "text": "You've been working late 4 nights this week. Here are spa vouchers from PointX just for you!",
                    "category": "wellness",
                    "action_url": "#pointx-spa",
                })

        if customer.credit_cards and customer.credit_cards[0].points_balance > 10000:
            pts = customer.credit_cards[0].points_balance
            nudges.append({
                "icon": "rewards",
                "text": f"You have {pts:,} PointX waiting! Redeem for your Singapore trip or convert to airline miles.",
                "category": "financial",
                "action_url": "#pointx",
            })

        return nudges[:5]


# ---------------------------------------------------------------------------
# Module 3: Task Prioritizer
# ---------------------------------------------------------------------------
class TaskPrioritizer:
    """Identifies and prioritizes today's actionable tasks."""

    @staticmethod
    def generate(customer: CustomerProfile) -> list:
        today = datetime.date.today()
        tasks = []

        for bill in customer.recurring_bills:
            if not bill.get("auto_pay") and bill.get("due_day"):
                days_until = bill["due_day"] - today.day
                if 0 <= days_until <= 5:
                    tasks.append({
                        "text": f"Pay {bill['name']}",
                        "amount_thb": bill["amount_thb"],
                        "due": f"Due in {days_until} day{'s' if days_until != 1 else ''}",
                        "completed": days_until < 0,
                        "priority": "high" if days_until <= 2 else "medium",
                    })

        has_dca = any("dca" in i.name.lower() or "s&p" in i.name.lower() for i in customer.investments)
        if has_dca:
            tasks.append({
                "text": "DCA on S&P500",
                "amount_thb": 5000,
                "due": "Monthly recurring",
                "completed": False,
                "priority": "medium",
            })

        if customer.credit_cards:
            tasks.append({
                "text": f"Review CardX statements",
                "amount_thb": None,
                "due": "This week",
                "completed": False,
                "priority": "low",
            })

        for goal in customer.financial_goals:
            if goal["pct"] >= 80:
                tasks.append({
                    "text": f"Top up {goal['name']} (almost there!)",
                    "amount_thb": goal["target_thb"] - goal["current_thb"],
                    "due": "When ready",
                    "completed": False,
                    "priority": "low",
                })

        return tasks[:5]


# ---------------------------------------------------------------------------
# Module 4: Insight Engine
# ---------------------------------------------------------------------------
class InsightEngine:
    """Generates spending, portfolio, and savings insights."""

    @staticmethod
    def generate(customer: CustomerProfile) -> list:
        insights = []

        # Spending anomaly
        overspend = [c for c in customer.spending_categories if c.mom_change_pct > 5]
        if overspend:
            top = max(overspend, key=lambda x: x.mom_change_pct)
            insights.append({
                "icon": "warning",
                "title": f"{top.name} spend up to +{top.mom_change_pct:.0f}%",
                "subtitle": f"vs last month - you might be overspending",
                "type": "spending",
                "sentiment": "negative",
            })

        # Portfolio performance
        total_portfolio = sum(i.value_thb for i in customer.investments)
        avg_return = sum(i.return_pct * i.value_thb for i in customer.investments) / total_portfolio if total_portfolio > 0 else 0
        avg_benchmark = sum(i.benchmark_return_pct * i.value_thb for i in customer.investments) / total_portfolio if total_portfolio > 0 else 0
        alpha = avg_return - avg_benchmark
        insights.append({
            "icon": "trending_up",
            "title": f"Portfolio +{avg_return:.1f}% (3M)",
            "subtitle": f"Outperforming benchmark by {alpha:.1f}%",
            "type": "portfolio",
            "sentiment": "positive",
        })

        # Savings trend
        if customer.savings_mom_change_thb > 0:
            insights.append({
                "icon": "savings",
                "title": f"You saved {customer.savings_mom_change_thb:,.0f} THB more this month",
                "subtitle": f"Savings rate now at {customer.savings_rate_pct}%",
                "type": "savings",
                "sentiment": "positive",
            })

        # Market insight
        insights.append({
            "icon": "market",
            "title": f"SET Index at {THAI_MARKET_DATA['set_index_current']:,.2f}",
            "subtitle": f"+{THAI_MARKET_DATA['set_change_pct']}% today. Your SCB SET Fund is tracking well.",
            "type": "market",
            "sentiment": "positive",
        })

        return insights


# ---------------------------------------------------------------------------
# Module 5: Savings Advisor
# ---------------------------------------------------------------------------
class SavingsAdvisor:
    """Generates 'Ways to Save' recommendations based on spending patterns."""

    @staticmethod
    def generate(customer: CustomerProfile) -> dict:
        top_categories = sorted(customer.spending_categories, key=lambda x: x.amount_thb, reverse=True)[:3]

        tips = []
        for cat in customer.spending_categories:
            if cat.name == "Dining" and cat.mom_change_pct > 5:
                tips.append({
                    "text": "Try meal prepping 2x a week to save ~3,000 THB/month on dining",
                    "potential_saving_thb": 3000,
                })
            if cat.name == "Transport":
                tips.append({
                    "text": "Switch to BTS monthly pass to save up to THB 800/month",
                    "potential_saving_thb": 800,
                })

        for bill in customer.recurring_bills:
            if not bill.get("auto_pay"):
                tips.append({
                    "text": f"Switch {bill['name']} to auto-pay to avoid late fees (save up to THB 200/year)",
                    "potential_saving_thb": 200,
                })

        total_potential = sum(t["potential_saving_thb"] for t in tips)
        return {
            "top_spending_categories": [
                {"name": c.name, "pct": c.pct_of_total, "amount_thb": c.amount_thb, "color": c.color}
                for c in top_categories
            ],
            "tips": tips[:4],
            "total_potential_saving_thb": total_potential,
            "auto_pay_tip": f"Switch to auto-pay to save up to THB 5,000/month to avoid late fees",
        }


# ---------------------------------------------------------------------------
# Module 6: Alert Engine
# ---------------------------------------------------------------------------
class AlertEngine:
    """Generates bill alerts and payment options."""

    @staticmethod
    def generate(customer: CustomerProfile) -> list:
        alerts = []
        today = datetime.date.today()

        for card in customer.credit_cards:
            due = datetime.date.fromisoformat(card.due_date)
            days_until = (due - today).days
            if days_until <= 15:
                interest_if_minimum = round(card.current_balance_thb * card.interest_rate_pct / 100 / 12, 0)
                installment_6m = round(card.current_balance_thb / 6, 0)
                alerts.append({
                    "type": "bill_due",
                    "card_name": card.name,
                    "card_number": card.number_masked,
                    "issuer": card.issuer,
                    "total_amount_thb": card.current_balance_thb,
                    "due_date": card.due_date,
                    "days_until_due": days_until,
                    "payment_options": [
                        {
                            "label": "Minimum payment",
                            "amount_thb": card.minimum_payment_thb,
                            "note": f"+THB {interest_if_minimum:,.0f} interest",
                            "recommended": False,
                        },
                        {
                            "label": "Full payment",
                            "amount_thb": card.current_balance_thb,
                            "note": "No interest",
                            "recommended": True,
                        },
                        {
                            "label": "6-month installment",
                            "amount_thb": installment_6m,
                            "note": "0% interest",
                            "recommended": False,
                            "is_monthly": True,
                        },
                    ],
                    "message": (
                        f"Your {card.issuer} ending {card.number_masked[-4:]} bill is due soon. "
                        f"Paying only the minimum would add up to {interest_if_minimum:,.0f} THB in interest."
                    ),
                })

        return alerts


# ---------------------------------------------------------------------------
# Module 7: Morning Brief Composer (Orchestrator)
# ---------------------------------------------------------------------------
class MorningBriefingAgent:
    """
    Orchestrates all modules to produce a complete, personalized morning briefing.
    This is the main agent entry point.
    """

    def __init__(self, customer: CustomerProfile):
        self.customer = customer
        self.health_scorer = FinancialHealthScorer()
        self.nudge_gen = NudgeGenerator()
        self.task_gen = TaskPrioritizer()
        self.insight_gen = InsightEngine()
        self.savings_gen = SavingsAdvisor()
        self.alert_gen = AlertEngine()

    def generate(self) -> dict:
        now = datetime.datetime.now()
        hour = now.hour
        if hour < 12:
            greeting_time = "morning"
        elif hour < 17:
            greeting_time = "afternoon"
        else:
            greeting_time = "evening"

        c = self.customer
        total_portfolio = sum(i.value_thb for i in c.investments)

        briefing = {
            "meta": {
                "generated_at": now.isoformat(),
                "customer_id": "demo-001",
                "persona": c.segment,
                "version": "1.0",
            },
            "greeting": {
                "time_of_day": greeting_time,
                "name": c.nickname,
                "message": f"Good {greeting_time}, {c.nickname}",
                "subtitle": "Here's your hot matcha for the day, and your personal briefing",
            },
            "financial_health": self.health_scorer.score(c),
            "for_you_nudges": self.nudge_gen.generate(c),
            "todays_tasks": self.task_gen.generate(c),
            "key_insights": self.insight_gen.generate(c),
            "ways_to_save": self.savings_gen.generate(c),
            "alerts": self.alert_gen.generate(c),
            "portfolio_summary": {
                "total_value_thb": total_portfolio,
                "investments": [
                    {
                        "name": i.name,
                        "type": i.type,
                        "value_thb": i.value_thb,
                        "return_pct": i.return_pct,
                    }
                    for i in c.investments
                ],
            },
            "accounts_summary": {
                "total_savings_thb": c.total_savings_thb,
                "accounts": [
                    {"name": a.name, "number": a.number_masked, "balance_thb": a.balance_thb}
                    for a in c.accounts
                ],
            },
            "market_snapshot": THAI_MARKET_DATA,
            "scbx_context": {
                "app": SCBX_CONTEXT["app_name"],
                "pointx_balance": c.credit_cards[0].points_balance if c.credit_cards else 0,
            },
        }

        return briefing

    def generate_json(self, indent: int = 2) -> str:
        return json.dumps(self.generate(), indent=indent, ensure_ascii=False, default=str)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    customer = create_demo_persona()
    agent = MorningBriefingAgent(customer)
    briefing = agent.generate()

    # Write to JSON file for the HTML demo to consume
    output_path = "morning_briefing_data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(briefing, f, indent=2, ensure_ascii=False, default=str)

    print(f"Morning briefing generated for {customer.nickname}")
    print(f"Financial Health Score: {briefing['financial_health']['overall_score']}/100")
    print(f"Nudges: {len(briefing['for_you_nudges'])}")
    print(f"Tasks: {len(briefing['todays_tasks'])}")
    print(f"Insights: {len(briefing['key_insights'])}")
    print(f"Alerts: {len(briefing['alerts'])}")
    print(f"\nOutput saved to: {output_path}")
    print(f"\nFull JSON:\n{agent.generate_json()}")
