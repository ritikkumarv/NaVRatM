"""Synthetic seed data — 52 demo applications with known fraud patterns."""

SEED_APPLICATIONS = [
    # ── Clean applications (low risk) ──
    {
        "id": "APP-001",
        "declared": {
            "full_name": "Rajesh Kumar Verma",
            "dob": "1988-05-12",
            "gender": "male",
            "address": "15, Shanti Nagar, Lucknow, Uttar Pradesh 226001",
            "aadhaar_masked": "XXXX-XXXX-4521",
            "pan_masked": "XXXXX2345X",
            "income_monthly": 9000.0,
            "bank_account_masked": "XXXXXXXXXX6789",
            "phone_masked": "XXXXXX7890",
            "scheme": "PM-KISAN",
            "state": "Uttar Pradesh",
            "district": "Lucknow",
        },
        "documents": [
            {
                "type": "aadhaar",
                "source": "Aadhaar Card",
                "extracted": {
                    "full_name": "Rajesh Kumar Verma",
                    "dob": "1988-05-12",
                    "gender": "male",
                    "address": "15 Shanti Nagar, Lucknow, UP 226001",
                    "aadhaar_masked": "XXXX-XXXX-4521",
                    "income_monthly": None,
                },
            },
            {
                "type": "income_certificate",
                "source": "Income Certificate",
                "extracted": {
                    "full_name": "Rajesh Kumar Verma",
                    "dob": "1988-05-12",
                    "income_monthly": 9200.0,
                    "address": "15, Shanti Nagar, Lucknow",
                },
            },
        ],
        "expected_risk": "low",
        "expected_score": 8,
        "fraud_label": False,
    },
    {
        "id": "APP-002",
        "declared": {
            "full_name": "Sunita Devi",
            "dob": "1975-11-20",
            "gender": "female",
            "address": "Village Rampur, Block Sadar, Varanasi, UP 221001",
            "aadhaar_masked": "XXXX-XXXX-8832",
            "pan_masked": "",
            "income_monthly": 5000.0,
            "bank_account_masked": "XXXXXXXXXX1234",
            "phone_masked": "XXXXXX5432",
            "scheme": "Ujjwala Yojana",
            "state": "Uttar Pradesh",
            "district": "Varanasi",
        },
        "documents": [
            {
                "type": "aadhaar",
                "source": "Aadhaar Card",
                "extracted": {
                    "full_name": "Sunita Devi",
                    "dob": "1975-11-20",
                    "gender": "female",
                    "address": "Village Rampur, Sadar, Varanasi 221001",
                    "aadhaar_masked": "XXXX-XXXX-8832",
                },
            },
            {
                "type": "income_certificate",
                "source": "Income Certificate",
                "extracted": {"full_name": "Sunita Devi", "income_monthly": 4800.0},
            },
        ],
        "expected_risk": "low",
        "expected_score": 5,
        "fraud_label": False,
    },
    {
        "id": "APP-003",
        "declared": {
            "full_name": "Anil Prasad Yadav",
            "dob": "1990-01-01",
            "gender": "male",
            "address": "22 MG Road, Patna, Bihar 800001",
            "aadhaar_masked": "XXXX-XXXX-9901",
            "pan_masked": "",
            "income_monthly": 7500.0,
            "bank_account_masked": "XXXXXXXXXX4455",
            "phone_masked": "XXXXXX1122",
            "scheme": "PM-KISAN",
            "state": "Bihar",
            "district": "Patna",
        },
        "documents": [
            {
                "type": "aadhaar",
                "source": "Aadhaar Card",
                "extracted": {
                    "full_name": "Anil Prasad Yadav",
                    "dob": "1990-01-01",
                    "gender": "male",
                    "address": "22 MG Road, Patna 800001",
                    "aadhaar_masked": "XXXX-XXXX-9901",
                },
            }
        ],
        "expected_risk": "low",
        "expected_score": 10,
        "fraud_label": False,
    },
    # ── Minor discrepancies (medium risk) ──
    {
        "id": "APP-004",
        "declared": {
            "full_name": "Mohan Lal Sharma",
            "dob": "1982-07-25",
            "gender": "male",
            "address": "45, Nehru Colony, Jaipur, Rajasthan 302001",
            "aadhaar_masked": "XXXX-XXXX-3344",
            "pan_masked": "",
            "income_monthly": 8000.0,
            "bank_account_masked": "XXXXXXXXXX7788",
            "phone_masked": "XXXXXX9988",
            "scheme": "PM-KISAN",
            "state": "Rajasthan",
            "district": "Jaipur",
        },
        "documents": [
            {
                "type": "aadhaar",
                "source": "Aadhaar Card",
                "extracted": {
                    "full_name": "Mohan L. Sharma",
                    "dob": "1982-07-25",
                    "gender": "male",
                    "address": "45 Nehru Colony Jaipur Raj",
                    "aadhaar_masked": "XXXX-XXXX-3344",
                },
            },
            {
                "type": "income_certificate",
                "source": "Income Certificate",
                "extracted": {
                    "full_name": "Mohan Lal Sharma",
                    "income_monthly": 12500.0,
                },
            },
        ],
        "expected_risk": "medium",
        "expected_score": 32,
        "fraud_label": False,
    },
    {
        "id": "APP-005",
        "declared": {
            "full_name": "Priya Singh",
            "dob": "1995-03-10",
            "gender": "female",
            "address": "12 Laxmi Nagar, Bhopal, MP 462001",
            "aadhaar_masked": "XXXX-XXXX-5566",
            "pan_masked": "",
            "income_monthly": 6000.0,
            "bank_account_masked": "XXXXXXXXXX2233",
            "phone_masked": "XXXXXX4455",
            "scheme": "Ujjwala Yojana",
            "state": "Madhya Pradesh",
            "district": "Bhopal",
        },
        "documents": [
            {
                "type": "aadhaar",
                "source": "Aadhaar Card",
                "extracted": {
                    "full_name": "Priya Kumari Singh",
                    "dob": "1995-03-10",
                    "gender": "female",
                    "address": "12 Laxmi Ngr Bhopal 462001",
                },
            },
            {
                "type": "bank_statement",
                "source": "Bank Statement",
                "extracted": {
                    "full_name": "Priya Singh",
                    "income_monthly": 10200.0,
                    "bank_account_masked": "XXXXXXXXXX2233",
                },
            },
        ],
        "expected_risk": "medium",
        "expected_score": 28,
        "fraud_label": False,
    },
    {
        "id": "APP-006",
        "declared": {
            "full_name": "Gopal Krishna Reddy",
            "dob": "1978-12-05",
            "gender": "male",
            "address": "78 Tank Bund Road, Hyderabad, Telangana 500001",
            "aadhaar_masked": "XXXX-XXXX-7788",
            "pan_masked": "",
            "income_monthly": 11000.0,
            "bank_account_masked": "XXXXXXXXXX3344",
            "phone_masked": "XXXXXX6677",
            "scheme": "MGNREGS",
            "state": "Telangana",
            "district": "Hyderabad",
        },
        "documents": [
            {
                "type": "aadhaar",
                "source": "Aadhaar Card",
                "extracted": {
                    "full_name": "G. Krishna Reddy",
                    "dob": "1978-12-05",
                    "gender": "male",
                    "address": "78 Tankbund Rd, Hyderabad",
                },
            },
            {
                "type": "income_certificate",
                "source": "Income Certificate",
                "extracted": {
                    "full_name": "Gopal Krishna Reddy",
                    "income_monthly": 18500.0,
                    "address": "78 Tank Bund Road Hyderabad",
                },
            },
        ],
        "expected_risk": "medium",
        "expected_score": 35,
        "fraud_label": False,
    },
    # ── High-risk fraud signals ──
    {
        "id": "APP-007",
        "declared": {
            "full_name": "Rakesh Mishra",
            "dob": "1985-06-15",
            "gender": "male",
            "address": "99 Civil Lines, Allahabad, UP 211001",
            "aadhaar_masked": "XXXX-XXXX-1122",
            "pan_masked": "",
            "income_monthly": 7000.0,
            "bank_account_masked": "XXXXXXXXXX5566",
            "phone_masked": "XXXXXX7788",
            "scheme": "PM-KISAN",
            "state": "Uttar Pradesh",
            "district": "Prayagraj",
        },
        "documents": [
            {
                "type": "aadhaar",
                "source": "Aadhaar Card",
                "extracted": {
                    "full_name": "Rakesh Kumar",
                    "dob": "1983-06-15",
                    "gender": "male",
                    "address": "Plot 99 Civil Lines Allahabad",
                    "aadhaar_masked": "XXXX-XXXX-1122",
                },
            },
            {
                "type": "income_certificate",
                "source": "Income Certificate",
                "extracted": {"full_name": "Rakesh Mishra", "income_monthly": 24000.0},
            },
            {
                "type": "bank_statement",
                "source": "Bank Statement",
                "extracted": {
                    "full_name": "R. Mishra",
                    "income_monthly": 28500.0,
                    "bank_account_masked": "XXXXXXXXXX5566",
                },
            },
        ],
        "expected_risk": "high",
        "expected_score": 72,
        "fraud_label": True,
    },
    {
        "id": "APP-008",
        "declared": {
            "full_name": "Kavita Joshi",
            "dob": "1992-09-28",
            "gender": "female",
            "address": "34 Shivaji Nagar, Pune, Maharashtra 411001",
            "aadhaar_masked": "XXXX-XXXX-9900",
            "pan_masked": "",
            "income_monthly": 5500.0,
            "bank_account_masked": "XXXXXXXXXX8877",
            "phone_masked": "XXXXXX1199",
            "scheme": "Ujjwala Yojana",
            "state": "Maharashtra",
            "district": "Pune",
        },
        "documents": [
            {
                "type": "aadhaar",
                "source": "Aadhaar Card",
                "extracted": {
                    "full_name": "Kavitha B Joshi",
                    "dob": "1990-09-28",
                    "gender": "female",
                    "address": "34 Shivaji Ngr Pune 411001",
                },
            },
            {
                "type": "income_certificate",
                "source": "Income Certificate",
                "extracted": {
                    "full_name": "Kavita Joshi",
                    "income_monthly": 22000.0,
                    "address": "54 MG Road, Mumbai",
                },
            },
        ],
        "expected_risk": "high",
        "expected_score": 68,
        "fraud_label": True,
    },
    {
        "id": "APP-009",
        "declared": {
            "full_name": "Deepak Patel",
            "dob": "1980-04-02",
            "gender": "male",
            "address": "67 Ashram Road, Ahmedabad, Gujarat 380001",
            "aadhaar_masked": "XXXX-XXXX-4455",
            "pan_masked": "",
            "income_monthly": 6500.0,
            "bank_account_masked": "XXXXXXXXXX1100",
            "phone_masked": "XXXXXX2233",
            "scheme": "PM-KISAN",
            "state": "Gujarat",
            "district": "Ahmedabad",
        },
        "documents": [
            {
                "type": "aadhaar",
                "source": "Aadhaar Card",
                "extracted": {
                    "full_name": "Dipak R Patel",
                    "dob": "1980-04-02",
                    "gender": "male",
                    "address": "67 Ashram Rd Ahmedabad",
                },
            },
            {
                "type": "income_certificate",
                "source": "Income Certificate",
                "extracted": {
                    "full_name": "Deepak Ramesh Patel",
                    "income_monthly": 45000.0,
                },
            },
            {
                "type": "bank_statement",
                "source": "Bank Statement",
                "extracted": {
                    "full_name": "Deepak R Patel",
                    "income_monthly": 52000.0,
                    "bank_account_masked": "XXXXXXXXXX1100",
                },
            },
        ],
        "expected_risk": "critical",
        "expected_score": 85,
        "fraud_label": True,
    },
    {
        "id": "APP-010",
        "declared": {
            "full_name": "Lakshmi Narayanan",
            "dob": "1970-08-18",
            "gender": "male",
            "address": "23 Anna Salai, Chennai, Tamil Nadu 600001",
            "aadhaar_masked": "XXXX-XXXX-6677",
            "pan_masked": "",
            "income_monthly": 8000.0,
            "bank_account_masked": "XXXXXXXXXX9988",
            "phone_masked": "XXXXXX4455",
            "scheme": "MGNREGS",
            "state": "Tamil Nadu",
            "district": "Chennai",
        },
        "documents": [
            {
                "type": "aadhaar",
                "source": "Aadhaar Card",
                "extracted": {
                    "full_name": "L. Narayanan",
                    "dob": "1972-08-18",
                    "gender": "male",
                    "address": "23 Anna Salai Chennai 600001",
                },
            },
            {
                "type": "income_certificate",
                "source": "Income Certificate",
                "extracted": {
                    "full_name": "Lakshmi Narayanan S",
                    "income_monthly": 35000.0,
                    "address": "55 Mount Road, Chennai",
                },
            },
            {
                "type": "bank_statement",
                "source": "Bank Statement",
                "extracted": {
                    "full_name": "Lakshmi N",
                    "income_monthly": 41000.0,
                },
            },
        ],
        "expected_risk": "critical",
        "expected_score": 90,
        "fraud_label": True,
    },
    # ── More clean / minor cases to fill the dashboard ──
    {
        "id": "APP-011",
        "declared": {"full_name": "Meena Kumari", "dob": "1993-02-14", "gender": "female", "address": "8 Rajaji Street, Madurai, TN 625001", "aadhaar_masked": "XXXX-XXXX-1234", "pan_masked": "", "income_monthly": 4500.0, "bank_account_masked": "XXXXXXXXXX5678", "phone_masked": "XXXXXX9012", "scheme": "Ujjwala Yojana", "state": "Tamil Nadu", "district": "Madurai"},
        "documents": [{"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Meena Kumari", "dob": "1993-02-14", "gender": "female", "address": "8 Rajaji St Madurai 625001"}}],
        "expected_risk": "low", "expected_score": 5, "fraud_label": False,
    },
    {
        "id": "APP-012",
        "declared": {"full_name": "Bharat Singh Thakur", "dob": "1987-10-03", "gender": "male", "address": "14 Mall Road, Shimla, HP 171001", "aadhaar_masked": "XXXX-XXXX-5678", "pan_masked": "", "income_monthly": 7200.0, "bank_account_masked": "XXXXXXXXXX9012", "phone_masked": "XXXXXX3456", "scheme": "PM-KISAN", "state": "Himachal Pradesh", "district": "Shimla"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Bharat S Thakur", "dob": "1987-10-03", "gender": "male"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Bharat Singh Thakur", "income_monthly": 7500.0}},
        ],
        "expected_risk": "low", "expected_score": 8, "fraud_label": False,
    },
    {
        "id": "APP-013",
        "declared": {"full_name": "Fatima Begum", "dob": "1968-06-22", "gender": "female", "address": "56 Charminar Road, Hyderabad, TS 500002", "aadhaar_masked": "XXXX-XXXX-3456", "pan_masked": "", "income_monthly": 3500.0, "bank_account_masked": "XXXXXXXXXX7890", "phone_masked": "XXXXXX1234", "scheme": "Ujjwala Yojana", "state": "Telangana", "district": "Hyderabad"},
        "documents": [{"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Fatima Begum", "dob": "1968-06-22", "gender": "female", "address": "56 Charminar Rd Hyderabad"}}],
        "expected_risk": "low", "expected_score": 3, "fraud_label": False,
    },
    {
        "id": "APP-014",
        "declared": {"full_name": "Vikram Chauhan", "dob": "1991-12-30", "gender": "male", "address": "101 Station Road, Indore, MP 452001", "aadhaar_masked": "XXXX-XXXX-7890", "pan_masked": "", "income_monthly": 9500.0, "bank_account_masked": "XXXXXXXXXX2345", "phone_masked": "XXXXXX6789", "scheme": "MGNREGS", "state": "Madhya Pradesh", "district": "Indore"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Vikram Singh Chauhan", "dob": "1991-12-30", "gender": "male"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Vikram Chauhan", "income_monthly": 16000.0}},
        ],
        "expected_risk": "medium", "expected_score": 25, "fraud_label": False,
    },
    {
        "id": "APP-015",
        "declared": {"full_name": "Sanjay Gupta", "dob": "1976-03-08", "gender": "male", "address": "29 Park Street, Kolkata, WB 700016", "aadhaar_masked": "XXXX-XXXX-2345", "pan_masked": "", "income_monthly": 6800.0, "bank_account_masked": "XXXXXXXXXX6789", "phone_masked": "XXXXXX0123", "scheme": "PM-KISAN", "state": "West Bengal", "district": "Kolkata"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Sanjay K Gupta", "dob": "1974-03-08", "gender": "male", "address": "29 Park St Kolkata"}},
            {"type": "bank_statement", "source": "Bank Statement", "extracted": {"full_name": "S. Gupta", "income_monthly": 32000.0}},
        ],
        "expected_risk": "high", "expected_score": 65, "fraud_label": True,
    },
    {
        "id": "APP-016",
        "declared": {"full_name": "Asha Rani", "dob": "1984-07-19", "gender": "female", "address": "7 Lajpat Nagar, New Delhi 110024", "aadhaar_masked": "XXXX-XXXX-6789", "pan_masked": "", "income_monthly": 5200.0, "bank_account_masked": "XXXXXXXXXX0123", "phone_masked": "XXXXXX4567", "scheme": "Ujjwala Yojana", "state": "Delhi", "district": "South Delhi"},
        "documents": [{"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Asha Rani", "dob": "1984-07-19", "gender": "female", "address": "7 Lajpat Nagar Delhi 110024"}}],
        "expected_risk": "low", "expected_score": 4, "fraud_label": False,
    },
    {
        "id": "APP-017",
        "declared": {"full_name": "Manoj Tiwari", "dob": "1989-11-11", "gender": "male", "address": "33 Hazratganj, Lucknow, UP 226001", "aadhaar_masked": "XXXX-XXXX-8901", "pan_masked": "", "income_monthly": 8800.0, "bank_account_masked": "XXXXXXXXXX4567", "phone_masked": "XXXXXX8901", "scheme": "MGNREGS", "state": "Uttar Pradesh", "district": "Lucknow"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Manoj K Tiwari", "dob": "1989-11-11", "gender": "male"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Manoj Tiwari", "income_monthly": 9100.0}},
            {"type": "bank_statement", "source": "Bank Statement", "extracted": {"full_name": "Manoj Tiwari", "income_monthly": 9500.0}},
        ],
        "expected_risk": "low", "expected_score": 6, "fraud_label": False,
    },
    {
        "id": "APP-018",
        "declared": {"full_name": "Ravi Shankar Dubey", "dob": "1965-04-25", "gender": "male", "address": "12 Dashashwamedh, Varanasi, UP 221001", "aadhaar_masked": "XXXX-XXXX-0123", "pan_masked": "", "income_monthly": 4200.0, "bank_account_masked": "XXXXXXXXXX8901", "phone_masked": "XXXXXX2345", "scheme": "PM-KISAN", "state": "Uttar Pradesh", "district": "Varanasi"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Ravishankar Dubey", "dob": "1965-04-25", "gender": "male", "address": "12 Dashashwamedh Ghat Varanasi"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Ravi Shankar Dubey", "income_monthly": 4000.0}},
        ],
        "expected_risk": "low", "expected_score": 7, "fraud_label": False,
    },
    {
        "id": "APP-019",
        "declared": {"full_name": "Pooja Mehta", "dob": "1997-01-30", "gender": "female", "address": "88 CG Road, Ahmedabad, Gujarat 380006", "aadhaar_masked": "XXXX-XXXX-4567", "pan_masked": "", "income_monthly": 7800.0, "bank_account_masked": "XXXXXXXXXX2345", "phone_masked": "XXXXXX6789", "scheme": "Ujjwala Yojana", "state": "Gujarat", "district": "Ahmedabad"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Pooja B Mehta", "dob": "1997-01-30", "gender": "female"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Pooja Mehta", "income_monthly": 7500.0}},
        ],
        "expected_risk": "low", "expected_score": 5, "fraud_label": False,
    },
    {
        "id": "APP-020",
        "declared": {"full_name": "Abdul Rahman Khan", "dob": "1973-09-14", "gender": "male", "address": "45 Aminabad, Lucknow, UP 226018", "aadhaar_masked": "XXXX-XXXX-5678", "pan_masked": "", "income_monthly": 5000.0, "bank_account_masked": "XXXXXXXXXX6789", "phone_masked": "XXXXXX0123", "scheme": "MGNREGS", "state": "Uttar Pradesh", "district": "Lucknow"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Abdul R Khan", "dob": "1973-09-14", "gender": "male", "address": "45 Aminabad Lucknow 226018"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Abdul Rahman Khan", "income_monthly": 38000.0}},
            {"type": "bank_statement", "source": "Bank Statement", "extracted": {"full_name": "A.R. Khan", "income_monthly": 42000.0}},
        ],
        "expected_risk": "critical", "expected_score": 88, "fraud_label": True,
    },
    # ═══════════════════════════════════════════════════════════════════
    # Sprint 4 — expanded fraud-pattern coverage (APP-021 → APP-052)
    # ═══════════════════════════════════════════════════════════════════

    # ── Ghost Beneficiaries (minimal/empty documents) ──
    {
        "id": "APP-021",
        "declared": {"full_name": "Phantom Singh", "dob": "1991-05-05", "gender": "male", "address": "Unknown Address, Block X, Gorakhpur, UP 273001", "aadhaar_masked": "XXXX-XXXX-0001", "pan_masked": "", "income_monthly": 4000.0, "bank_account_masked": "", "phone_masked": "", "scheme": "PM-KISAN", "state": "Uttar Pradesh", "district": "Gorakhpur"},
        "documents": [],
        "expected_risk": "high", "expected_score": 55, "fraud_label": True, "fraud_type": "ghost",
    },
    {
        "id": "APP-022",
        "declared": {"full_name": "Blank Doc Rani", "dob": "1985-08-12", "gender": "female", "address": "Village Kuch Nahi, Sitapur, UP 261001", "aadhaar_masked": "XXXX-XXXX-0002", "pan_masked": "", "income_monthly": 3500.0, "bank_account_masked": "", "phone_masked": "", "scheme": "Ujjwala Yojana", "state": "Uttar Pradesh", "district": "Sitapur"},
        "documents": [{"type": "aadhaar", "source": "Aadhaar Card", "extracted": {}}],
        "expected_risk": "high", "expected_score": 50, "fraud_label": True, "fraud_type": "ghost",
    },
    {
        "id": "APP-023",
        "declared": {"full_name": "No Proof Kumar", "dob": "1992-03-22", "gender": "male", "address": "NA, Deoria, UP 274001", "aadhaar_masked": "XXXX-XXXX-0003", "pan_masked": "", "income_monthly": 5000.0, "bank_account_masked": "", "phone_masked": "", "scheme": "MGNREGS", "state": "Uttar Pradesh", "district": "Deoria"},
        "documents": [],
        "expected_risk": "high", "expected_score": 55, "fraud_label": True, "fraud_type": "ghost",
    },
    {
        "id": "APP-024",
        "declared": {"full_name": "Empty Docs Devi", "dob": "1978-11-30", "gender": "female", "address": "Ghost Lane 1, Ambedkar Nagar, UP 224001", "aadhaar_masked": "XXXX-XXXX-0004", "pan_masked": "", "income_monthly": 2800.0, "bank_account_masked": "", "phone_masked": "", "scheme": "PM-KISAN", "state": "Uttar Pradesh", "district": "Ambedkar Nagar"},
        "documents": [{"type": "income_certificate", "source": "Income Certificate", "extracted": {}}],
        "expected_risk": "high", "expected_score": 52, "fraud_label": True, "fraud_type": "ghost",
    },
    {
        "id": "APP-025",
        "declared": {"full_name": "Invisible Prasad", "dob": "1995-01-15", "gender": "male", "address": "Plot 0, Nowhere, Ballia, UP 277001", "aadhaar_masked": "XXXX-XXXX-0005", "pan_masked": "", "income_monthly": 4500.0, "bank_account_masked": "", "phone_masked": "", "scheme": "Ujjwala Yojana", "state": "Uttar Pradesh", "district": "Ballia"},
        "documents": [],
        "expected_risk": "high", "expected_score": 55, "fraud_label": True, "fraud_type": "ghost",
    },

    # ── Duplicate Identity Ring (shared phone, bank, address) ──
    {
        "id": "APP-026",
        "declared": {"full_name": "Raju Sharma", "dob": "1988-02-14", "gender": "male", "address": "12 Ring Road, Sector 15, Noida, UP 201301", "aadhaar_masked": "XXXX-XXXX-5551", "pan_masked": "", "income_monthly": 6000.0, "bank_account_masked": "XXXXXXXXXX5555", "phone_masked": "XXXXXX5555", "scheme": "PM-KISAN", "state": "Uttar Pradesh", "district": "Gautam Buddha Nagar"},
        "documents": [{"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Raju Sharma", "dob": "1988-02-14", "gender": "male", "address": "12 Ring Road Noida", "aadhaar_masked": "XXXX-XXXX-5551"}}],
        "expected_risk": "high", "expected_score": 60, "fraud_label": True, "fraud_type": "duplicate_ring",
    },
    {
        "id": "APP-027",
        "declared": {"full_name": "Pappu Verma", "dob": "1990-06-20", "gender": "male", "address": "12 Ring Road, Sector 15, Noida, UP 201301", "aadhaar_masked": "XXXX-XXXX-5552", "pan_masked": "", "income_monthly": 5800.0, "bank_account_masked": "XXXXXXXXXX5555", "phone_masked": "XXXXXX5555", "scheme": "MGNREGS", "state": "Uttar Pradesh", "district": "Gautam Buddha Nagar"},
        "documents": [{"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Pappu Verma", "dob": "1990-06-20", "gender": "male", "address": "12 Ring Road Noida", "aadhaar_masked": "XXXX-XXXX-5552"}}],
        "expected_risk": "high", "expected_score": 58, "fraud_label": True, "fraud_type": "duplicate_ring",
    },
    {
        "id": "APP-028",
        "declared": {"full_name": "Munna Bhai", "dob": "1987-09-10", "gender": "male", "address": "12 Ring Road, Sector 15, Noida, UP 201301", "aadhaar_masked": "XXXX-XXXX-5553", "pan_masked": "", "income_monthly": 6200.0, "bank_account_masked": "XXXXXXXXXX5555", "phone_masked": "XXXXXX5555", "scheme": "PM-KISAN", "state": "Uttar Pradesh", "district": "Gautam Buddha Nagar"},
        "documents": [{"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Munna Bhai", "dob": "1987-09-10", "gender": "male", "address": "12 Ring Road Sector 15 Noida"}}],
        "expected_risk": "high", "expected_score": 60, "fraud_label": True, "fraud_type": "duplicate_ring",
    },
    {
        "id": "APP-029",
        "declared": {"full_name": "Chhotu Lal", "dob": "1992-12-01", "gender": "male", "address": "12 Ring Road, Sector 15, Noida, UP 201301", "aadhaar_masked": "XXXX-XXXX-5554", "pan_masked": "", "income_monthly": 5500.0, "bank_account_masked": "XXXXXXXXXX5555", "phone_masked": "XXXXXX5555", "scheme": "Ujjwala Yojana", "state": "Uttar Pradesh", "district": "Gautam Buddha Nagar"},
        "documents": [{"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Chhotu Lal", "dob": "1992-12-01", "gender": "male", "address": "12 Ring Road Noida"}}],
        "expected_risk": "high", "expected_score": 58, "fraud_label": True, "fraud_type": "duplicate_ring",
    },
    {
        "id": "APP-030",
        "declared": {"full_name": "Billu Yadav", "dob": "1989-04-18", "gender": "male", "address": "12 Ring Road, Sector 15, Noida, UP 201301", "aadhaar_masked": "XXXX-XXXX-5555", "pan_masked": "", "income_monthly": 5900.0, "bank_account_masked": "XXXXXXXXXX5555", "phone_masked": "XXXXXX5555", "scheme": "MGNREGS", "state": "Uttar Pradesh", "district": "Gautam Buddha Nagar"},
        "documents": [{"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Billu Yadav", "dob": "1989-04-18", "gender": "male", "address": "12 Ring Rd Noida"}}],
        "expected_risk": "high", "expected_score": 60, "fraud_label": True, "fraud_type": "duplicate_ring",
    },

    # ── Income Inflation (massive declared-vs-extracted income gap) ──
    {
        "id": "APP-031",
        "declared": {"full_name": "Suresh Inflated Rao", "dob": "1983-07-12", "gender": "male", "address": "5 MG Road, Bangalore, Karnataka 560001", "aadhaar_masked": "XXXX-XXXX-3101", "pan_masked": "XXXXX3101X", "income_monthly": 6000.0, "bank_account_masked": "XXXXXXXXXX3101", "phone_masked": "XXXXXX3101", "scheme": "PM-KISAN", "state": "Karnataka", "district": "Bangalore Urban"},
        "documents": [
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Suresh Rao", "income_monthly": 55000.0}},
            {"type": "bank_statement", "source": "Bank Statement", "extracted": {"full_name": "Suresh I Rao", "income_monthly": 62000.0, "bank_account_masked": "XXXXXXXXXX3101"}},
        ],
        "expected_risk": "critical", "expected_score": 82, "fraud_label": True, "fraud_type": "income_inflation",
    },
    {
        "id": "APP-032",
        "declared": {"full_name": "Geeta Mishra", "dob": "1979-11-25", "gender": "female", "address": "88 Civil Lines, Nagpur, Maharashtra 440001", "aadhaar_masked": "XXXX-XXXX-3201", "pan_masked": "", "income_monthly": 5500.0, "bank_account_masked": "XXXXXXXXXX3201", "phone_masked": "XXXXXX3201", "scheme": "Ujjwala Yojana", "state": "Maharashtra", "district": "Nagpur"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Geeta R Mishra", "dob": "1979-11-25", "gender": "female"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Geeta Mishra", "income_monthly": 48000.0}},
        ],
        "expected_risk": "critical", "expected_score": 80, "fraud_label": True, "fraud_type": "income_inflation",
    },
    {
        "id": "APP-033",
        "declared": {"full_name": "Kiran Bala", "dob": "1986-04-10", "gender": "female", "address": "22 Dalal Street, Mumbai, Maharashtra 400001", "aadhaar_masked": "XXXX-XXXX-3301", "pan_masked": "", "income_monthly": 7000.0, "bank_account_masked": "XXXXXXXXXX3301", "phone_masked": "XXXXXX3301", "scheme": "MGNREGS", "state": "Maharashtra", "district": "Mumbai"},
        "documents": [
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Kiran Bala", "income_monthly": 58000.0}},
            {"type": "bank_statement", "source": "Bank Statement", "extracted": {"full_name": "K. Bala", "income_monthly": 64000.0}},
        ],
        "expected_risk": "critical", "expected_score": 85, "fraud_label": True, "fraud_type": "income_inflation",
    },
    {
        "id": "APP-034",
        "declared": {"full_name": "Harish Pandey", "dob": "1975-08-20", "gender": "male", "address": "33 Gomti Nagar, Lucknow, UP 226010", "aadhaar_masked": "XXXX-XXXX-3401", "pan_masked": "", "income_monthly": 4800.0, "bank_account_masked": "XXXXXXXXXX3401", "phone_masked": "XXXXXX3401", "scheme": "PM-KISAN", "state": "Uttar Pradesh", "district": "Lucknow"},
        "documents": [
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Harish Pandey", "income_monthly": 42000.0}},
            {"type": "bank_statement", "source": "Bank Statement", "extracted": {"full_name": "H Pandey", "income_monthly": 47000.0, "bank_account_masked": "XXXXXXXXXX3401"}},
        ],
        "expected_risk": "critical", "expected_score": 82, "fraud_label": True, "fraud_type": "income_inflation",
    },
    {
        "id": "APP-035",
        "declared": {"full_name": "Nirmala Soni", "dob": "1990-01-15", "gender": "female", "address": "11 Law Garden, Ahmedabad, Gujarat 380015", "aadhaar_masked": "XXXX-XXXX-3501", "pan_masked": "", "income_monthly": 5200.0, "bank_account_masked": "XXXXXXXXXX3501", "phone_masked": "XXXXXX3501", "scheme": "Ujjwala Yojana", "state": "Gujarat", "district": "Ahmedabad"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Nirmala K Soni", "dob": "1990-01-15", "gender": "female"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Nirmala Soni", "income_monthly": 51000.0}},
        ],
        "expected_risk": "critical", "expected_score": 80, "fraud_label": True, "fraud_type": "income_inflation",
    },

    # ── Deceased Claims (elderly / deceased beneficiaries) ──
    {
        "id": "APP-036",
        "declared": {"full_name": "Late Shri Ram Prasad", "dob": "1942-03-15", "gender": "male", "address": "Old Quarter 1, Varanasi, UP 221001", "aadhaar_masked": "XXXX-XXXX-3601", "pan_masked": "", "income_monthly": 3000.0, "bank_account_masked": "XXXXXXXXXX3601", "phone_masked": "XXXXXX3601", "scheme": "PM-KISAN", "state": "Uttar Pradesh", "district": "Varanasi"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Ram Prasad", "dob": "1942-03-15", "gender": "male", "address": "Old Quarter Varanasi"}},
        ],
        "expected_risk": "high", "expected_score": 60, "fraud_label": True, "fraud_type": "deceased",
    },
    {
        "id": "APP-037",
        "declared": {"full_name": "Late Smt Kamla Devi", "dob": "1938-09-20", "gender": "female", "address": "Ward 3, Mathura, UP 281001", "aadhaar_masked": "XXXX-XXXX-3701", "pan_masked": "", "income_monthly": 2500.0, "bank_account_masked": "XXXXXXXXXX3701", "phone_masked": "XXXXXX3701", "scheme": "Ujjwala Yojana", "state": "Uttar Pradesh", "district": "Mathura"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Kamla Devi", "dob": "1938-09-20", "gender": "female"}},
        ],
        "expected_risk": "high", "expected_score": 58, "fraud_label": True, "fraud_type": "deceased",
    },
    {
        "id": "APP-038",
        "declared": {"full_name": "Late Babu Lal Verma", "dob": "1945-12-10", "gender": "male", "address": "Purani Basti, Agra, UP 282001", "aadhaar_masked": "XXXX-XXXX-3801", "pan_masked": "", "income_monthly": 2800.0, "bank_account_masked": "XXXXXXXXXX3801", "phone_masked": "XXXXXX3801", "scheme": "MGNREGS", "state": "Uttar Pradesh", "district": "Agra"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Babu Lal", "dob": "1945-12-10", "gender": "male"}},
        ],
        "expected_risk": "high", "expected_score": 58, "fraud_label": True, "fraud_type": "deceased",
    },

    # ── Scheme Hoppers (same person, multiple schemes, inconsistent data) ──
    {
        "id": "APP-039",
        "declared": {"full_name": "Ramesh Chandra Gupta", "dob": "1980-06-15", "gender": "male", "address": "55 Station Road, Kanpur, UP 208001", "aadhaar_masked": "XXXX-XXXX-3901", "pan_masked": "XXXXX3901X", "income_monthly": 7000.0, "bank_account_masked": "XXXXXXXXXX3901", "phone_masked": "XXXXXX3901", "scheme": "PM-KISAN", "state": "Uttar Pradesh", "district": "Kanpur"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Ramesh C Gupta", "dob": "1980-06-15", "gender": "male", "address": "55 Station Rd Kanpur"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Ramesh Chandra Gupta", "income_monthly": 7200.0}},
        ],
        "expected_risk": "medium", "expected_score": 40, "fraud_label": True, "fraud_type": "scheme_hopping",
    },
    {
        "id": "APP-040",
        "declared": {"full_name": "Ramesh Chandra Gupta", "dob": "1980-06-15", "gender": "male", "address": "55 Station Road, Kanpur, UP 208001", "aadhaar_masked": "XXXX-XXXX-3901", "pan_masked": "XXXXX3901X", "income_monthly": 4500.0, "bank_account_masked": "XXXXXXXXXX3901", "phone_masked": "XXXXXX3901", "scheme": "Ujjwala Yojana", "state": "Uttar Pradesh", "district": "Kanpur"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "R C Gupta", "dob": "1980-06-15", "gender": "male"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Ramesh Gupta", "income_monthly": 12000.0}},
        ],
        "expected_risk": "high", "expected_score": 55, "fraud_label": True, "fraud_type": "scheme_hopping",
    },
    {
        "id": "APP-041",
        "declared": {"full_name": "Ramesh Chandra Gupta", "dob": "1980-06-15", "gender": "male", "address": "112 Mall Road, Kanpur, UP 208004", "aadhaar_masked": "XXXX-XXXX-3901", "pan_masked": "XXXXX3901X", "income_monthly": 3200.0, "bank_account_masked": "XXXXXXXXXX3901", "phone_masked": "XXXXXX3901", "scheme": "MGNREGS", "state": "Uttar Pradesh", "district": "Kanpur"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Ramesh Chandra Gupta", "dob": "1981-06-15", "gender": "male", "address": "112 Mall Rd Kanpur"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Ramesh C Gupta", "income_monthly": 18000.0}},
        ],
        "expected_risk": "high", "expected_score": 58, "fraud_label": True, "fraud_type": "scheme_hopping",
    },

    # ── Address Cluster (3+ apps at same address) ──
    {
        "id": "APP-042",
        "declared": {"full_name": "Amar Nath", "dob": "1985-03-22", "gender": "male", "address": "42 Cluster Colony, Sector 7, Gurugram, Haryana 122001", "aadhaar_masked": "XXXX-XXXX-4201", "pan_masked": "", "income_monthly": 6500.0, "bank_account_masked": "XXXXXXXXXX4201", "phone_masked": "XXXXXX4201", "scheme": "PM-KISAN", "state": "Haryana", "district": "Gurugram"},
        "documents": [{"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Amar Nath", "dob": "1985-03-22", "gender": "male", "address": "42 Cluster Colony Sec 7 Gurugram"}}],
        "expected_risk": "high", "expected_score": 52, "fraud_label": True, "fraud_type": "address_cluster",
    },
    {
        "id": "APP-043",
        "declared": {"full_name": "Prem Lata", "dob": "1990-07-08", "gender": "female", "address": "42 Cluster Colony, Sector 7, Gurugram, Haryana 122001", "aadhaar_masked": "XXXX-XXXX-4301", "pan_masked": "", "income_monthly": 5800.0, "bank_account_masked": "XXXXXXXXXX4301", "phone_masked": "XXXXXX4301", "scheme": "Ujjwala Yojana", "state": "Haryana", "district": "Gurugram"},
        "documents": [{"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Prem Lata", "dob": "1990-07-08", "gender": "female", "address": "42 Cluster Colony Gurugram"}}],
        "expected_risk": "high", "expected_score": 52, "fraud_label": True, "fraud_type": "address_cluster",
    },
    {
        "id": "APP-044",
        "declared": {"full_name": "Om Prakash", "dob": "1977-01-30", "gender": "male", "address": "42 Cluster Colony, Sector 7, Gurugram, Haryana 122001", "aadhaar_masked": "XXXX-XXXX-4401", "pan_masked": "", "income_monthly": 7200.0, "bank_account_masked": "XXXXXXXXXX4401", "phone_masked": "XXXXXX4401", "scheme": "MGNREGS", "state": "Haryana", "district": "Gurugram"},
        "documents": [{"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Om Prakash", "dob": "1977-01-30", "gender": "male", "address": "42 Cluster Colony Sector 7 Gurugram 122001"}}],
        "expected_risk": "high", "expected_score": 52, "fraud_label": True, "fraud_type": "address_cluster",
    },
    {
        "id": "APP-045",
        "declared": {"full_name": "Savitri Devi", "dob": "1982-11-14", "gender": "female", "address": "42 Cluster Colony, Sector 7, Gurugram, Haryana 122001", "aadhaar_masked": "XXXX-XXXX-4501", "pan_masked": "", "income_monthly": 4900.0, "bank_account_masked": "XXXXXXXXXX4501", "phone_masked": "XXXXXX4501", "scheme": "PM-KISAN", "state": "Haryana", "district": "Gurugram"},
        "documents": [{"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Savitri Devi", "dob": "1982-11-14", "gender": "female", "address": "42 Cluster Colony Gurugram"}}],
        "expected_risk": "high", "expected_score": 52, "fraud_label": True, "fraud_type": "address_cluster",
    },
    {
        "id": "APP-046",
        "declared": {"full_name": "Dharamveer Singh", "dob": "1988-05-05", "gender": "male", "address": "42 Cluster Colony, Sector 7, Gurugram, Haryana 122001", "aadhaar_masked": "XXXX-XXXX-4601", "pan_masked": "", "income_monthly": 6100.0, "bank_account_masked": "XXXXXXXXXX4601", "phone_masked": "XXXXXX4601", "scheme": "Ujjwala Yojana", "state": "Haryana", "district": "Gurugram"},
        "documents": [{"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Dharamveer Singh", "dob": "1988-05-05", "gender": "male", "address": "42 Cluster Colony Sec 7 Gurugram"}}],
        "expected_risk": "high", "expected_score": 52, "fraud_label": True, "fraud_type": "address_cluster",
    },

    # ── Additional Clean Applications ──
    {
        "id": "APP-047",
        "declared": {"full_name": "Anita Kumari", "dob": "1994-08-18", "gender": "female", "address": "25 Gandhi Nagar, Ranchi, Jharkhand 834001", "aadhaar_masked": "XXXX-XXXX-4701", "pan_masked": "", "income_monthly": 5500.0, "bank_account_masked": "XXXXXXXXXX4701", "phone_masked": "XXXXXX4701", "scheme": "Ujjwala Yojana", "state": "Jharkhand", "district": "Ranchi"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Anita Kumari", "dob": "1994-08-18", "gender": "female", "address": "25 Gandhi Nagar Ranchi"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Anita Kumari", "income_monthly": 5700.0}},
        ],
        "expected_risk": "low", "expected_score": 5, "fraud_label": False, "fraud_type": "clean",
    },
    {
        "id": "APP-048",
        "declared": {"full_name": "Sunil Kumar Das", "dob": "1981-05-02", "gender": "male", "address": "77 Lake Town, Kolkata, WB 700089", "aadhaar_masked": "XXXX-XXXX-4801", "pan_masked": "", "income_monthly": 8200.0, "bank_account_masked": "XXXXXXXXXX4801", "phone_masked": "XXXXXX4801", "scheme": "PM-KISAN", "state": "West Bengal", "district": "Kolkata"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Sunil K Das", "dob": "1981-05-02", "gender": "male", "address": "77 Lake Town Kolkata"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Sunil Kumar Das", "income_monthly": 8500.0}},
        ],
        "expected_risk": "low", "expected_score": 7, "fraud_label": False, "fraud_type": "clean",
    },
    {
        "id": "APP-049",
        "declared": {"full_name": "Rekha Jain", "dob": "1973-10-12", "gender": "female", "address": "9 Malviya Nagar, Jaipur, Rajasthan 302017", "aadhaar_masked": "XXXX-XXXX-4901", "pan_masked": "", "income_monthly": 4200.0, "bank_account_masked": "XXXXXXXXXX4901", "phone_masked": "XXXXXX4901", "scheme": "Ujjwala Yojana", "state": "Rajasthan", "district": "Jaipur"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Rekha Jain", "dob": "1973-10-12", "gender": "female", "address": "9 Malviya Nagar Jaipur"}},
        ],
        "expected_risk": "low", "expected_score": 4, "fraud_label": False, "fraud_type": "clean",
    },
    {
        "id": "APP-050",
        "declared": {"full_name": "Dinesh Prasad Sahu", "dob": "1969-02-28", "gender": "male", "address": "18 Civil Station, Raipur, Chhattisgarh 492001", "aadhaar_masked": "XXXX-XXXX-5001", "pan_masked": "", "income_monthly": 6800.0, "bank_account_masked": "XXXXXXXXXX5001", "phone_masked": "XXXXXX5001", "scheme": "MGNREGS", "state": "Chhattisgarh", "district": "Raipur"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Dinesh P Sahu", "dob": "1969-02-28", "gender": "male", "address": "18 Civil Station Raipur"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Dinesh Prasad Sahu", "income_monthly": 7000.0}},
        ],
        "expected_risk": "low", "expected_score": 6, "fraud_label": False, "fraud_type": "clean",
    },
    {
        "id": "APP-051",
        "declared": {"full_name": "Kamla Bai Patil", "dob": "1987-06-30", "gender": "female", "address": "63 Tilak Road, Pune, Maharashtra 411030", "aadhaar_masked": "XXXX-XXXX-5101", "pan_masked": "", "income_monthly": 5100.0, "bank_account_masked": "XXXXXXXXXX5101", "phone_masked": "XXXXXX5101", "scheme": "Ujjwala Yojana", "state": "Maharashtra", "district": "Pune"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Kamla B Patil", "dob": "1987-06-30", "gender": "female", "address": "63 Tilak Rd Pune"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Kamla Bai Patil", "income_monthly": 5300.0}},
        ],
        "expected_risk": "low", "expected_score": 5, "fraud_label": False, "fraud_type": "clean",
    },
    {
        "id": "APP-052",
        "declared": {"full_name": "Jagdish Yadav", "dob": "1976-12-05", "gender": "male", "address": "31 Vikas Nagar, Dehradun, Uttarakhand 248001", "aadhaar_masked": "XXXX-XXXX-5201", "pan_masked": "", "income_monthly": 7500.0, "bank_account_masked": "XXXXXXXXXX5201", "phone_masked": "XXXXXX5201", "scheme": "PM-KISAN", "state": "Uttarakhand", "district": "Dehradun"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Jagdish Yadav", "dob": "1976-12-05", "gender": "male", "address": "31 Vikas Nagar Dehradun"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Jagdish Yadav", "income_monthly": 7800.0}},
        ],
        "expected_risk": "low", "expected_score": 4, "fraud_label": False, "fraud_type": "clean",
    },
]

# ── Annotate legacy entries (APP-001…APP-020) with fraud_type ──
_FRAUD_TYPE_MAP: dict[str, str] = {
    "APP-001": "clean",
    "APP-002": "clean",
    "APP-003": "clean",
    "APP-004": "clean",
    "APP-005": "clean",
    "APP-006": "clean",
    "APP-007": "income_inflation",
    "APP-008": "income_inflation",
    "APP-009": "income_inflation",
    "APP-010": "income_inflation",
    "APP-011": "clean",
    "APP-012": "clean",
    "APP-013": "clean",
    "APP-014": "clean",
    "APP-015": "income_inflation",
    "APP-016": "clean",
    "APP-017": "clean",
    "APP-018": "clean",
    "APP-019": "clean",
    "APP-020": "income_inflation",
}
for _app in SEED_APPLICATIONS:
    _app.setdefault("fraud_type", _FRAUD_TYPE_MAP.get(_app["id"], "clean"))
