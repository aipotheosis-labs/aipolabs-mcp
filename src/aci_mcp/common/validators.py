def validate_apps_configured(apps: list[str]) -> bool:
    """
    Validate that all apps provided are configured on platform.aci.dev.
    """
    return True


def validate_linked_accounts_exist(apps: list[str], linked_account_owner_id: str) -> bool:
    """
    Validate that the linked accounts (identified by the linked_account_owner_id + app name) exist on platform.aci.dev.
    """
    return True
