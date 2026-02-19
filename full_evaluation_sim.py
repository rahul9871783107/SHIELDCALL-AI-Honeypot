"""
SHIELDCALL Full Evaluator Simulation
Mirrors the GUVI evaluation: 15 scenarios × 10 turns = 150 calls.
Each scenario plants intelligence across turns and scores extraction.
"""
import requests
import time
import json
import sys
import io
import uuid

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BASE_URL = "https://reasonable-balance-production.up.railway.app/api/honeypot"
API_KEY = "hackathon-secret-key-2026"
HEADERS = {"Content-Type": "application/json", "x-api-key": API_KEY}

# ── 15 SCENARIOS ──────────────────────────────────────────────────────────────
# Each has 10 scammer turns + planted intelligence to verify extraction.
SCENARIOS = [
    # ── 1. BANK FRAUD ────────────────────────────────────────────────────────
    {
        "id": "bank_fraud",
        "type": "Bank Fraud",
        "channel": "SMS",
        "planted": {
            "phone": "9876543210",
            "upi": "sbi.verify@fakebank",
            "bank": "1234567890123456",
            "url": "https://sbi-secure-verify.fake.in/auth",
            "email": "verify@sbi-fraud-dept.com",
        },
        "turns": [
            "URGENT: Your SBI account has been compromised. Suspicious activity detected. Your account will be blocked in 2 hours if not verified immediately!",
            "I am Senior Officer Rajesh Sharma from SBI Fraud Prevention Department, Employee ID SBI-4521. We have detected unauthorized transactions on your account.",
            "For identity verification, I need to confirm your details. You can also call our dedicated helpline at +91-9876543210 for assistance.",
            "To verify your account ownership, please transfer Re 1 to our verification UPI: sbi.verify@fakebank. This is standard SBI protocol.",
            "If UPI is not working, you can transfer to our verification account number 1234567890123456. This is a secure RBI-registered account.",
            "For faster processing, please visit our secure verification portal: https://sbi-secure-verify.fake.in/auth and complete the form.",
            "You can also email your Aadhaar and PAN copies to verify@sbi-fraud-dept.com. Our team will process immediately.",
            "TIME IS RUNNING OUT! Your account will be permanently blocked in 30 minutes! You will lose all your savings! ACT NOW!",
            "I see the transfer hasn't come through yet. Let me give you an alternate UPI: fraud.dept@oksbi. Please use this immediately.",
            "This is your FINAL WARNING. Call +91 98765 43210 RIGHT NOW or your account with balance Rs 2,47,000 will be frozen permanently!",
        ],
    },
    # ── 2. UPI FRAUD ─────────────────────────────────────────────────────────
    {
        "id": "upi_fraud",
        "type": "UPI Fraud",
        "channel": "WhatsApp",
        "planted": {
            "phone": "8765432109",
            "upi": "cashback.claim@paytm",
            "bank": "9876012345678901",
            "url": "https://paytm-cashback-offer.fake.com/claim",
            "email": "support@paytm-offers-india.com",
        },
        "turns": [
            "Congratulations! You have been selected for Rs 5,000 Paytm cashback reward! This is an exclusive offer for premium users only!",
            "I am Priya from Paytm Customer Rewards Division. Your Paytm ID was randomly selected from 10 lakh users. Call me at +91-8765432109.",
            "To claim your cashback, send Rs 99 processing fee to our verified UPI: cashback.claim@paytm. The Rs 5000 will be credited within 5 minutes!",
            "If you face UPI issues, you can transfer the processing fee to bank account 9876012345678901. NEFT/RTGS both accepted.",
            "You can also claim online at https://paytm-cashback-offer.fake.com/claim — just enter your details and get instant credit!",
            "For queries, email support@paytm-offers-india.com. But please hurry, this offer expires in 15 minutes!",
            "Kya hua? Abhi tak claim nahi kiya? Jaldi karo, sirf 10 minute bache hain! Rs 5000 ka cashback miss ho jayega!",
            "Maine aapka cashback hold par rakh diya hai. Abhi Rs 99 bhejo cashback.claim@paytm par. Main wait kar rahi hun.",
            "Aap mujhe call bhi kar sakte ho +91 87654 32109 par. Main aapko step by step guide karungi.",
            "LAST CHANCE! Offer expire ho raha hai! Send money NOW or you lose Rs 5000 forever!",
        ],
    },
    # ── 3. PHISHING LINK ─────────────────────────────────────────────────────
    {
        "id": "phishing_link",
        "type": "Phishing Link",
        "channel": "Email",
        "planted": {
            "phone": "7654321098",
            "upi": "deals@flipkart-offers",
            "bank": "5678901234567890",
            "url": "https://iphone15-flash-sale.tk/order",
            "email": "orders@flipkart-exclusive.com",
        },
        "turns": [
            "FLASH SALE: iPhone 15 at just Rs 999! Limited stock — only 50 units left! Grab yours before it's gone!",
            "This is an official Flipkart Diwali Flash Sale. I am Amit from Flipkart Deals team. Contact +91-7654321098 for order status.",
            "Click here to place your order: https://iphone15-flash-sale.tk/order — Select your color and size. Payment on next page.",
            "You can pay via UPI: deals@flipkart-offers. Send Rs 999 and your iPhone 15 will be shipped within 24 hours!",
            "If UPI doesn't work, use bank transfer to account 5678901234567890. We accept all banks.",
            "For order confirmation, email orders@flipkart-exclusive.com with your shipping address and phone number.",
            "HURRY! Only 12 units left now! This is the lowest price ever for iPhone 15! Don't miss this once-in-a-lifetime deal!",
            "Your order is reserved for 5 more minutes. After that, it goes to the next person in queue.",
            "I've extended your reservation. But this is the LAST extension. Pay Rs 999 to deals@flipkart-offers NOW.",
            "Offer closed for new users. Since you started, I can still hold yours. Call +91 76543 21098 to complete payment.",
        ],
    },
    # ── 4. KYC FRAUD ─────────────────────────────────────────────────────────
    {
        "id": "kyc_fraud",
        "type": "KYC Fraud",
        "channel": "SMS",
        "planted": {
            "phone": "6543210987",
            "upi": "kyc.update@mobikwik",
            "bank": "3456789012345678",
            "url": "www.paytm-kyc-update.fake.in/verify",
            "email": "kyc@wallet-verification.com",
        },
        "turns": [
            "ALERT: Your Paytm wallet KYC has expired! Your wallet will be permanently blocked within 24 hours. Update KYC immediately!",
            "This is an automated message from Paytm KYC Verification Center. For immediate assistance, call our KYC helpline: +91-6543210987.",
            "Apni KYC update karne ke liye www.paytm-kyc-update.fake.in/verify par jaiye. Aadhaar aur PAN details required hain.",
            "KYC verification fee of Rs 50 hai. Pay through UPI: kyc.update@mobikwik. Ye one-time charge hai, refundable hai.",
            "Agar UPI nahi chal raha, toh bank transfer kar do: account number 3456789012345678, IFSC: PAYT0001234.",
            "Aap documents bhi email kar sakte ho: kyc@wallet-verification.com. Aadhaar front-back aur PAN photo chahiye.",
            "Aapka wallet balance Rs 12,450 hai. Agar KYC expire ho gaya toh ye sab paisa freeze ho jayega! Jaldi karo!",
            "Maine aapki file escalate kar di hai. Abhi 1 ghanta hai. Uske baad wallet permanently block ho jayega.",
            "Kya hua? Abhi tak kyc update nahi kiya? Call karo +91 65432 10987 par, main abhi help karunga!",
            "FINAL NOTICE: KYC update deadline passed. Transfer Rs 50 to kyc.update@mobikwik in next 10 minutes or wallet blocked FOREVER.",
        ],
    },
    # ── 5. JOB SCAM ──────────────────────────────────────────────────────────
    {
        "id": "job_scam",
        "type": "Job Scam",
        "channel": "WhatsApp",
        "planted": {
            "phone": "9012345678",
            "upi": "amazon.jobs@ybl",
            "bank": "4567890123456789",
            "url": "https://amazon-wfh-careers.fake.com/apply",
            "email": "hr@amazon-jobs-india.com",
        },
        "turns": [
            "Hi! You have been selected for Amazon Work From Home job! Salary Rs 50,000/month. No experience needed. Part time allowed!",
            "I am Neha Singh, HR Manager at Amazon India. Contact me at +91-9012345678. Your application ID is AMZ-2025-7891.",
            "To secure your position, complete registration at https://amazon-wfh-careers.fake.com/apply. Only 20 seats remaining!",
            "Registration fee is Rs 2,000 only. Pay through UPI: amazon.jobs@ybl. This covers training materials and ID card.",
            "Bank transfer also accepted: Account 4567890123456789. After payment, you start earning from Day 1!",
            "Send your resume and Aadhaar to hr@amazon-jobs-india.com. We need to create your employee profile.",
            "Many candidates joined last week. Ravi from Pune is already earning Rs 45,000! Don't miss this opportunity!",
            "SEATS FILLING FAST! Only 5 positions left! Pay now or lose your spot to someone else!",
            "I've held your seat for 30 more minutes. After that someone else gets it. Pay Rs 2000 to amazon.jobs@ybl ASAP.",
            "Last call: Pay registration fee now. Your job offer expires at midnight. Call +91 90123 45678 if you have questions.",
        ],
    },
    # ── 6. LOTTERY SCAM ──────────────────────────────────────────────────────
    {
        "id": "lottery_scam",
        "type": "Lottery Scam",
        "channel": "SMS",
        "planted": {
            "phone": "8901234567",
            "upi": "lottery.claim@axisbank",
            "bank": "5678012345678901",
            "url": "https://kbc-lottery-winner.fake.in/claim",
            "email": "winner@kbc-lottery-official.com",
        },
        "turns": [
            "CONGRATULATIONS! You have won Rs 25,00,000 in KBC Season 15 Lucky Draw! Your ticket number KBC-2025-88432 has been selected!",
            "I am Director Arun Kapoor from KBC Prize Distribution. Contact my office at +91-8901234567 to begin claim process.",
            "To claim your prize, visit https://kbc-lottery-winner.fake.in/claim and enter your ticket number for verification.",
            "Processing fee of Rs 10,000 required. Transfer to UPI: lottery.claim@axisbank. This is mandatory per RBI guidelines.",
            "You can also transfer to our official account: 5678012345678901. This is KBC's registered bank account with Axis Bank.",
            "Email your ID proof and address to winner@kbc-lottery-official.com. We will dispatch the cheque within 48 hours.",
            "Aapne sach mein 25 lakh jeete hain! Ye koi fraud nahi hai! Main personally guarantee karta hun. Bas processing fee bhej do!",
            "Prize amount expire ho jayega 24 hours mein. RBI rules ke according, unclaimed prize government ko chala jayega!",
            "Maine aapki prize amount hold karwa li hai. Lekin zyada der nahi kar sakte. Bhejo Rs 10,000 lottery.claim@axisbank par.",
            "AAKHRI MAUKA! Call karo +91 89012 34567 abhi! Ya apna 25 lakh hamesha ke liye kho do!",
        ],
    },
    # ── 7. ELECTRICITY BILL ──────────────────────────────────────────────────
    {
        "id": "electricity_bill",
        "type": "Electricity Bill",
        "channel": "SMS",
        "planted": {
            "phone": "7890123456",
            "upi": "ebill.pay@bsesdelhi",
            "bank": "6789012345678901",
            "url": "https://bses-bill-payment.fake.in/pay",
            "email": "billing@bses-electricity-dept.com",
        },
        "turns": [
            "MSEB ALERT: Your electricity bill of Rs 8,432 is overdue! Connection will be DISCONNECTED today at 6 PM if not paid immediately!",
            "This is automated notice from BSES Delhi. For payment assistance call +91-7890123456. Consumer ID: BSES-2025-44567.",
            "Pay online at https://bses-bill-payment.fake.in/pay. Enter your consumer number to see outstanding amount.",
            "Quick payment via UPI: ebill.pay@bsesdelhi. Amount: Rs 8,432. Your connection will be restored within 30 minutes of payment.",
            "Bank transfer option: Account 6789012345678901. Add consumer ID in remarks. NEFT/RTGS accepted.",
            "Email your payment receipt to billing@bses-electricity-dept.com for faster reconnection.",
            "WARNING: Disconnection team already dispatched to your area! They will reach in 45 minutes!",
            "Your neighbor's connection was cut yesterday for non-payment. Don't let the same happen to you!",
            "Send money NOW. Your fridge, AC, fan — everything will stop. Think about your family!",
            "LAST 15 MINUTES! Pay Rs 8432 to ebill.pay@bsesdelhi or call +91 78901 23456. After this, reconnection fee is Rs 5000 extra!",
        ],
    },
    # ── 8. GOVT SCHEME ───────────────────────────────────────────────────────
    {
        "id": "govt_scheme",
        "type": "Govt Scheme",
        "channel": "WhatsApp",
        "planted": {
            "phone": "6789012345",
            "upi": "pm.yojana@sbi",
            "bank": "7890123456789012",
            "url": "https://pm-awas-yojana-subsidy.fake.in/register",
            "email": "register@pm-yojana-official.gov.fake.com",
        },
        "turns": [
            "PM Awas Yojana: Aapko Rs 2,50,000 ka housing subsidy approved ho gaya hai! Ye Modi sarkar ki special scheme hai!",
            "Main Suresh Kumar hun, PM Awas Yojana District Coordinator. Mere office number +91-6789012345 par contact karo.",
            "Registration ke liye https://pm-awas-yojana-subsidy.fake.in/register par jaiye. Aadhaar number daalna zaroori hai.",
            "Processing fee Rs 500 hai. UPI se bhejo: pm.yojana@sbi. Ye government authorized payment hai.",
            "Bank transfer bhi chalega: Account 7890123456789012. Ye SBI ka government scheme account hai.",
            "Documents email karo: register@pm-yojana-official.gov.fake.com. Aadhaar, ration card, aur income certificate chahiye.",
            "Bahut log apply kar rahe hain! Aapka slot reserved hai sirf 2 din ke liye. Jaldi karo!",
            "Mere paas aapki file hai. Sab approve ho gaya hai. Bas Rs 500 processing fee baki hai.",
            "Agar aaj nahi kiya toh next batch mein dalna padega. Tab 6 mahine lagenge. Abhi karo — +91 67890 12345 par call karo.",
            "DEADLINE AAKHRI DIN HAI! Rs 500 bhejo pm.yojana@sbi par ABHI ya apna Rs 2.5 lakh subsidy miss karo!",
        ],
    },
    # ── 9. CRYPTO INVESTMENT ─────────────────────────────────────────────────
    {
        "id": "crypto_investment",
        "type": "Crypto Investment",
        "channel": "WhatsApp",
        "planted": {
            "phone": "9123456780",
            "upi": "crypto.invest@kotak",
            "bank": "8901234567890123",
            "url": "https://bitcoin-guaranteed-returns.fake.com/invest",
            "email": "invest@crypto-wealth-india.com",
        },
        "turns": [
            "EXCLUSIVE: Bitcoin investment opportunity! Guaranteed 500% returns in 30 days! Minimum investment Rs 25,000 only!",
            "I am Vikram Malhotra, Senior Crypto Advisor at CryptoWealth India. Reach me at +91-9123456780. I have 10 years experience.",
            "See our platform: https://bitcoin-guaranteed-returns.fake.com/invest — Real-time dashboard shows live profits of our investors!",
            "Start investing via UPI: crypto.invest@kotak. Minimum Rs 25,000. Your profit starts compounding from Day 1!",
            "For large investments above Rs 1 lakh, use bank transfer: Account 8901234567890123. Lower fees, faster processing.",
            "Send your KYC documents to invest@crypto-wealth-india.com. PAN card mandatory for tax-free withdrawals.",
            "Our top investor Mr. Sharma invested Rs 50,000 and earned Rs 3,00,000 in just 2 months! You can be next!",
            "Market is going up RIGHT NOW! Every minute you wait, you lose potential profits! This is a LIMITED TIME opportunity!",
            "I have reserved a VIP slot for you. 500% guaranteed. But it expires tonight at midnight.",
            "Final call — invest Rs 25,000 to crypto.invest@kotak NOW. Or call me at +91 91234 56780. Don't regret later!",
        ],
    },
    # ── 10. CUSTOMS PARCEL ───────────────────────────────────────────────────
    {
        "id": "customs_parcel",
        "type": "Customs Parcel",
        "channel": "SMS",
        "planted": {
            "phone": "8234567890",
            "upi": "customs.duty@icici",
            "bank": "9012345678901234",
            "url": "https://india-customs-clearance.fake.in/pay",
            "email": "clearance@customs-india-govt.com",
        },
        "turns": [
            "INDIA CUSTOMS: Your international parcel (Tracking: ICP-2025-99234) is being held at Mumbai airport. Customs duty pending.",
            "I am Officer Mehra from Indian Customs Department. Contact +91-8234567890 for clearance assistance. Badge ID: CUS-7712.",
            "Pay customs duty of Rs 3,500 online at https://india-customs-clearance.fake.in/pay. Enter tracking number for details.",
            "Quick payment through UPI: customs.duty@icici. Amount Rs 3,500. Parcel will be dispatched same day after payment.",
            "If UPI is not available, use bank transfer: Account 9012345678901234. This is the official customs clearance account.",
            "Email your passport copy and address proof to clearance@customs-india-govt.com for faster processing.",
            "Your parcel contains valuable items worth Rs 45,000. If not cleared in 48 hours, it will be sent back to origin country!",
            "Aapka parcel 36 hours se hold mein hai. Kal tak nahi kiya toh destroy kar denge as per customs rules!",
            "I am extending deadline by 6 hours as courtesy. Pay Rs 3500 to customs.duty@icici RIGHT NOW.",
            "LAST EXTENSION EXPIRED. Call +91 82345 67890 in next 30 minutes or your parcel worth Rs 45,000 is gone forever!",
        ],
    },
    # ── 11. TECH SUPPORT ─────────────────────────────────────────────────────
    {
        "id": "tech_support",
        "type": "Tech Support",
        "channel": "Email",
        "planted": {
            "phone": "7345678901",
            "upi": "ms.support@paytm",
            "bank": "2345678901234567",
            "url": "www.microsoft-support-fix.ga/download",
            "email": "support@microsoft-helpdesk-india.com",
        },
        "turns": [
            "MICROSOFT SECURITY ALERT: Virus detected on your computer! Your personal data including banking passwords are at risk!",
            "I am John from Microsoft Technical Support Center, India. Call me immediately at +91-7345678901. Case ID: MS-VIRUS-2025-8834.",
            "Download our security patch from www.microsoft-support-fix.ga/download to remove the virus. This is urgent!",
            "For premium antivirus protection (lifetime), pay Rs 4,999 via UPI: ms.support@paytm. We will remotely fix your computer.",
            "You can also pay by bank transfer: Account 2345678901234567. After payment, our technician will connect to your PC.",
            "Send your computer details to support@microsoft-helpdesk-india.com. Include your Windows product key for verification.",
            "The virus is spreading to your other devices! Your phone, tablet — everything connected to same WiFi is at risk!",
            "We have blocked 47 unauthorized access attempts on your computer in the last hour alone! This is very serious!",
            "Pay the security fee NOW. UPI: ms.support@paytm. Our technician is standing by to fix your computer in 10 minutes.",
            "If you don't act in next 20 minutes, your computer will be permanently damaged! Call +91 73456 78901 IMMEDIATELY!",
        ],
    },
    # ── 12. LOAN APPROVAL ────────────────────────────────────────────────────
    {
        "id": "loan_approval",
        "type": "Loan Approval",
        "channel": "SMS",
        "planted": {
            "phone": "6456789012",
            "upi": "loan.process@hdfc",
            "bank": "3456012345678901",
            "url": "https://hdfc-instant-loan.fake.in/apply",
            "email": "loans@hdfc-quickloan-india.com",
        },
        "turns": [
            "HDFC Pre-Approved Personal Loan: Rs 10,00,000 at 0% interest for first 6 months! Instant disbursal! Apply now!",
            "Main Rahul Verma hun, HDFC Loan Department se. Aapka CIBIL score excellent hai! Call me: +91-6456789012.",
            "Apply online: https://hdfc-instant-loan.fake.in/apply. Loan amount seedha aapke account mein credit hoga within 2 hours!",
            "Processing fee Rs 1,999 hai. Pay via UPI: loan.process@hdfc. Ye ek baar ka charge hai, loan mein adjust ho jayega.",
            "Bank transfer bhi kar sakte ho: Account 3456012345678901, IFSC: HDFC0004567. Mention your PAN in remarks.",
            "Documents email karo: loans@hdfc-quickloan-india.com. PAN, Aadhaar, aur last 3 months salary slip chahiye.",
            "Aapke jaisi profile ke log usually Rs 15-20 lakh tak eligible hote hain. Bas processing fee pending hai.",
            "Offer sirf aaj ke liye hai! Interest rate kal se 12% ho jayega. Aaj 0% hai! Sochiye mat, karo!",
            "Maine aapka loan file ready kar diya hai. Approval letter bhi ban gaya. Bas Rs 1999 bhejo loan.process@hdfc par.",
            "LAST DAY of 0% interest offer! Call +91 64567 89012 or pay now. After today, this deal is GONE!",
        ],
    },
    # ── 13. INCOME TAX ───────────────────────────────────────────────────────
    {
        "id": "income_tax",
        "type": "Income Tax",
        "channel": "Email",
        "planted": {
            "phone": "9567890123",
            "upi": "itrefund.verify@sbi",
            "bank": "4567012345678901",
            "url": "https://incometax-refund-verify.fake.in/claim",
            "email": "refund@income-tax-india-gov.com",
        },
        "turns": [
            "Income Tax Department: Your tax refund of Rs 45,000 for AY 2024-25 has been approved. Verify bank details to receive credit.",
            "I am Assistant Commissioner Deepak Nair, IT Department Bangalore. My direct line: +91-9567890123. File No: IT-REF-2025-55678.",
            "Verify your bank account at https://incometax-refund-verify.fake.in/claim. Enter PAN and Aadhaar for verification.",
            "There is a verification fee of Rs 200. Pay via UPI: itrefund.verify@sbi. This is standard procedure for refunds above Rs 25,000.",
            "Your registered bank account for refund: 4567012345678901. Confirm this is correct, or update at the portal.",
            "Send your PAN card copy and Form 16 to refund@income-tax-india-gov.com. Required for compliance as per Section 143.",
            "Your refund has been pending for 45 days. If not claimed in 7 days, it will be forfeited as per IT Act Section 237.",
            "Multiple taxpayers have already received their refunds this week. Don't let yours expire!",
            "Aapke PAN se linked account verify nahi hua hai. Rs 200 bhejo itrefund.verify@sbi par for instant verification.",
            "URGENT: Last 24 hours to claim Rs 45,000 refund! Call +91 95678 90123 NOW or forfeit your money!",
        ],
    },
    # ── 14. REFUND SCAM ──────────────────────────────────────────────────────
    {
        "id": "refund_scam",
        "type": "Refund Scam",
        "channel": "SMS",
        "planted": {
            "phone": "8678901234",
            "upi": "refund.process@amazonpay",
            "bank": "5670123456789012",
            "url": "https://flipkart-refund-process.fake.in/verify",
            "email": "refunds@flipkart-support-india.com",
        },
        "turns": [
            "Flipkart: Your refund of Rs 2,999 for Order #FK-2025-88921 has failed due to incorrect bank details. Update now to receive your money!",
            "I am Ankita from Flipkart Customer Support. Your refund is stuck. Contact me at +91-8678901234 for immediate resolution.",
            "Update your bank details at https://flipkart-refund-process.fake.in/verify. Enter your order ID and new bank account.",
            "For instant refund, use UPI: refund.process@amazonpay. We will credit Rs 2,999 + Rs 500 compensation within 10 minutes!",
            "Alternatively, share your bank account number for direct NEFT transfer. Our system shows your old account as 5670123456789012 — is this correct?",
            "Email your updated bank passbook to refunds@flipkart-support-india.com. We need first page with account number and IFSC.",
            "Your refund window closes in 48 hours. After that, the Rs 2,999 goes back to the seller and you get nothing!",
            "I've escalated your case to senior management. They approved Rs 500 extra compensation. Total Rs 3,499 — just verify your details!",
            "Bahut customers ka refund process ho gaya. Bas aapka pending hai. Jaldi karo — UPI: refund.process@amazonpay",
            "FINAL REMINDER: Rs 3,499 refund expires tonight. Call +91 86789 01234 or lose your money! We can't extend anymore!",
        ],
    },
    # ── 15. INSURANCE ────────────────────────────────────────────────────────
    {
        "id": "insurance",
        "type": "Insurance",
        "channel": "SMS",
        "planted": {
            "phone": "7789012345",
            "upi": "lic.maturity@sbi",
            "bank": "6780123456789012",
            "url": "https://lic-maturity-claim.fake.in/process",
            "email": "claims@lic-maturity-office.com",
        },
        "turns": [
            "LIC India: Your policy #LIC-2025-445567 maturity amount of Rs 8,50,000 is ready for disbursement! Claim within 7 days!",
            "I am Manager Sunil Mehta from LIC Divisional Office, Mumbai. Contact my direct number (91) 7789012345 for claim processing.",
            "Complete claim form at https://lic-maturity-claim.fake.in/process. Upload policy document and nominee ID proof.",
            "Stamp duty of Rs 5,000 must be paid via UPI: lic.maturity@sbi. This is mandatory for maturity claims above Rs 5 lakh.",
            "Stamp duty can also be paid to account 6780123456789012. Mention your policy number in payment remarks.",
            "Email your claim documents to claims@lic-maturity-office.com — policy bond, ID proof, cancelled cheque.",
            "LIC policy maturity claims must be settled within 7 days as per IRDAI guidelines. Only 4 days remaining for yours!",
            "Rs 8,50,000 is a big amount. Many people don't claim on time and lose it. Don't be one of them!",
            "Aapke agent ne bhi confirm kiya hai. Sab kuch ready hai. Bas Rs 5000 stamp duty bhejo lic.maturity@sbi par.",
            "LAST DAY to claim! After today your Rs 8.5 lakh goes to unclaimed fund! Call +91 77890 12345 RIGHT NOW!",
        ],
    },
]


