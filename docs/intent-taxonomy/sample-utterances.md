# Sample Utterance Library — NexBank NEXA

**Deliverable:** L2 (sample utterance library) · Parent: [`README.md`](README.md)

≥10 utterances per intent across the 32 domain intents (**320+ total**, exceeding the 250 minimum), mixing English, Hinglish, and code-switched forms to reflect the NexBank customer base. These seed NLU training/eval and the demo's lexical classifier. `[H]` marks Hinglish/code-switched examples.

---

## Account Management

**ACC-001 · account.balance.check**
1. What's my account balance?
2. Show me my savings balance please
3. How much money do I have in my account?
4. Check balance for my current account
5. Kitna balance hai mere account mein? `[H]`
6. Available balance batao `[H]`
7. Can you tell me my closing balance as of yesterday?
8. Balance enquiry
9. I want to see how much is left in savings
10. What is the available balance on account ending 4521?

**ACC-002 · account.statement.request**
1. I need my account statement
2. Send me last 3 months statement
3. Can I get a PDF statement for March?
4. Email me my statement please
5. Statement chahiye pichle mahine ka `[H]`
6. Download my transaction history for last 30 days
7. I want a statement between 1 Jan and 31 Mar
8. Mini statement please
9. Send account statement to my email
10. Give me my e-statement for the last quarter

**ACC-003 · account.profile.contact_update**
1. I want to change my registered mobile number
2. Update my email address
3. My phone number has changed
4. Change my contact details
5. Naya mobile number update karna hai `[H]`
6. Please update my registered email id
7. I got a new number, update it in your records
8. Modify my phone number on file
9. How do I change the email linked to my account?
10. Update contact info

**ACC-004 · account.profile.address_update**
1. I need to update my mailing address
2. Change my address in your records
3. I moved to a new house, update address
4. Update my communication address
5. Ghar ka address change karna hai `[H]`
6. My address is outdated, please fix it
7. Change permanent address
8. New address update karo `[H]`
9. Where do I submit address proof to change my address?
10. Update the address where you send my cards

**ACC-005 · account.lifecycle.closure**
1. I want to close my account
2. How do I shut down my savings account?
3. Please close my NexBank account
4. Account band karna hai `[H]`
5. I'd like to terminate my account
6. Close my account permanently
7. What's the process to close my account?
8. I no longer need this account, close it
9. Deactivate my account
10. Cancel my savings account

**ACC-006 · account.lifecycle.nominee_update**
1. I want to add a nominee
2. Change the nominee on my account
3. Update nominee details
4. Nominee add karna hai `[H]`
5. How do I register a nominee?
6. Replace my current nominee
7. Add my spouse as nominee
8. Update beneficiary for my account
9. I need to change who my nominee is
10. Register nominee for savings account

**ACC-007 · account.lifecycle.upgrade_downgrade**
1. Can I upgrade my account to premium?
2. I want to downgrade to a basic account
3. Change my account type
4. Upgrade to a salary account
5. Premium account mein upgrade karna hai `[H]`
6. What are the benefits of upgrading?
7. Move me to a zero-balance account
8. Switch my account tier
9. I want a better account plan
10. Downgrade my account, too many charges

---

## Transaction & Payment

**TXN-001 · transaction.status.enquiry**
1. Where is my transaction?
2. Status of my transfer to Rahul
3. Did my payment go through?
4. Check status of transaction TXN9F2A
5. Mera transaction complete hua ya nahi? `[H]`
6. Has the ₹5000 transfer been processed?
7. What happened to my payment from this morning?
8. Track my transaction
9. Is my NEFT done?
10. Payment status check karo `[H]`

**TXN-002 · transaction.dispute.\***
1. I see a charge I didn't make
2. There's a wrong debit on my account
3. I was charged twice for the same thing
4. Raise a dispute for this transaction
5. Ye ₹1500 ka charge galat hai `[H]`
6. I want to dispute a payment
7. The merchant charged me the wrong amount
8. Refund this incorrect charge
9. Duplicate charge on my card, please reverse
10. This transaction is incorrect, I need it disputed

**TXN-003 · transaction.upi.failure**
1. My UPI payment failed but money got deducted
2. UPI transaction failed
3. Paisa cut gaya but payment nahi hua `[H]`
4. My Google Pay transfer didn't reach the person
5. UPI payment stuck
6. Money debited, merchant says not received
7. Failed UPI but amount deducted, help
8. My PhonePe payment failed
9. UPI ref UPI123456789 failed, refund please
10. Payment ka paisa wapas kab aayega? `[H]`

**TXN-004 · transaction.neft_rtgs.status**
1. Check my NEFT status
2. Has my RTGS gone through?
3. Status of UTR number please
4. My NEFT to HDFC is pending
5. NEFT abhi tak nahi pahuncha `[H]`
6. When will my RTGS be credited?
7. Track NEFT transfer
8. Is my IMPS done?
9. RTGS status check karo `[H]`
10. My beneficiary hasn't received the NEFT

