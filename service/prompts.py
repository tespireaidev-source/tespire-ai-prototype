ROLE_PROMPTS = {
    "owner": {
        "operational": [
            "What is the enrolment rate this term?",
            "How much fees are outstanding this term?",
        ],
        "academic": [
            "What is the overall performance average this term?",
            "Which classes are underperforming?",
        ],
        "actionable": [
            "Which students are at risk academically?",
            "Which classes have low attendance?"
        ]
    },
    "admin": {
        "operational": [
            "What is the enrolment rate this term?",
            "How much fees are outstanding this term?",
        ],
        "academic": [
            "What is the overall performance average this term?",
        ],
        "actionable": [
            "Which classes have low attendance?"
        ]
    },
    "teacher": {
        "academic": [
            "What is my class performance this term?",
            "Which students need improvement?"
        ],
        "operational": [
            "What is attendance rate this term?"
        ],
        "actionable": [
            "Which students are below average?"
        ]
    },
    "parent": {
        "academic": [
            "What is my child's performance this term?",
        ],
        "operational": [
            "What is my child's attendance rate?",
        ],
        "actionable": [
            "Is my child at academic risk?"
        ]
    }
}


def get_guided_prompts(role: str):
    return ROLE_PROMPTS.get(role, {})