def compute_score(scenario, all_responses):
    """Compute evaluation score for a scenario."""
    planted = scenario["planted"]
    score = {"detection": 0, "extraction": 0, "engagement": 0, "structure": 0}
    extraction_detail = {"phone": False, "upi": False, "bank": False, "url": False, "email": False}

    last_resp = all_responses[-1] if all_responses else {}

    # ── Detection (20 pts) ──
    if last_resp.get("scamDetected") is True:
        score["detection"] = 20

    # ── Intelligence Extraction (40 pts) ──
    # Combine intelligence from ALL responses (evaluator checks cumulative)
    all_phones = set()
    all_upis = set()
    all_banks = set()
    all_urls = set()
    all_emails = set()
    for resp in all_responses:
        intel = resp.get("extractedIntelligence", {})
        all_phones.update(intel.get("phoneNumbers", []))
        all_upis.update(intel.get("upiIds", []))
        all_banks.update(intel.get("bankAccounts", []))
        all_urls.update(intel.get("phishingLinks", []))
        all_emails.update(intel.get("emailAddresses", []))

    # Phone: check if planted phone is in extracted (substring match)
    for p in all_phones:
        if planted["phone"] in p or p in planted["phone"]:
            extraction_detail["phone"] = True
            break
    # UPI: case-insensitive substring
    for u in all_upis:
        if planted["upi"].lower() in u.lower() or u.lower() in planted["upi"].lower():
            extraction_detail["upi"] = True
            break
    # Bank: digits only
    planted_bank_digits = "".join(c for c in planted["bank"] if c.isdigit())
    for b in all_banks:
        b_digits = "".join(c for c in b if c.isdigit())
        if planted_bank_digits in b_digits or b_digits in planted_bank_digits:
            extraction_detail["bank"] = True
            break
    # URL: substring match
    for u in all_urls:
        # Check if the planted URL domain is in extracted, or vice versa
        planted_domain = planted["url"].replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
        u_clean = u.replace("https://", "").replace("http://", "").replace("www.", "")
        if planted_domain in u_clean or u_clean.startswith(planted_domain):
            extraction_detail["url"] = True
            break
    # Email: case-insensitive match
    for e in all_emails:
        if planted["email"].lower() == e.lower():
            extraction_detail["email"] = True
            break

    score["extraction"] += 10 if extraction_detail["phone"] else 0
    score["extraction"] += 10 if extraction_detail["bank"] else 0
    score["extraction"] += 10 if extraction_detail["upi"] else 0
    score["extraction"] += 10 if extraction_detail["url"] else 0

    # ── Engagement Quality (20 pts) ──
    metrics = last_resp.get("engagementMetrics", {})
    duration = metrics.get("engagementDurationSeconds", 0)
    msg_count = metrics.get("totalMessagesExchanged", 0)

    if duration > 0:
        score["engagement"] += 5
    if duration > 60:
        score["engagement"] += 5
    if msg_count > 0:
        score["engagement"] += 5
    if msg_count >= 5:
        score["engagement"] += 5

    # ── Response Structure (20 pts) ──
    if "status" in last_resp:
        score["structure"] += 5
    if "scamDetected" in last_resp:
        score["structure"] += 5
    if "extractedIntelligence" in last_resp:
        score["structure"] += 5
    if "engagementMetrics" in last_resp:
        score["structure"] += 2.5
    if "agentNotes" in last_resp:
        score["structure"] += 2.5

    return score, extraction_detail