**TXN-005 · transaction.recurring.\***
1. Set up a monthly payment to my landlord
2. Cancel my recurring payment
3. Start an auto-pay for my SIP
4. Stop the standing instruction
5. Har mahine ka payment set karna hai `[H]`
6. Create a recurring transfer
7. Cancel my auto-debit
8. Modify my standing instruction amount
9. Set up autopay for electricity bill
10. Recurring payment band karo `[H]`

**TXN-006 · transaction.international.enquiry**
1. How do I send money abroad?
2. International transfer to USA
3. Can I transfer dollars to my son in Dubai?
4. What are the charges for a foreign remittance?
5. Bahar paisa kaise bhejun? `[H]`
6. Wire transfer to UK
7. Send money to a US bank account
8. Foreign currency transfer enquiry
9. Remittance to Singapore, how much fee?
10. International fund transfer process

---

## Card Management

**CRD-001 · card.control.{block|unblock}**
1. Block my debit card
2. I lost my card, block it now
3. Unblock my credit card
4. Freeze my card temporarily
5. Card block kar do jaldi `[H]`
6. My card is stolen, disable it
7. Please unblock my card, I found it
8. Temporarily block my card
9. Deactivate my debit card
10. Card ko unblock karna hai `[H]`

**CRD-002 · card.replacement**
1. I need a replacement card
2. My card is damaged, send a new one
3. Reissue my debit card
4. Naya card chahiye, purana kho gaya `[H]`
5. Replace my expired card
6. Get me a new credit card, mine broke
7. Order a replacement card
8. My card is not working, replace it
9. Send a fresh card to my address
10. I want a duplicate card

**CRD-003 · card.credit_limit.change**
1. Increase my credit card limit
2. Lower my credit limit
3. Can I get a higher limit?
4. Credit limit badhao `[H]`
5. Request a limit increase
6. Reduce my card limit please
7. What's my current credit limit and can I raise it?
8. Change my credit card limit
9. I want more spending limit on my card
10. Limit increase karna hai `[H]`

**CRD-004 · card.emi.conversion**
1. Convert my purchase to EMI
2. Can I pay this in installments?
3. EMI conversion for my ₹40000 purchase
4. Is transaction ko EMI mein convert karo `[H]`
5. Break my credit card bill into EMIs
6. Convert last transaction to 6-month EMI
7. I want to pay my bill in parts
8. EMI option for my TV purchase
9. Split this payment into monthly EMIs
10. Kitne mahine ka EMI ho sakta hai? `[H]`

**CRD-005 · card.rewards.enquiry**
1. How many reward points do I have?
2. Check my cashback balance
3. Reward points kitne hain? `[H]`
4. How do I redeem my points?
5. What's my rewards balance?
6. Show my credit card points
7. Can I convert points to cash?
8. Reward points redeem kaise karun? `[H]`
9. When do my points expire?
10. Points balance enquiry

---

## Product & Advisory

**PRD-001 · product.info**
1. Tell me about your credit cards
2. What are the features of NexSave account?
3. Details of your home loan
4. NexFD ke baare mein batao `[H]`
5. What fees does the premium card have?
6. Explain your savings account benefits
7. What documents do I need for a home loan?
8. Information about NexProtect insurance
9. What's the interest-free period on your card?
10. Product details for NexGold

**PRD-002 · product.loan.eligibility**
1. Am I eligible for a home loan?
2. What's the maximum personal loan I can get?
3. Loan eligibility check
4. Kitna loan mil sakta hai mujhe? `[H]`
5. Do I qualify for a car loan?
6. What CIBIL score do I need for a home loan?
7. Check my loan eligibility
8. Can I get a 20 lakh home loan?
9. Eligibility criteria for personal loan
10. Home loan ke liye eligible hun kya? `[H]`

**PRD-003 · product.deposit.rates**
1. What are your current FD rates?
2. Fixed deposit interest for 1 year
3. FD ka rate kya hai? `[H]`
4. Recurring deposit rates please
5. Best FD tenure for highest rate?
6. What interest do I get on a 2-year FD?
7. Show me deposit rates
8. Senior citizen FD rate
9. RD interest rate batao `[H]`
10. Current fixed deposit rates for 5 years

**PRD-004 · product.insurance.info**
1. Tell me about your term insurance
2. What does NexProtect cover?
3. Insurance ke baare mein jaankari do `[H]`
4. Maximum cover on your term plan?
5. Do you offer health insurance?
6. Premium for 1 crore term cover?
7. What is the claim process for insurance?
8. Life insurance options
9. Term insurance details chahiye `[H]`
10. Is medical check needed for insurance?

