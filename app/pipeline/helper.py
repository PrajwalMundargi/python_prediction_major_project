from app.common.database import SessionLocal
from app.models.gsoc_organizations import GSoCOrganization  # your main org table
from app.services.github_service import extract_org_name_from_url


def get_organization_list(start_from_id=None):
    """Fetch GitHub organization identifiers from gsoc_organizations table.
    
    Args:
        start_from_id: Optional organization ID to start from (inclusive).
    """
    with SessionLocal() as session:
        query = session.query(
            GSoCOrganization.id,
            GSoCOrganization.name,
            GSoCOrganization.github_url,
            GSoCOrganization.slug,
        )
        
        if start_from_id is not None:
            query = query.filter(GSoCOrganization.id >= start_from_id)
            print(f"Filtering organizations with ID >= {start_from_id}")
        
        query = query.order_by(GSoCOrganization.id)
        orgs = query.all()
        if orgs:
            print(f"First organization ID in query result: {orgs[0][0]}")

    normalized_orgs = []
    skipped_without_identifier = 0
    seen_slugs = set()

    for org_id, name, github_url, slug in orgs:
        display_name = name or slug or "Unknown"
        github_slug = extract_org_name_from_url(github_url) if github_url else None

        if not github_slug and slug:
            candidate = slug.strip().strip("/")
            candidate = candidate.split("/")[-1]
            github_slug = candidate

        if github_slug:
            github_slug = github_slug.lstrip("@").replace(" ", "-").lower()
            if github_slug.endswith(".git"):
                github_slug = github_slug[:-4]

        if not github_slug:
            skipped_without_identifier += 1
            continue

        if github_slug in seen_slugs:
            continue

        seen_slugs.add(github_slug)
        normalized_orgs.append({
            "id": org_id,
            "display_name": display_name,
            "github_slug": github_slug,
        })

    if skipped_without_identifier:
        print(f"WARNING: Skipped {skipped_without_identifier} organizations without GitHub identifiers.")

    # Filter again after normalization to ensure we only return orgs >= start_from_id
    if start_from_id is not None:
        normalized_orgs = [org for org in normalized_orgs if org["id"] >= start_from_id]
        if normalized_orgs:
            print(f"After normalization, first organization ID: {normalized_orgs[0]['id']}")

    return normalized_orgs
