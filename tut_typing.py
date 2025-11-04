from typing import List, Optional

def get_names(user_ids: List[int]) -> Optional[List[str]]:
    """Return a list of names for given user IDs, or None if no users found."""
    if not user_ids:
        return None # Allowed because return type is Optional[List[str]]
    return [f"User {uid}" for uid in user_ids]

if __name__ == "__main__":
    ids = [1, 2, 3]
    names = get_names(ids)
    if names is not None:
        for name in names:
            print(name)
    else:
        print("No users found.")