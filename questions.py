"""
The 10 preset demo / test questions.

`reference` is a note to help YOU grade answers by hand. The code never
uses it to judge correctness.
"""

QUESTIONS = [
    # --- Exact questions: precision matters -------------------------------
    {
        "id": "E1",
        "type": "exact",
        "question": "How is Monthly Active Users (MAU) defined at Northwind Analytics?",
        "reference": "Distinct users with >=1 qualifying action (run a query, view a dashboard >=10s, "
                     "create/edit a report) in the trailing 28 days, UTC; excludes internal, test and "
                     "API-only accounts. Effective 2026-03-01. The OLD 'logged in during the calendar month' "
                     "definition is wrong.",
    },
    {
        "id": "E2",
        "type": "exact",
        "question": "In the Reports API v2, which response field shows when a report was last refreshed, and what format is it in?",
        "reference": "last_refreshed_at: ISO 8601 timestamp in UTC (e.g. 2026-09-01T08:30:00Z).",
    },
    {
        "id": "E3",
        "type": "exact",
        "question": "What is the refund window for annual plans?",
        "reference": "30 days from the initial purchase or the annual renewal date (full refund). "
                     "14 and 60 days are wrong (old meeting-note claims).",
    },
    {
        "id": "E4",
        "type": "exact",
        "question": "How much does the Growth tier cost per user, and how many API calls per day does it include?",
        "reference": "$79/user/month billed annually ($95 billed monthly); 10,000 API calls per day.",
    },
    {
        "id": "E5",
        "type": "exact",
        "question": "Which team owns the Reports API, and who leads that team?",
        "reference": "Platform API team, led by Marcus Okafor.",
    },
    # --- Open-ended questions: answer only exists in the messy /raw data ------------
    {
        "id": "O1",
        "type": "open-ended",
        "question": "What are customers complaining about most?",
        "reference": "Slow dashboards (large/many widgets), CSV export truncated at 10,000 rows, "
                     "SSO only on Enterprise (price), scheduled-report timezone bugs, mobile app crashes.",
    },
    {
        "id": "O2",
        "type": "open-ended",
        "question": "What features did customers request in August 2026?",
        "reference": "Dark mode for dashboards, scheduled PDF delivery to Slack, Excel (.xlsx) export, "
                     "row-level permissions on Growth, custom fiscal calendar, Snowflake write-back.",
    },
    {
        "id": "O3",
        "type": "open-ended",
        "question": "Which customers are at risk of churning, and why?",
        "reference": "Brightline Logistics (slow dashboards), Kestrel Health (SSO requires Enterprise), "
                     "Vantage Foods (CSV export truncation).",
    },
    {
        "id": "O4",
        "type": "open-ended",
        "question": "What problems do new customers run into during onboarding?",
        "reference": "Confusing data-source connection step (Postgres/SSL, IP allowlist), invite emails "
                     "landing in spam, empty dashboards with no templates/sample data.",
    },
    {
        "id": "O5",
        "type": "open-ended",
        "question": "What issues have customers reported with CSV exports?",
        "reference": "Exports silently truncated at 10,000 rows; date columns in wrong timezone/format; "
                     "UTF-8 characters garbled in Excel (no BOM).",
    },
]
