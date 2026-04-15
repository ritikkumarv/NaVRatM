"""Synthetic seed data — 20 demo applications with known fraud patterns."""

SEED_APPLICATIONS = [
    # ── Clean applications (low risk) ──
    {
        "id": "APP-001",
        "declared": {
            "full_name": "Rajesh Kumar Verma",
            "date_of_birth": "1988-05-12",
            "gender": "male",
            "address": "15, Shanti Nagar, Lucknow, Uttar Pradesh 226001",
            "aadhaar_number": "XXXX-XXXX-4521",
            "pan_number": "XXXXX2345X",
            "income_monthly": 9000.0,
            "bank_account": "XXXXXXXXXX6789",
            "phone": "XXXXXX7890",
            "scheme": "PM-KISAN",
            "state": "Uttar Pradesh",
            "district": "Lucknow"
        },
        "documents": [
            {
                "type": "aadhaar", "source": "Aadhaar Card",
                "extracted": {"full_name": "Rajesh Kumar Verma", "date_of_birth": "1988-05-12", "gender": "male", "address": "15 Shanti Nagar, Lucknow, UP 226001", "aadhaar_number": "XXXX-XXXX-4521", "income_monthly": None}
            },
            {
                "type": "income_certificate", "source": "Income Certificate",
                "extracted": {"full_name": "Rajesh Kumar Verma", "date_of_birth": "1988-05-12", "income_monthly": 9200.0, "address": "15, Shanti Nagar, Lucknow"}
            }
        ],
        "expected_risk": "low",
        "expected_score": 8,
        "fraud_label": False
    },
    {
        "id": "APP-002",
        "declared": {
            "full_name": "Sunita Devi",
            "date_of_birth": "1975-11-20",
            "gender": "female",
            "address": "Village Rampur, Block Sadar, Varanasi, UP 221001",
            "aadhaar_number": "XXXX-XXXX-8832",
            "pan_number": "",
            "income_monthly": 5000.0,
            "bank_account": "XXXXXXXXXX1234",
            "phone": "XXXXXX5432",
            "scheme": "Ujjwala Yojana",
            "state": "Uttar Pradesh",
            "district": "Varanasi"
        },
        "documents": [
            {
                "type": "aadhaar", "source": "Aadhaar Card",
                "extracted": {"full_name": "Sunita Devi", "date_of_birth": "1975-11-20", "gender": "female", "address": "Village Rampur, Sadar, Varanasi 221001", "aadhaar_number": "XXXX-XXXX-8832"}
            },
            {
                "type": "income_certificate", "source": "Income Certificate",
                "extracted": {"full_name": "Sunita Devi", "income_monthly": 4800.0}
            }
        ],
        "expected_risk": "low",
        "expected_score": 5,
        "fraud_label": False
    },
    {
        "id": "APP-003",
        "declared": {
            "full_name": "Anil Prasad Yadav",
            "date_of_birth": "1990-01-01",
            "gender": "male",
            "address": "22 MG Road, Patna, Bihar 800001",
            "aadhaar_number": "XXXX-XXXX-9901",
            "income_monthly": 7500.0,
            "bank_account": "XXXXXXXXXX4455",
            "phone": "XXXXXX1122",
            "scheme": "PM-KISAN",
            "state": "Bihar",
            "district": "Patna"
        },
        "documents": [
            {
                "type": "aadhaar", "source": "Aadhaar Card",
                "extracted": {"full_name": "Anil Prasad Yadav", "date_of_birth": "1990-01-01", "gender": "male", "address": "22 MG Road, Patna 800001", "aadhaar_number": "XXXX-XXXX-9901"}
            }
        ],
        "expected_risk": "low",
        "expected_score": 10,
        "fraud_label": False
    },

    # ── Minor discrepancies (medium risk) ──
    {
        "id": "APP-004",
        "declared": {
            "full_name": "Mohan Lal Sharma",
            "date_of_birth": "1982-07-25",
            "gender": "male",
            "address": "45, Nehru Colony, Jaipur, Rajasthan 302001",
            "aadhaar_number": "XXXX-XXXX-3344",
            "income_monthly": 8000.0,
            "bank_account": "XXXXXXXXXX7788",
            "phone": "XXXXXX9988",
            "scheme": "PM-KISAN",
            "state": "Rajasthan",
            "district": "Jaipur"
        },
        "documents": [
            {
                "type": "aadhaar", "source": "Aadhaar Card",
                "extracted": {"full_name": "Mohan L. Sharma", "date_of_birth": "1982-07-25", "gender": "male", "address": "45 Nehru Colony Jaipur Raj", "aadhaar_number": "XXXX-XXXX-3344"}
            },
            {
                "type": "income_certificate", "source": "Income Certificate",
                "extracted": {"full_name": "Mohan Lal Sharma", "income_monthly": 12500.0}
            }
        ],
        "expected_risk": "medium",
        "expected_score": 32,
        "fraud_label": False
    },
    {
        "id": "APP-005",
        "declared": {
            "full_name": "Priya Singh",
            "date_of_birth": "1995-03-10",
            "gender": "female",
            "address": "12 Laxmi Nagar, Bhopal, MP 462001",
            "aadhaar_number": "XXXX-XXXX-5566",
            "income_monthly": 6000.0,
            "bank_account": "XXXXXXXXXX2233",
            "phone": "XXXXXX4455",
            "scheme": "Ujjwala Yojana",
            "state": "Madhya Pradesh",
            "district": "Bhopal"
        },
        "documents": [
            {
                "type": "aadhaar", "source": "Aadhaar Card",
                "extracted": {"full_name": "Priya Kumari Singh", "date_of_birth": "1995-03-10", "gender": "female", "address": "12 Laxmi Ngr Bhopal 462001"}
            },
            {
                "type": "bank_statement", "source": "Bank Statement",
                "extracted": {"full_name": "Priya Singh", "income_monthly": 10200.0, "bank_account": "XXXXXXXXXX2233"}
            }
        ],
        "expected_risk": "medium",
        "expected_score": 28,
        "fraud_label": False
    },
    {
        "id": "APP-006",
        "declared": {
            "full_name": "Gopal Krishna Reddy",
            "date_of_birth": "1978-12-05",
            "gender": "male",
            "address": "78 Tank Bund Road, Hyderabad, Telangana 500001",
            "aadhaar_number": "XXXX-XXXX-7788",
            "income_monthly": 11000.0,
            "bank_account": "XXXXXXXXXX3344",
            "phone": "XXXXXX6677",
            "scheme": "MGNREGS",
            "state": "Telangana",
            "district": "Hyderabad"
        },
        "documents": [
            {
                "type": "aadhaar", "source": "Aadhaar Card",
                "extracted": {"full_name": "G. Krishna Reddy", "date_of_birth": "1978-12-05", "gender": "male", "address": "78 Tankbund Rd, Hyderabad"}
            },
            {
                "type": "income_certificate", "source": "Income Certificate",
                "extracted": {"full_name": "Gopal Krishna Reddy", "income_monthly": 18500.0, "address": "78 Tank Bund Road Hyderabad"}
            }
        ],
        "expected_risk": "medium",
        "expected_score": 35,
        "fraud_label": False
    },

    # ── High-risk fraud signals ──
    {
        "id": "APP-007",
        "declared": {
            "full_name": "Rakesh Mishra",
            "date_of_birth": "1985-06-15",
            "gender": "male",
            "address": "99 Civil Lines, Allahabad, UP 211001",
            "aadhaar_number": "XXXX-XXXX-1122",
            "income_monthly": 7000.0,
            "bank_account": "XXXXXXXXXX5566",
            "phone": "XXXXXX7788",
            "scheme": "PM-KISAN",
            "state": "Uttar Pradesh",
            "district": "Prayagraj"
        },
        "documents": [
            {
                "type": "aadhaar", "source": "Aadhaar Card",
                "extracted": {"full_name": "Rakesh Kumar", "date_of_birth": "1983-06-15", "gender": "male", "address": "Plot 99 Civil Lines Allahabad", "aadhaar_number": "XXXX-XXXX-1122"}
            },
            {
                "type": "income_certificate", "source": "Income Certificate",
                "extracted": {"full_name": "Rakesh Mishra", "income_monthly": 24000.0}
            },
            {
                "type": "bank_statement", "source": "Bank Statement",
                "extracted": {"full_name": "R. Mishra", "income_monthly": 28500.0, "bank_account": "XXXXXXXXXX5566"}
            }
        ],
        "expected_risk": "high",
        "expected_score": 72,
        "fraud_label": True
    },
    {
        "id": "APP-008",
        "declared": {
            "full_name": "Kavita Joshi",
            "date_of_birth": "1992-09-28",
            "gender": "female",
            "address": "34 Shivaji Nagar, Pune, Maharashtra 411001",
            "aadhaar_number": "XXXX-XXXX-9900",
            "income_monthly": 5500.0,
            "bank_account": "XXXXXXXXXX8877",
            "phone": "XXXXXX1199",
            "scheme": "Ujjwala Yojana",
            "state": "Maharashtra",
            "district": "Pune"
        },
        "documents": [
            {
                "type": "aadhaar", "source": "Aadhaar Card",
                "extracted": {"full_name": "Kavitha B Joshi", "date_of_birth": "1990-09-28", "gender": "female", "address": "34 Shivaji Ngr Pune 411001"}
            },
            {
                "type": "income_certificate", "source": "Income Certificate",
                "extracted": {"full_name": "Kavita Joshi", "income_monthly": 22000.0, "address": "54 MG Road, Mumbai"}
            }
        ],
        "expected_risk": "high",
        "expected_score": 68,
        "fraud_label": True
    },
    {
        "id": "APP-009",
        "declared": {
            "full_name": "Deepak Patel",
            "date_of_birth": "1980-04-02",
            "gender": "male",
            "address": "67 Ashram Road, Ahmedabad, Gujarat 380001",
            "aadhaar_number": "XXXX-XXXX-4455",
            "income_monthly": 6500.0,
            "bank_account": "XXXXXXXXXX1100",
            "phone": "XXXXXX2233",
            "scheme": "PM-KISAN",
            "state": "Gujarat",
            "district": "Ahmedabad"
        },
        "documents": [
            {
                "type": "aadhaar", "source": "Aadhaar Card",
                "extracted": {"full_name": "Dipak R Patel", "date_of_birth": "1980-04-02", "gender": "male", "address": "67 Ashram Rd Ahmedabad"}
            },
            {
                "type": "income_certificate", "source": "Income Certificate",
                "extracted": {"full_name": "Deepak Ramesh Patel", "income_monthly": 45000.0}
            },
            {
                "type": "bank_statement", "source": "Bank Statement",
                "extracted": {"full_name": "Deepak R Patel", "income_monthly": 52000.0, "bank_account": "XXXXXXXXXX1100"}
            }
        ],
        "expected_risk": "critical",
        "expected_score": 85,
        "fraud_label": True
    },
    {
        "id": "APP-010",
        "declared": {
            "full_name": "Lakshmi Narayanan",
            "date_of_birth": "1970-08-18",
            "gender": "male",
            "address": "23 Anna Salai, Chennai, Tamil Nadu 600001",
            "aadhaar_number": "XXXX-XXXX-6677",
            "income_monthly": 8000.0,
            "bank_account": "XXXXXXXXXX9988",
            "phone": "XXXXXX4455",
            "scheme": "MGNREGS",
            "state": "Tamil Nadu",
            "district": "Chennai"
        },
        "documents": [
            {
                "type": "aadhaar", "source": "Aadhaar Card",
                "extracted": {"full_name": "L. Narayanan", "date_of_birth": "1972-08-18", "gender": "male", "address": "23 Anna Salai Chennai 600001"}
            },
            {
                "type": "income_certificate", "source": "Income Certificate",
                "extracted": {"full_name": "Lakshmi Narayanan S", "income_monthly": 35000.0, "address": "55 Mount Road, Chennai"}
            },
            {
                "type": "bank_statement", "source": "Bank Statement",
                "extracted": {"full_name": "Lakshmi N", "income_monthly": 41000.0}
            }
        ],
        "expected_risk": "critical",
        "expected_score": 90,
        "fraud_label": True
    },

    # ── More clean / minor cases to fill the dashboard ──
    {
        "id": "APP-011",
        "declared": {"full_name": "Meena Kumari", "date_of_birth": "1993-02-14", "gender": "female", "address": "8 Rajaji Street, Madurai, TN 625001", "aadhaar_number": "XXXX-XXXX-1234", "income_monthly": 4500.0, "bank_account": "XXXXXXXXXX5678", "phone": "XXXXXX9012", "scheme": "Ujjwala Yojana", "state": "Tamil Nadu", "district": "Madurai"},
        "documents": [{"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Meena Kumari", "date_of_birth": "1993-02-14", "gender": "female", "address": "8 Rajaji St Madurai 625001"}}],
        "expected_risk": "low", "expected_score": 5, "fraud_label": False
    },
    {
        "id": "APP-012",
        "declared": {"full_name": "Bharat Singh Thakur", "date_of_birth": "1987-10-03", "gender": "male", "address": "14 Mall Road, Shimla, HP 171001", "aadhaar_number": "XXXX-XXXX-5678", "income_monthly": 7200.0, "bank_account": "XXXXXXXXXX9012", "phone": "XXXXXX3456", "scheme": "PM-KISAN", "state": "Himachal Pradesh", "district": "Shimla"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Bharat S Thakur", "date_of_birth": "1987-10-03", "gender": "male"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Bharat Singh Thakur", "income_monthly": 7500.0}}
        ],
        "expected_risk": "low", "expected_score": 8, "fraud_label": False
    },
    {
        "id": "APP-013",
        "declared": {"full_name": "Fatima Begum", "date_of_birth": "1968-06-22", "gender": "female", "address": "56 Charminar Road, Hyderabad, TS 500002", "aadhaar_number": "XXXX-XXXX-3456", "income_monthly": 3500.0, "bank_account": "XXXXXXXXXX7890", "phone": "XXXXXX1234", "scheme": "Ujjwala Yojana", "state": "Telangana", "district": "Hyderabad"},
        "documents": [{"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Fatima Begum", "date_of_birth": "1968-06-22", "gender": "female", "address": "56 Charminar Rd Hyderabad"}}],
        "expected_risk": "low", "expected_score": 3, "fraud_label": False
    },
    {
        "id": "APP-014",
        "declared": {"full_name": "Vikram Chauhan", "date_of_birth": "1991-12-30", "gender": "male", "address": "101 Station Road, Indore, MP 452001", "aadhaar_number": "XXXX-XXXX-7890", "income_monthly": 9500.0, "bank_account": "XXXXXXXXXX2345", "phone": "XXXXXX6789", "scheme": "MGNREGS", "state": "Madhya Pradesh", "district": "Indore"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Vikram Singh Chauhan", "date_of_birth": "1991-12-30", "gender": "male"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Vikram Chauhan", "income_monthly": 16000.0}}
        ],
        "expected_risk": "medium", "expected_score": 25, "fraud_label": False
    },
    {
        "id": "APP-015",
        "declared": {"full_name": "Sanjay Gupta", "date_of_birth": "1976-03-08", "gender": "male", "address": "29 Park Street, Kolkata, WB 700016", "aadhaar_number": "XXXX-XXXX-2345", "income_monthly": 6800.0, "bank_account": "XXXXXXXXXX6789", "phone": "XXXXXX0123", "scheme": "PM-KISAN", "state": "West Bengal", "district": "Kolkata"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Sanjay K Gupta", "date_of_birth": "1974-03-08", "gender": "male", "address": "29 Park St Kolkata"}},
            {"type": "bank_statement", "source": "Bank Statement", "extracted": {"full_name": "S. Gupta", "income_monthly": 32000.0}}
        ],
        "expected_risk": "high", "expected_score": 65, "fraud_label": True
    },
    {
        "id": "APP-016",
        "declared": {"full_name": "Asha Rani", "date_of_birth": "1984-07-19", "gender": "female", "address": "7 Lajpat Nagar, New Delhi 110024", "aadhaar_number": "XXXX-XXXX-6789", "income_monthly": 5200.0, "bank_account": "XXXXXXXXXX0123", "phone": "XXXXXX4567", "scheme": "Ujjwala Yojana", "state": "Delhi", "district": "South Delhi"},
        "documents": [{"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Asha Rani", "date_of_birth": "1984-07-19", "gender": "female", "address": "7 Lajpat Nagar Delhi 110024"}}],
        "expected_risk": "low", "expected_score": 4, "fraud_label": False
    },
    {
        "id": "APP-017",
        "declared": {"full_name": "Manoj Tiwari", "date_of_birth": "1989-11-11", "gender": "male", "address": "33 Hazratganj, Lucknow, UP 226001", "aadhaar_number": "XXXX-XXXX-8901", "income_monthly": 8800.0, "bank_account": "XXXXXXXXXX4567", "phone": "XXXXXX8901", "scheme": "MGNREGS", "state": "Uttar Pradesh", "district": "Lucknow"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Manoj K Tiwari", "date_of_birth": "1989-11-11", "gender": "male"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Manoj Tiwari", "income_monthly": 9100.0}},
            {"type": "bank_statement", "source": "Bank Statement", "extracted": {"full_name": "Manoj Tiwari", "income_monthly": 9500.0}}
        ],
        "expected_risk": "low", "expected_score": 6, "fraud_label": False
    },
    {
        "id": "APP-018",
        "declared": {"full_name": "Ravi Shankar Dubey", "date_of_birth": "1965-04-25", "gender": "male", "address": "12 Dashashwamedh, Varanasi, UP 221001", "aadhaar_number": "XXXX-XXXX-0123", "income_monthly": 4200.0, "bank_account": "XXXXXXXXXX8901", "phone": "XXXXXX2345", "scheme": "PM-KISAN", "state": "Uttar Pradesh", "district": "Varanasi"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Ravishankar Dubey", "date_of_birth": "1965-04-25", "gender": "male", "address": "12 Dashashwamedh Ghat Varanasi"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Ravi Shankar Dubey", "income_monthly": 4000.0}}
        ],
        "expected_risk": "low", "expected_score": 7, "fraud_label": False
    },
    {
        "id": "APP-019",
        "declared": {"full_name": "Pooja Mehta", "date_of_birth": "1997-01-30", "gender": "female", "address": "88 CG Road, Ahmedabad, Gujarat 380006", "aadhaar_number": "XXXX-XXXX-4567", "income_monthly": 7800.0, "bank_account": "XXXXXXXXXX2345", "phone": "XXXXXX6789", "scheme": "Ujjwala Yojana", "state": "Gujarat", "district": "Ahmedabad"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Pooja B Mehta", "date_of_birth": "1997-01-30", "gender": "female"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Pooja Mehta", "income_monthly": 7500.0}}
        ],
        "expected_risk": "low", "expected_score": 5, "fraud_label": False
    },
    {
        "id": "APP-020",
        "declared": {"full_name": "Abdul Rahman Khan", "date_of_birth": "1973-09-14", "gender": "male", "address": "45 Aminabad, Lucknow, UP 226018", "aadhaar_number": "XXXX-XXXX-5678", "income_monthly": 5000.0, "bank_account": "XXXXXXXXXX6789", "phone": "XXXXXX0123", "scheme": "MGNREGS", "state": "Uttar Pradesh", "district": "Lucknow"},
        "documents": [
            {"type": "aadhaar", "source": "Aadhaar Card", "extracted": {"full_name": "Abdul R Khan", "date_of_birth": "1973-09-14", "gender": "male", "address": "45 Aminabad Lucknow 226018"}},
            {"type": "income_certificate", "source": "Income Certificate", "extracted": {"full_name": "Abdul Rahman Khan", "income_monthly": 38000.0}},
            {"type": "bank_statement", "source": "Bank Statement", "extracted": {"full_name": "A.R. Khan", "income_monthly": 42000.0}}
        ],
        "expected_risk": "critical", "expected_score": 88, "fraud_label": True
    },
]
