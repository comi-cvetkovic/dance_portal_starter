def is_judge_account(user):
    if not getattr(user, "is_authenticated", False):
        return False
    username = (getattr(user, "username", "") or "").strip()
    if username.startswith("judge_"):
        return True
    try:
        if getattr(user, "is_judge", False):
            return True
        return user.groups.filter(name__iexact="judges").exists()
    except Exception:
        return False


def judge_event_id_from_username(username):
    try:
        parts = (username or "").split("_")
        if len(parts) >= 3 and parts[0] == "judge":
            return int(parts[1])
    except Exception:
        return None
    return None
