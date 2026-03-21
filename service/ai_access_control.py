AI_ROLE_ACCESS = {}


def get_default_policy():
    return {
        "owner": True,
        "admin": True,
        "teacher": False,
        "parent": False
    }


def is_ai_enabled_for_role(school_id: int, role: str) -> bool:

    role = role.lower()

    if school_id not in AI_ROLE_ACCESS:
        
        AI_ROLE_ACCESS[school_id] = get_default_policy().copy()

    policy = AI_ROLE_ACCESS[school_id]

    return policy.get(role, False)