**PRD-005 · product.investment.advisory** *(information-only; routes to advisor)*
1. Should I invest in FD or mutual funds?
2. Which investment is best for me?
3. Mujhe kahan invest karna chahiye? `[H]`
4. Is now a good time to buy gold?
5. Recommend a good mutual fund for me
6. What should I do with my 5 lakhs?
7. Best plan for retirement at 50?
8. Kaunsa MF lena chahiye mere liye? `[H]`
9. Advise me on where to put my savings
10. Which is better for me, equity or debt funds?

---

## Complaint & Feedback

**CMP-001 · complaint.register**
1. I want to file a complaint
2. Register a complaint about my card
3. Complaint darj karni hai `[H]`
4. I have an issue I want on record
5. Log a complaint against a wrong charge
6. I need to raise a formal complaint
7. File grievance for failed transaction
8. Meri shikayat likho `[H]`
9. I want to report a problem with your service
10. Register issue: ATM didn't dispense cash

**CMP-002 · complaint.status**
1. What's the status of my complaint?
2. Check complaint CMP-2024-78901
3. Meri complaint ka kya hua? `[H]`
4. Any update on my grievance?
5. Status of my earlier complaint
6. Has my complaint been resolved?
7. Track my complaint
8. Complaint status batao `[H]`
9. Where does my complaint stand?
10. Update on ticket CMP-2024-79012

**CMP-003 · complaint.escalate**
1. I want to escalate my complaint
2. This has been pending for weeks, escalate it
3. My issue is still not resolved, take it higher
4. Complaint escalate karo `[H]`
5. I'm not satisfied, escalate to a manager
6. Raise the priority of my complaint
7. Nobody helped me, escalate this
8. Escalate CMP-2024-78901 please
9. This is taking too long, escalate
10. Bahut din ho gaye, ab escalate karo `[H]`

**CMP-004 · complaint.feedback**
1. I want to give feedback
2. Great service today, thank you
3. Feedback dena hai `[H]`
4. Your app is hard to use
5. Rate my experience as 5 stars
6. I have a suggestion for you
7. The wait time was too long
8. Achha laga aapki service `[H]`
9. I want to share my experience
10. Feedback: the agent was very helpful

**CMP-005 · complaint.callback_request**
1. Can someone call me back?
2. Request a supervisor callback
3. Mujhe call back chahiye `[H]`
4. Have a manager call me
5. I want a callback tomorrow morning
6. Please arrange a call from your team
7. Callback request for my issue
8. Supervisor se baat karni hai, call karwao `[H]`
9. Schedule a callback at 5pm
10. Ask someone to phone me about this

---

## Security & Fraud

**SEC-001 · security.fraud.report**
1. Someone made transactions I didn't authorise
2. My account is hacked
3. There's fraud on my card
4. Mere account se fraud hua hai `[H]`
5. I think my card details are stolen
6. Unauthorised transactions on my account, help
7. Report fraud on my debit card
8. Someone withdrew money without my permission
9. Fraudulent charge of ₹15000, I never did this
10. Mera paisa kisi ne chura liya `[H]`

**SEC-002 · security.phishing.report**
1. I got a suspicious SMS asking for my OTP
2. Report a phishing email
3. Someone is pretending to be NexBank
4. Mujhe fake call aaya bank ke naam se `[H]`
5. I received a fraud link claiming to be you
6. A caller asked for my card details
7. Phishing message report karna hai `[H]`
8. Got a scam WhatsApp from "NexBank"
9. Someone tried to trick me into sharing my PIN
10. Report a fake NexBank website

**SEC-003 · security.credentials.reset**
1. Reset my internet banking password
2. I forgot my login password
3. Password reset karna hai `[H]`
4. Change my mobile banking PIN
5. Help me reset my credentials
6. I'm locked out of my account, reset access
7. Reset my UPI PIN
8. My login isn't working, reset password
9. Naya password set karna hai `[H]`
10. Recover my account access

**SEC-004 · security.suspicious.activity**
1. I got an alert about a login I don't recognise
2. Suspicious activity on my account
3. Was there a login from a new device?
4. Mere account mein kuch galat lag raha hai `[H]`
5. I see a login from another city
6. Unusual activity notification, is it real?
7. Someone tried to access my account
8. Check for suspicious logins on my account
9. Koi meri account access kar raha hai kya? `[H]`
10. I received an unexpected OTP I didn't request

---

## General / meta (flow control)

**GEN-001 greeting:** Hi · Hello · Namaste · Hey there · Good morning
**GEN-002 smalltalk:** How are you? · Are you a robot? · What can you do?
**GEN-003 human_agent_request:** I want to talk to a human · Connect me to an agent · Kisi insaan se baat karao `[H]`
**GEN-004 out_of_scope:** What's the weather? · Tell me a joke · Who won the match?
**GEN-005 thanks_closure:** Thank you · That's all · Dhanyavaad · No, that's everything

---

*Count: 32 domain intents × 10 = 320 utterances (+ general). Hinglish coverage embedded throughout for code-switching robustness.*
