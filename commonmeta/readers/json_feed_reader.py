"""JSON Feed reader for commonmeta-py"""
from typing import Optional
import requests
from pydash import py_

from ..utils import (
    compact,
    normalize_url,
    from_json_feed,
    wrap,
    dict_to_spdx,
    name_to_fos,
)
from ..author_utils import get_authors
from ..base_utils import presence, sanitize, parse_attributes
from ..date_utils import get_date_from_unix_timestamp
from ..doi_utils import normalize_doi, validate_prefix
from ..constants import Commonmeta


def get_json_feed_item(pid: str, **kwargs) -> dict:
    """get_json_feed_item"""
    if pid is None:
        return {"state": "not_found"}
    url = normalize_url(pid)
    response = requests.get(url, kwargs, timeout=10)
    if response.status_code != 200:
        return {"state": "not_found"}
    return response.json()


def read_json_feed_item(data: Optional[dict], **kwargs) -> Commonmeta:
    """read_json_feed_item"""
    if data is None:
        return {"state": "not_found"}
    meta = data
    read_options = kwargs or {}

    url = normalize_url(meta.get("url", None))
    id_ = normalize_doi(read_options.get("doi", None) or meta.get("doi", None)) or url
    type_ = "Article"

    if meta.get("authors", None):
        contributors = get_authors(from_json_feed(wrap(meta.get("authors"))))
    else:
        contributors = [{"type": "Organization", "name": ":(unav)"}]

    title = parse_attributes(meta.get("title", None))
    titles = [{"title": sanitize(title)}] if title else None

    publisher = py_.get(meta, "blog.title", None)
    if publisher is not None:
        publisher = {"name": publisher}

    date: dict = {}
    date["published"] = (
        get_date_from_unix_timestamp(meta.get("published_at", None))
        if meta.get("published_at", None)
        else None
    )
    date["updated"] = (
        get_date_from_unix_timestamp(meta.get("updated_at", None))
        if meta.get("updated_at", None)
        else None
    )

    license_ = py_.get(meta, "blog.license", None)
    if license_ is not None:
        license_ = dict_to_spdx({"url": license_})

    container = compact(
        {
            "type": "Periodical",
            "title": py_.get(meta, "blog.title", None),
            "identifier": py_.get(meta, "blog.issn", None),
            "identifierType": "ISSN" if py_.get(meta, "blog.issn", None) else None,
        }
    )

    description = meta.get("summary", None)
    if description is not None:
        descriptions = [
            {"description": sanitize(description), "descriptionType": "Abstract"}
        ]
    else:
        descriptions = None
    category = py_.get(meta, "blog.category", None)
    if category is not None:
        subjects = [name_to_fos(py_.human_case(category))]
    references = [get_reference(i) for i in wrap(meta.get("reference", None))]
    funding_references = get_funding_references(meta)
    related_identifiers = get_related_identifiers(wrap(meta.get("relationships", None)))
    alternate_identifiers = [
        {"alternateIdentifier": meta.get("id"), "alternateIdentifierType": "UUID"}
    ]
    state = "findable" if meta or read_options else "not_found"

    return {
        # required properties
        "id": id_,
        "type": type_,
        "url": url,
        "contributors": contributors,
        "titles": presence(titles),
        "publisher": publisher,
        "date": compact(date),
        # recommended and optional properties
        "subjects": presence(subjects),
        "language": meta.get("language", None),
        "alternate_identifiers": alternate_identifiers,
        "sizes": None,
        "formats": None,
        "version": None,
        "license": license_,
        "descriptions": descriptions,
        "geo_locations": None,
        "funding_references": presence(funding_references),
        "references": references,
        "related_identifiers": presence(related_identifiers),
        # other properties
        "container": presence(container),
        # "provider": get_doi_ra(id_),
        "state": state,
        "schema_version": None,
    } | read_options


def get_reference(reference: Optional[dict]) -> Optional[dict]:
    """get json feed reference"""
    if reference is None or not isinstance(reference, dict):
        return None
    doi = reference.get("doi", None)
    metadata = {
        "key": reference.get("key", None),
        "doi": normalize_doi(doi) if doi else None,
        "title": None,
        "publicationYear": None,
        "url": reference.get("url", None) if doi is None else None,
    }
    return compact(metadata)


def get_funding_references(meta: Optional[dict]) -> Optional[list]:
    """get json feed funding references.
    Check that relationships resolve and have type "HasAward" or 
    funding is provided by blog metadata"""
    
    if meta is None or not isinstance(meta, dict):
        return None
        
    def format_funding(url: str) -> dict:
        """format funding. Prefix 10.3030 means funder is European Commission"""
        print(url)
        return {
            "funderName": "European Commission",
            "funderIdentifier": "https://doi.org/10.13039/501100000780",
            "funderIdentifierType": "Crossref Funder ID",
            "awardNumber": url.split("/")[-1],
        }
        
    awards = [
        format_funding(i.get("url"))
        for i in wrap(meta.get("relationships", None))
        if i.get("type", None) == "HasAward" and validate_prefix(i.get("url", None)) == "10.3030"
    ]
    funding = py_.get(meta, "blog.funding", None)
    if funding is not None:
        awards += [{
            "funderName": funding.get("funder_name", None),
            "funderIdentifier": funding.get("funder_id", None),
            "funderIdentifierType": "Crossref Funder ID",
            "awardTitle": funding.get("award", None),
            "awardNumber": funding.get("award_number", None),
        }]
    return awards


def get_related_identifiers(relationships: Optional[list]) -> Optional[list]:
    """get json feed related identifiers.
    Check that relationships resolve and has a supported type"""
    supported_types = ["IsIdenticalTo", "IsPreprintOf", "IsTranslationOf"]

    def format_relationship(relationship: dict) -> dict:
        """format relationship"""
        return {
            "id": relationship.get("url", None),
            "type": relationship.get("type", None),
        }

    return [
        format_relationship(i)
        for i in relationships
        if i.get("type", None) in supported_types
    ]