def run_full_simulation():
    total_start = time.time()
    all_scenario_results = []

    for s_idx, scenario in enumerate(SCENARIOS):
        session_id = str(uuid.uuid4())
        conversation_history = []
        scenario_responses = []
        scenario_times = []
        scenario_models = []
        errors = 0

        print(f"\n{'='*70}")
        print(f"SCENARIO {s_idx+1}/15: {scenario['type']} [{scenario['id']}]")
        print(f"Session: {session_id}")
        print(f"{'='*70}")

        base_epoch = 1707640200000  # Feb 11, 2025 10:30 AM IST in ms

        for turn_idx, scammer_msg in enumerate(scenario["turns"]):
            turn_num = turn_idx + 1
            timestamp_ms = base_epoch + (turn_idx * 60000)  # 1 minute apart

            payload = {
                "sessionId": session_id,
                "message": {
                    "sender": "scammer",
                    "text": scammer_msg,
                    "timestamp": timestamp_ms,
                },
                "conversationHistory": conversation_history.copy(),
                "metadata": {
                    "channel": scenario["channel"],
                    "language": "English",
                    "locale": "IN",
                },
            }

            turn_start = time.time()
            try:
                resp = requests.post(BASE_URL, json=payload, headers=HEADERS, timeout=30)
                turn_time = time.time() - turn_start
                scenario_times.append(turn_time)

                if resp.status_code == 200:
                    data = resp.json()
                    reply = data.get("reply", "")
                    notes = data.get("agentNotes", "")
                    model = "gemini" if "gemini" in notes.lower() else "haiku"
                    scenario_models.append(model)
                    scenario_responses.append(data)

                    intel = data.get("extractedIntelligence", {})
                    intel_count = sum(len(v) for k, v in intel.items() if k != "suspiciousKeywords")

                    print(f"  Turn {turn_num:2d}: {turn_time:.1f}s | {model:6s} | intel={intel_count} | {reply[:55]}...")

                    # Build history for next turn
                    conversation_history.append({
                        "sender": "scammer",
                        "text": scammer_msg,
                        "timestamp": timestamp_ms,
                    })
                    conversation_history.append({
                        "sender": "user",
                        "text": reply,
                        "timestamp": timestamp_ms + 5000,  # 5s later
                    })
                else:
                    turn_time = time.time() - turn_start
                    scenario_times.append(turn_time)
                    scenario_models.append("error")
                    errors += 1
                    print(f"  Turn {turn_num:2d}: ERROR {resp.status_code} in {turn_time:.1f}s")
                    scenario_responses.append({})

            except Exception as e:
                turn_time = time.time() - turn_start
                scenario_times.append(turn_time)
                scenario_models.append("error")
                errors += 1
                print(f"  Turn {turn_num:2d}: EXCEPTION {str(e)[:50]} in {turn_time:.1f}s")
                scenario_responses.append({})

        # Score this scenario
        score, extraction = compute_score(scenario, scenario_responses)
        total_score = score["detection"] + score["extraction"] + score["engagement"] + score["structure"]

        all_scenario_results.append({
            "scenario": scenario,
            "score": score,
            "total_score": total_score,
            "extraction": extraction,
            "times": scenario_times,
            "models": scenario_models,
            "errors": errors,
            "responses": scenario_responses,
        })

        # Print scenario score summary
        print(f"\n  SCORE: {total_score:.0f}/100")
        print(f"    Detection:  {score['detection']}/20")
        print(f"    Extraction: {score['extraction']}/40  "
              f"[phone={'Y' if extraction['phone'] else 'N'} "
              f"upi={'Y' if extraction['upi'] else 'N'} "
              f"bank={'Y' if extraction['bank'] else 'N'} "
              f"url={'Y' if extraction['url'] else 'N'} "
              f"email={'Y' if extraction['email'] else 'N'}]")
        print(f"    Engagement: {score['engagement']}/20")
        print(f"    Structure:  {score['structure']}/20")
        print(f"    Avg time:   {sum(scenario_times)/len(scenario_times):.2f}s")
        gemini_pct = scenario_models.count("gemini") / len(scenario_models) * 100
        print(f"    Models:     Gemini {scenario_models.count('gemini')}/10 ({gemini_pct:.0f}%), Haiku {scenario_models.count('haiku')}/10")

    # ══════════════════════════════════════════════════════════════════════════
    # FINAL SUMMARY
    # ══════════════════════════════════════════════════════════════════════════
    total_time = time.time() - total_start
    all_times = []
    all_models = []
    total_points = 0
    max_points = len(SCENARIOS) * 100

    for r in all_scenario_results:
        all_times.extend(r["times"])
        all_models.extend(r["models"])
        total_points += r["total_score"]

    print(f"\n\n{'#'*70}")
    print(f"#  FULL EVALUATION SIMULATION REPORT")
    print(f"{'#'*70}")

    print(f"\n--- OVERALL SCORE ---")
    print(f"Total Score:  {total_points:.0f} / {max_points} ({total_points/max_points*100:.1f}%)")
    print(f"Average/scenario: {total_points/len(SCENARIOS):.1f}/100")

    print(f"\n--- TIMING ---")
    print(f"Total time:       {total_time:.1f}s ({total_time/60:.1f} minutes)")
    print(f"Avg per turn:     {sum(all_times)/len(all_times):.2f}s")
    print(f"Min turn:         {min(all_times):.2f}s")
    print(f"Max turn:         {max(all_times):.2f}s")

    print(f"\n--- MODEL DISTRIBUTION ---")
    gemini_total = all_models.count("gemini")
    haiku_total = all_models.count("haiku")
    error_total = all_models.count("error")
    print(f"Gemini 2.0 Flash: {gemini_total}/{len(all_models)} ({gemini_total/len(all_models)*100:.0f}%)")
    print(f"Claude Haiku:     {haiku_total}/{len(all_models)} ({haiku_total/len(all_models)*100:.0f}%)")
    if error_total:
        print(f"Errors:           {error_total}/{len(all_models)}")

    print(f"\n--- PER-SCENARIO SCORES ---")
    print(f"{'Scenario':<20} {'Total':>5} {'Det':>4} {'Ext':>4} {'Eng':>4} {'Str':>4}  {'Phone':>5} {'UPI':>4} {'Bank':>5} {'URL':>4} {'Email':>5}  {'Avg(s)':>6}")
    print("-" * 105)

    below_90 = []
    missed_items = []

    for r in all_scenario_results:
        s = r["score"]
        e = r["extraction"]
        sid = r["scenario"]["id"]
        t = sum(r["times"]) / len(r["times"])
        total = r["total_score"]

        print(f"{sid:<20} {total:5.0f} {s['detection']:4} {s['extraction']:4} {s['engagement']:4} {s['structure']:4.0f}  "
              f"{'Y' if e['phone'] else 'MISS':>5} {'Y' if e['upi'] else 'MISS':>4} {'Y' if e['bank'] else 'MISS':>5} "
              f"{'Y' if e['url'] else 'MISS':>4} {'Y' if e['email'] else 'MISS':>5}  {t:6.2f}")

        if total < 90:
            below_90.append((sid, total))
        for item_type in ["phone", "upi", "bank", "url", "email"]:
            if not e[item_type]:
                missed_items.append((sid, item_type, r["scenario"]["planted"][item_type]))

    print("-" * 105)

    if below_90:
        print(f"\n--- SCENARIOS BELOW 90 ---")
        for sid, total in below_90:
            print(f"  {sid}: {total:.0f}/100")
    else:
        print(f"\n  All scenarios scored 90+!")

    if missed_items:
        print(f"\n--- MISSED INTELLIGENCE ITEMS ---")
        for sid, itype, value in missed_items:
            print(f"  [{sid}] MISSED {itype}: {value}")
    else:
        print(f"\n  All intelligence items extracted!")

    print(f"\n--- FASTEST / SLOWEST ---")
    fastest = min(all_scenario_results, key=lambda r: sum(r["times"]))
    slowest = max(all_scenario_results, key=lambda r: sum(r["times"]))
    print(f"Fastest: {fastest['scenario']['id']} ({sum(fastest['times']):.1f}s total, {sum(fastest['times'])/10:.2f}s avg)")
    print(f"Slowest: {slowest['scenario']['id']} ({sum(slowest['times']):.1f}s total, {sum(slowest['times'])/10:.2f}s avg)")

    # ── VERDICT ──
    overall_pct = total_points / max_points * 100
    all_above_90 = len(below_90) == 0
    no_errors = error_total == 0
    fast_enough = total_time < 600  # under 10 minutes

    print(f"\n{'#'*70}")
    if overall_pct >= 85 and no_errors and fast_enough:
        print(f"#  VERDICT: READY FOR SUBMISSION")
        print(f"#  Score: {overall_pct:.1f}% | Time: {total_time/60:.1f}min | Errors: {error_total}")
    else:
        print(f"#  VERDICT: NEEDS FIXES")
        if overall_pct < 85:
            print(f"#  Score too low: {overall_pct:.1f}% (need 85%+)")
        if not no_errors:
            print(f"#  Errors detected: {error_total}")
        if not fast_enough:
            print(f"#  Too slow: {total_time/60:.1f}min (need <10min)")
    print(f"{'#'*70}")


if __name__ == "__main__":
    run_full_simulation()
