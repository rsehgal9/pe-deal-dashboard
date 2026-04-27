# Private Equity Deal Dashboard (Mini LBO)

## Overview

This project is an interactive dashboard designed to simulate how private equity investors **screen and evaluate potential acquisition targets**.

Instead of looking at companies one-by-one, the tool allows users to:
- Filter and compare multiple businesses
- Identify the most attractive investment opportunities
- Estimate potential returns using a simplified deal model

The goal is to replicate the **early-stage investment process** used by private equity firms.

---

## What This Tool Does

### 1. Screens Companies Based on Key Metrics
Users can filter companies using important investment criteria such as:
- Revenue growth
- Profitability (EBITDA margin)
- Valuation (EV / EBITDA)
- Leverage (Debt / EBITDA)

This helps narrow a large set of companies into a smaller group of high-potential targets.

---

### 2. Ranks Investment Opportunities
The dashboard applies a scoring system to rank companies based on their:
- Growth potential
- Profitability
- Valuation attractiveness
- Financial risk

This mimics how investors prioritize which deals to spend time on.

---

### 3. Simulates a Private Equity Investment (Mini LBO)
For each company, the tool estimates:
- Entry value (what you pay to acquire the company)
- Debt and equity structure
- Future earnings growth over a holding period
- Exit value (what the company could be worth when sold)

From this, it calculates:
- **MOIC (Multiple of Invested Capital)** – how much the investment grows
- **IRR (Internal Rate of Return)** – the annualized return

---

### 4. Tests Different Scenarios
Users can adjust assumptions such as:
- Holding period (how long the investment is held)
- Exit valuation multiple
- Growth expectations
- Debt repayment

This allows users to see how sensitive returns are to different conditions.

---

### 5. Provides Clear Investment Insights
The dashboard highlights:
- The top-ranked investment opportunity
- Key reasons why it stands out
- How it compares to other companies

This reflects how analysts summarize investment ideas for decision-makers.

---

## Why This Project Matters

In private equity, the challenge is not just finding companies—it’s:
- Identifying **which ones are worth pursuing**
- Understanding **what drives returns**
- Evaluating **risk vs. reward**

This dashboard brings those concepts together in a single, interactive tool.

It demonstrates how financial data, investment logic, and decision-making can be combined into a structured workflow.

---

## Who This Is For

This tool is useful for:
- Students learning about private equity and investing
- Anyone interested in how deals are evaluated
- Users who want a simplified view of financial modeling and returns

No coding or technical background is required to understand or use the dashboard.

---

## How to Run the Project

1. Install required packages:
   ```bash
   pip install -r requirements.txt
