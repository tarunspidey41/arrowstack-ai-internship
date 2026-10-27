"""Generate SIMULATED support tickets (no real customer data is used).

train.csv       - templates A (seen phrasing)
eval.csv        - 50% seen templates + 50% HELD-OUT templates (unseen phrasing) + typos
hard_cases.csv  - hand-written ambiguous / multi-issue tickets

Run:  python scripts/generate_data.py
"""
import random
import csv
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

CORE = {
    "billing": [
        "I was charged twice for my {plan} subscription this month.",
        "My invoice #{n} shows an amount I do not recognise.",
        "Please refund the payment of Rs {amt} made on {date}.",
        "The discount code {code} was not applied at checkout.",
        "I want to update the credit card on file because it expires soon.",
        "Why did my bill increase after the plan renewal?",
        "I cancelled my plan but I still got billed.",
        # held-out (eval only)
        "The GST amount on my latest invoice looks wrong.",
        "Money was deducted from my bank but the payment shows as pending.",
    ],
    "technical": [
        "The app crashes every time I open the {feature} page.",
        "I get a 500 error when exporting reports.",
        "The dashboard has been loading very slowly since this morning.",
        "Sync between mobile and desktop has stopped working.",
        "API requests return timeout errors intermittently.",
        "File upload fails at 90 percent with an unknown error.",
        "Notifications are not being delivered to my phone.",
        # held-out
        "The search box returns blank results for anything I type.",
        "Screen freezes and the page never finishes rendering after the latest update.",
    ],
    "account_access": [
        "I forgot my password and the reset email never arrives.",
        "My account is locked after too many login attempts.",
        "I cannot log in, it says my credentials are invalid.",
        "The two-factor code is not accepted on my new phone.",
        "Please change the email address linked to my account.",
        "I need access added for a new team member.",
        "My username is not recognised at sign in.",
        # held-out
        "After changing my number I cannot receive the verification code to get in.",
        "Unable to get into my profile, the page keeps sending me back to the sign in screen.",
    ],
    "security": [
        "I received a suspicious email pretending to be from your company asking for my password.",
        "I think someone accessed my account without permission, there are logins from another country.",
        "I found a vulnerability: the API returns other users' email addresses.",
        "My API key was exposed in a public repository.",
        "There are unauthorised transactions on my account.",
        "Possible data breach: customer records are visible to other tenants.",
        "A phishing site is using your company logo.",
        # held-out
        "Someone has been sending messages from my profile and I did not write them.",
        "Our audit logs show an unknown admin account created last night.",
    ],
    "feature_request": [
        "It would be great to have a dark mode.",
        "Can you add export to Excel on the reports page?",
        "Please consider adding single sign-on with Google.",
        "We would love a bulk edit option for contacts.",
        "Is there a plan to support a Tamil language interface?",
        "Suggestion: add keyboard shortcuts for common actions.",
        "It would help if the calendar view could show week numbers.",
        # held-out
        "Our team needs a way to schedule reports to be emailed every Monday.",
        "Would you ever build a native tablet version?",
    ],
    "general_inquiry": [
        "What are your support hours on weekends?",
        "Do you have a student discount?",
        "Where can I find the user guide for the {feature} module?",
        "Where can I find your data retention policy?",
        "Can I get a demo for my team?",
        "Which regions are your servers hosted in?",
        "How many users can I add on the starter plan?",
        # held-out
        "Is your service available in Hindi and Tamil support?",
        "Could someone explain the difference between the standard and premium tiers?",
    ],
}
HELD_OUT = 2  # last N templates per type are eval-only

URGENCY_PHRASES = {
    "critical": [
        "Our whole production system is down.",
        "All our users are affected and we are losing revenue.",
        "This is an emergency, it is happening right now.",
        "Customers cannot place any orders at all.",
    ],
    "high": [
        "I cannot work until this is fixed.",
        "We have a client deadline today.",
        "This is blocking my whole team.",
        "Please resolve this within a few hours.",
    ],
    "medium": [
        "It is affecting my work a bit but I have a workaround.",
        "Please look into this in the next couple of days.",
        "This keeps happening and it is quite annoying.",
    ],
    "low": [
        "No rush at all.",
        "Whenever you get a chance.",
        "Just a minor thing.",
        "Not urgent, just wanted to mention it.",
    ],
}
# urgency weights by issue type (low, medium, high, critical)
URGENCY_WEIGHTS = {
    "billing": [0.25, 0.4, 0.3, 0.05],
    "technical": [0.15, 0.35, 0.3, 0.2],
    "account_access": [0.15, 0.35, 0.4, 0.1],
    "security": [0.0, 0.1, 0.45, 0.45],
    "feature_request": [0.7, 0.3, 0.0, 0.0],
    "general_inquiry": [0.7, 0.3, 0.0, 0.0],
}
DEFAULT_URGENCY = {  # label when the ticket carries NO urgency cue
    "billing": "medium", "technical": "medium", "account_access": "medium",
    "security": "high", "feature_request": "low", "general_inquiry": "low",
}
GREET = ["Hi,", "Hello team,", "Good morning,", "Dear support,", "", ""]
CLOSE = ["Thanks.", "Thank you.", "Regards, Arun", "Please help.", "", ""]
PLANS = ["Pro", "Starter", "Team", "Business"]
FEATURES = ["reports", "billing", "profile", "analytics", "settings"]
CODES = ["WELCOME10", "FEST25", "STUDENT50"]


