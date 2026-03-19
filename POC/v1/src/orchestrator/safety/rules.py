"""Definitions of non-negotiable clinical safety rules and constraints."""

# Gender-specific tests that should NOT be recommended for the opposite gender
GENDER_EXCLUSIONS = {
    "male": ["mammogram", "pap smear", "cervical", "ovarian", "pregnancy test"],
    "female": ["prostate", "testicular"],
}

# Mandatory screenings based on age thresholds
AGE_BASED_MANDATORY_TESTS = {
    50: ["colonoscopy"],
    40: ["lipid profile", "blood glucose"],
}

# Mapping of risk signal counts to minimum allowed tier
MINIMUM_TIER_RULES = {
    2: "Advanced",  # 2 or more high-risk signals require at least Advanced
    3: "Premium",  # 3 or more high-risk signals require at least Premium
}

# Tier weight for comparison logic
TIER_WEIGHTS = {
    "Standard": 1,
    "Advanced": 2,
    "Premium": 3,
}
