from service.database import supabase


def tenant_query(table: str, tenant_id: int):
    """
    Creates a Supabase query already scoped to a tenant (school).

    This prevents cross-school data leakage.
    """

    return (
        supabase
        .table(table)
        .eq("tenant_id", tenant_id)
    )