def typo(s: str, rng: random.Random, p: float) -> str:
    chars = list(s)
    for i in range(1, len(chars) - 1):
        if chars[i].isalpha() and rng.random() < p:
            op = rng.choice(["swap", "drop", "dup"])
            if op == "swap":
                chars[i], chars[i + 1] = chars[i + 1], chars[i]
            elif op == "drop":
                chars[i] = ""
            else:
                chars[i] = chars[i] * 2
    return "".join(chars)


def make_ticket(rng, issue, templates, typo_p):
    core = rng.choice(templates).format(
        plan=rng.choice(PLANS), n=rng.randint(1000, 9999), amt=rng.choice([499, 999, 1499, 2999]),
        date=f"{rng.randint(1, 28)}/{rng.randint(1, 12)}", code=rng.choice(CODES),
        feature=rng.choice(FEATURES))
    # 25% of tickets carry no urgency cue -> label = type default
    if rng.random() < 0.25:
        urgency, cue = DEFAULT_URGENCY[issue], ""
    else:
        urgency = rng.choices(["low", "medium", "high", "critical"], URGENCY_WEIGHTS[issue])[0]
        cue = rng.choice(URGENCY_PHRASES[urgency])
    parts = [rng.choice(GREET), core, cue, rng.choice(CLOSE)]
    body = " ".join(p for p in parts if p)
    if rng.random() < 0.3:
        body = body.lower()
    body = typo(body, rng, typo_p)
    return body, urgency


def build(n, seed, which, typo_p):
    rng = random.Random(seed)
    rows = []
    per = n // len(CORE)
    for issue, tpls in CORE.items():
        seen, held = tpls[:-HELD_OUT], tpls[-HELD_OUT:]
        for _ in range(per):
            if which == "train":
                pool = seen
            else:  # eval: half seen, half held-out
                pool = held if rng.random() < 0.5 else seen
            text, urg = make_ticket(rng, issue, pool, typo_p)
            rows.append({"text": text, "issue_type": issue, "urgency": urg})
    rng.shuffle(rows)
    return rows


HARD = [
    ("I was charged twice and now I also cannot log in to see the invoice, please fix both.", "billing", "medium"),
    ("Is it normal that your app asks for my password again and again? Looks suspicious to me.", "security", "high"),
    ("The export button is gone. Was it removed or is it a bug?", "technical", "medium"),
    ("Not urgent but our entire production environment has been down since 9am.", "technical", "critical"),
    ("hi", "general_inquiry", "low"),
    ("Do you plan to add refunds to the mobile app? I have asked for a refund of my payment too.", "billing", "medium"),
    ("Why am I seeing someone else's name on my dashboard? Customer data might be leaking.", "security", "critical"),
    ("Just wondering whether it is possible to enable 2FA for all team members.", "general_inquiry", "low"),
    ("The new update broke login for all our staff and we cannot open the shop.", "account_access", "critical"),
    ("I would like a feature to download my invoices in bulk because the billing page is too slow.", "feature_request", "low"),
    ("Thanks for the quick help last time! Quick question: do you offer annual billing?", "general_inquiry", "low"),
    ("URGENT!!! please reply ASAP!!! my account", "account_access", "high"),
    ("someone changed my password and my email, I did not do this", "security", "high"),
    ("Can't sync files and the app says my subscription expired although I paid yesterday.", "billing", "high"),
    ("The reports page times out. We have an audit tomorrow and need the numbers today.", "technical", "high"),
    ("Please add more payment options like UPI. It would make renewals easier.", "feature_request", "low"),
    ("My card was declined but the money left my account, can you check, no rush.", "billing", "low"),
    ("Where do I report a bug that lets anyone read other users' files?", "security", "critical"),
    ("Not able to access", "account_access", "medium"),
    ("Our admin left the company and we need to transfer ownership of the workspace.", "account_access", "medium"),
]


def write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["text", "issue_type", "urgency"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows):4d} rows -> {path.name}")


if __name__ == "__main__":
    DATA.mkdir(exist_ok=True)
    write(DATA / "train.csv", build(900, seed=42, which="train", typo_p=0.01))
    write(DATA / "eval.csv", build(300, seed=7, which="eval", typo_p=0.02))
    write(DATA / "hard_cases.csv", [{"text": t, "issue_type": i, "urgency": u} for t, i, u in HARD])
