"""Utils module for commonmeta-py"""
import os
import json
import re
from typing import Optional
from urllib.parse import urlparse
import yaml
from furl import furl
import bibtexparser
from bs4 import BeautifulSoup
from pydash import py_
import base32_lib as base32
import pycountry

from .base_utils import wrap, compact, parse_attributes
from .doi_utils import normalize_doi, doi_from_url, get_doi_ra, validate_doi, doi_as_url
from .constants import DATACITE_CONTRIBUTOR_TYPES

NORMALIZED_LICENSES = {
    "https://creativecommons.org/licenses/by/1.0": "https://creativecommons.org/licenses/by/1.0/legalcode",
    "https://creativecommons.org/licenses/by/2.0": "https://creativecommons.org/licenses/by/2.0/legalcode",
    "https://creativecommons.org/licenses/by/2.5": "https://creativecommons.org/licenses/by/2.5/legalcode",
    "https://creativecommons.org/licenses/by/3.0": "https://creativecommons.org/licenses/by/3.0/legalcode",
    "https://creativecommons.org/licenses/by/3.0/us": "https://creativecommons.org/licenses/by/3.0/legalcode",
    "https://creativecommons.org/licenses/by/4.0": "https://creativecommons.org/licenses/by/4.0/legalcode",
    "https://creativecommons.org/licenses/by-nc/1.0": "https://creativecommons.org/licenses/by-nc/1.0/legalcode",
    "https://creativecommons.org/licenses/by-nc/2.0": "https://creativecommons.org/licenses/by-nc/2.0/legalcode",
    "https://creativecommons.org/licenses/by-nc/2.5": "https://creativecommons.org/licenses/by-nc/2.5/legalcode",
    "https://creativecommons.org/licenses/by-nc/3.0": "https://creativecommons.org/licenses/by-nc/3.0/legalcode",
    "https://creativecommons.org/licenses/by-nc/4.0": "https://creativecommons.org/licenses/by-nc/4.0/legalcode",
    "https://creativecommons.org/licenses/by-nd-nc/1.0": "https://creativecommons.org/licenses/by-nd-nc/1.0/legalcode",
    "https://creativecommons.org/licenses/by-nd-nc/2.0": "https://creativecommons.org/licenses/by-nd-nc/2.0/legalcode",
    "https://creativecommons.org/licenses/by-nd-nc/2.5": "https://creativecommons.org/licenses/by-nd-nc/2.5/legalcode",
    "https://creativecommons.org/licenses/by-nd-nc/3.0": "https://creativecommons.org/licenses/by-nd-nc/3.0/legalcode",
    "https://creativecommons.org/licenses/by-nd-nc/4.0": "https://creativecommons.org/licenses/by-nd-nc/4.0/legalcode",
    "https://creativecommons.org/licenses/by-nc-sa/1.0": "https://creativecommons.org/licenses/by-nc-sa/1.0/legalcode",
    "https://creativecommons.org/licenses/by-nc-sa/2.0": "https://creativecommons.org/licenses/by-nc-sa/2.0/legalcode",
    "https://creativecommons.org/licenses/by-nc-sa/2.5": "https://creativecommons.org/licenses/by-nc-sa/2.5/legalcode",
    "https://creativecommons.org/licenses/by-nc-sa/3.0": "https://creativecommons.org/licenses/by-nc-sa/3.0/legalcode",
    "https://creativecommons.org/licenses/by-nc-sa/3.0/us": "https://creativecommons.org/licenses/by-nc-sa/3.0/legalcode",
    "https://creativecommons.org/licenses/by-nc-sa/4.0": "https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode",
    "https://creativecommons.org/licenses/by-nd/1.0": "https://creativecommons.org/licenses/by-nd/1.0/legalcode",
    "https://creativecommons.org/licenses/by-nd/2.0": "https://creativecommons.org/licenses/by-nd/2.0/legalcode",
    "https://creativecommons.org/licenses/by-nd/2.5": "https://creativecommons.org/licenses/by-nd/2.5/legalcode",
    "https://creativecommons.org/licenses/by-nd/3.0": "https://creativecommons.org/licenses/by-nd/3.0/legalcode",
    "https://creativecommons.org/licenses/by-nd/4.0": "https://creativecommons.org/licenses/by-nd/2.0/legalcode",
    "https://creativecommons.org/licenses/by-sa/1.0": "https://creativecommons.org/licenses/by-sa/1.0/legalcode",
    "https://creativecommons.org/licenses/by-sa/2.0": "https://creativecommons.org/licenses/by-sa/2.0/legalcode",
    "https://creativecommons.org/licenses/by-sa/2.5": "https://creativecommons.org/licenses/by-sa/2.5/legalcode",
    "https://creativecommons.org/licenses/by-sa/3.0": "https://creativecommons.org/licenses/by-sa/3.0/legalcode",
    "https://creativecommons.org/licenses/by-sa/4.0": "https://creativecommons.org/licenses/by-sa/4.0/legalcode",
    "https://creativecommons.org/licenses/by-nc-nd/1.0": "https://creativecommons.org/licenses/by-nc-nd/1.0/legalcode",
    "https://creativecommons.org/licenses/by-nc-nd/2.0": "https://creativecommons.org/licenses/by-nc-nd/2.0/legalcode",
    "https://creativecommons.org/licenses/by-nc-nd/2.5": "https://creativecommons.org/licenses/by-nc-nd/2.5/legalcode",
    "https://creativecommons.org/licenses/by-nc-nd/3.0": "https://creativecommons.org/licenses/by-nc-nd/3.0/legalcode",
    "https://creativecommons.org/licenses/by-nc-nd/4.0": "https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode",
    "https://creativecommons.org/licenses/publicdomain": "https://creativecommons.org/licenses/publicdomain/",
    "https://creativecommons.org/publicdomain/zero/1.0": "https://creativecommons.org/publicdomain/zero/1.0/legalcode",
}

UNKNOWN_INFORMATION = {
    ":unac": "temporarily inaccessible",
    ":unal": "unallowed, suppressed intentionally",
    ":unap": "not applicable, makes no sense",
    ":unas": "value unassigned (e.g., Untitled)",
    ":unav": "value unavailable, possibly unknown",
    ":unkn": "known to be unknown (e.g., Anonymous, Inconnue)",
    ":none": "never had a value, never will",
    ":null": "explicitly and meaningfully empty",
    ":tba": "to be assigned or announced later",
    ":etal": "too numerous to list (et alia)",
}

HTTP_SCHEME = "http://"
HTTPS_SCHEME = "https://"


def normalize_id(pid: Optional[str], **kwargs) -> Optional[str]:
    """Check for valid DOI or HTTP(S) URL"""
    if pid is None:
        return None

    # check if pid is a bytes object
    if isinstance(pid, (bytes, bytearray)):
        pid = pid.decode()

    # check for valid DOI
    doi = normalize_doi(pid, **kwargs)
    if doi is not None:
        return doi

    # check for valid HTTP uri and ensure https
    uri = urlparse(pid)
    if not uri.netloc or uri.scheme not in ["http", "https"]:
        return None
    if uri.scheme == "http":
        pid = pid.replace(HTTP_SCHEME, HTTPS_SCHEME)

    # remove trailing slash
    if pid.endswith("/"):
        pid = pid.strip("/")

    return pid


def normalize_ids(ids: list, relation_type=None) -> list:
    """Normalize identifiers"""

    def format_id(i):
        if i.get("id", None):
            idn = normalize_id(i["id"])
            doi = doi_from_url(idn)
            related_identifier_type = "DOI" if doi is not None else "URL"
            idn = doi or idn
            type_ = (
                i.get("type")
                if isinstance(i.get("type", None), str)
                else wrap(i.get("type", None))[0]
            )
            return compact(
                {
                    "relatedIdentifier": idn,
                    "relationType": relation_type,
                    "relatedIdentifierType": related_identifier_type,
                }
            )
        return None

    return [format_id(i) for i in ids]


def normalize_url(url: Optional[str], secure=False, lower=False) -> Optional[str]:
    """Normalize URL"""
    if url is None or not isinstance(url, str):
        return None
    if url.endswith("/"):
        url = url.strip("/")
    if secure is True and url.startswith(HTTP_SCHEME):
        url = url.replace(HTTP_SCHEME, HTTPS_SCHEME)
    if lower is True:
        return url.lower()
    return url


def normalize_cc_url(url: Optional[str]):
    """Normalize Creative Commons URL"""
    if url is None or not isinstance(url, str):
        return None
    url = normalize_url(url, secure=True)
    return NORMALIZED_LICENSES.get(url, url)


def normalize_ror(ror: Optional[str]) -> Optional[str]:
    """Normalize ROR ID"""
    ror = validate_ror(ror)
    if ror is None:
        return None

    # turn ROR ID into URL
    return "https://ror.org/" + ror


def validate_ror(ror: Optional[str]) -> Optional[str]:
    """Validate ROR"""
    if ror is None or not isinstance(ror, str):
        return None
    match = re.search(
        r"\A(?:(?:http|https)://ror\.org/)?([0-9a-z]{7}\d{2})\Z",
        ror,
    )
    if match is None:
        return None
    ror = match.group(1).replace(" ", "-")
    return ror


def validate_url(url: str) -> Optional[str]:
    if url is None:
        return None
    elif validate_doi(url):
        return "DOI"
    f = furl(url)
    if f and f.scheme in ["http", "https"]:
        return "URL"
    match = re.search(
        r"\A(ISSN|eISSN) (\d{4}-\d{3}[0-9X]+)\Z",
        url,
    )
    if match is not None:
        return "ISSN"
    return None


def normalize_orcid(orcid: Optional[str]) -> Optional[str]:
    """Normalize ORCID"""
    if orcid is None or not isinstance(orcid, str):
        return None
    orcid = validate_orcid(orcid)
    if orcid is None:
        return None
    return "https://orcid.org/" + orcid


def validate_orcid(orcid: Optional[str]) -> Optional[str]:
    """Validate ORCID"""
    if orcid is None or not isinstance(orcid, str):
        return None
    match = re.search(
        r"\A(?:(?:http|https)://(?:(?:www|sandbox)?\.)?orcid\.org/)?(\d{4}[ -]\d{4}[ -]\d{4}[ -]\d{3}[0-9X]+)\Z",
        orcid,
    )
    if match is None:
        return None
    orcid = match.group(1).replace(" ", "-")
    return orcid


def validate_isni(isni: Optional[str]) -> Optional[str]:
    """Validate ISNI"""
    if isni is None or not isinstance(isni, str):
        return None
    match = re.search(
        r"\A(?:(?:http|https)://isni\.org/isni/)?(\d{4}([ -])?\d{4}([ -])?\d{4}([ -])?\d{3}[0-9X]+)\Z",
        isni,
    )
    if match is None:
        return None
    isni = match.group(1).replace(" ", "")
    return isni


def normalize_isni(isni: Optional[str]) -> Optional[str]:
    """Normalize ISNI"""
    if isni is None or not isinstance(isni, str):
        return None
    isni = validate_isni(isni)
    if isni is None:
        return None
    return "https://isni.org/isni/" + isni


def normalize_name_identifier(ni: Optional[str]) -> Optional[str]:
    """Normalize name identifier"""
    if ni is None:
        return None
    if isinstance(ni, str):
        return
    if isinstance(ni, dict):
        return format_name_identifier(ni)
    if isinstance(ni, list):
        return next(
            (format_name_identifier(i) for i in wrap(ni.get("nameIdentifiers", None))),
            None,
        )
    return None


def format_name_identifier(ni):
    """format_name_identifier"""
    if ni is None:
        return None
    elif isinstance(ni, str):
        return normalize_orcid(ni) or normalize_ror(ni) or normalize_isni(ni)
    name_identifier = ni.get("nameIdentifier", None) or ni.get(
        "publisherIdentifier", None
    )
    name_identifier_scheme = ni.get("nameIdentifierScheme", None) or ni.get(
        "publisherIdentifierScheme", None
    )
    scheme_uri = ni.get("schemeURI", None) or ni.get("schemeUri", None)
    if name_identifier is None:
        return None
    elif name_identifier_scheme == "ORCID":
        return normalize_orcid(name_identifier)
    elif name_identifier_scheme == "ISNI":
        return normalize_isni(name_identifier)
    elif name_identifier_scheme == "ROR":
        return normalize_ror(name_identifier)
    elif validate_url(name_identifier) == "URL":
        return name_identifier
    elif isinstance(name_identifier, str) and scheme_uri is not None:
        return scheme_uri + name_identifier
    return None


def normalize_issn(string, **kwargs):
    """Normalize ISSN
    Pick electronic issn if there are multiple
    Format issn as xxxx-xxxx"""
    content = kwargs.get("content", "#text")
    if string is None:
        return None
    if isinstance(string, str):
        issn = string
    elif isinstance(string, dict):
        issn = string.get(content, None)
    elif isinstance(string, list):
        issn = next(
            (i for i in string if i.get("media_type", None) == "electronic"), {}
        ).get(content, None)
    if issn is None:
        return None
    if len(issn) == 9:
        return issn
    if len(issn) == 8:
        return issn[0:4] + "-" + issn[4:8]
    return None


def dict_to_spdx(dct: dict) -> dict:
    """Convert a dict to SPDX"""
    dct.update({"url": normalize_cc_url(dct.get("url", None))})
    file_path = os.path.join(
        os.path.dirname(__file__), "resources", "spdx", "licenses.json"
    )
    with open(file_path, encoding="utf-8") as json_file:
        spdx = json.load(json_file).get("licenses")
    license_ = next(
        (
            lic
            for lic in spdx
            if lic["licenseId"].casefold() == dct.get("id", "").casefold()
            or lic["seeAlso"][0] == dct.get("url", None)
        ),
        None,
    )
    if license_ is None:
        return dct
    #   license = spdx.find do |l|
    #     l['licenseId'].casecmp?(hsh['rightsIdentifier']) || l['seeAlso'].first == normalize_cc_url(hsh['rightsUri']) || l['name'] == hsh['rights'] || l['seeAlso'].first == normalize_cc_url(hsh['rights'])
    #   end
    return compact(
        {
            "id": license_["licenseId"],
            "url": license_["seeAlso"][0],
        }
    )

    #   else
    #     {
    #       'rights': hsh['#text'] || hsh['rights'],
    #       'rightsUri': hsh['rightsUri'] || hsh['rightsUri'],
    #       'rightsIdentifier': hsh['rightsIdentifier'].present? ? hsh['rightsIdentifier'].downcase : None,
    #       'rightsIdentifierScheme': hsh['rightsIdentifierScheme'],
    #       'schemeUri': hsh['schemeUri'],
    #       'lang': hsh['lang']
    #     }.compact
    #   end
    # end


def from_json_feed(elements: list) -> list:
    """Convert from JSON Feed elements"""

    def format_element(element):
        """format element"""
        if not isinstance(element, dict):
            return None
        mapping = {"url": "id"}
        for key, value in mapping.items():
            if element.get(key, None) is not None:
                element[value] = element.pop(key)
        return element

    return [format_element(i) for i in elements]


def from_inveniordm(elements: list) -> list:
    """Convert from inveniordm elements"""

    def format_element(element):
        """format element"""
        if not isinstance(element, dict):
            return None
        mapping = {"orcid": "ORCID"}
        for key, value in mapping.items():
            if element.get(key, None) is not None:
                element[value] = element.pop(key)
        return element

    return [format_element(i) for i in elements]


def from_crossref_xml(elements: list) -> list:
    """Convert from crossref_xml elements"""

    def format_affiliation(element):
        """Format affiliation"""
        return {"name": element}

    def format_element(element):
        """format element"""
        if element.get("name", None) is not None:
            element["type"] = "Organization"
            element["name"] = element.get("name")
        else:
            element["type"] = "Person"
        element["givenName"] = element.get("given_name", None)
        element["familyName"] = element.get("surname", None)
        element["contributorType"] = element.get(
            "contributor_role", "author"
        ).capitalize()
        if element.get("ORCID", None) is not None:
            orcid = parse_attributes(element.get("ORCID"))
            element["ORCID"] = normalize_orcid(orcid)
        element = py_.omit(
            element, "given_name", "surname", "sequence", "contributor_role"
        )
        return compact(element)

    return [format_element(i) for i in elements]


def from_kbase(elements: list) -> list:
    """Convert from kbase elements"""

    def map_contributor_role(role):
        if role.split(":")[0] == "CRediT":
            return py_.pascal_case(role.split(":")[1])
        elif role.split(":")[0] == "DataCite":
            return DATACITE_CONTRIBUTOR_TYPES.get(role.split(":")[1], "Other")
        else:
            return role.split(":")[1]

    def format_element(element):
        """format element"""
        if not isinstance(element, dict):
            return None
        if element.get("contributor_id", None) is not None:
            element["ORCID"] = from_curie(element["contributor_id"])
        element["contributor_roles"] = [
            map_contributor_role(i)
            for i in wrap(element.get("contributor_roles", None))
        ]
        element = py_.omit(element, "contributor_id")
        return compact(element)

    return [format_element(i) for i in elements]


def from_csl(elements: list) -> list:
    """Convert from csl elements"""

    def format_element(element):
        """format element"""
        if element.get("literal", None) is not None:
            element["type"] = "Organization"
            element["name"] = element["literal"]
        elif element.get("name", None) is not None:
            element["type"] = "Organization"
            element["name"] = element.get("name")
        else:
            element["type"] = "Person"
            element["name"] = " ".join(
                [element.get("given", None), element.get("family", None)]
            )
        element["givenName"] = element.get("given", None)
        element["familyName"] = element.get("family", None)
        element["affiliation"] = element.get("affiliation", None)
        element = py_.omit(element, "given", "family", "literal", "sequence")
        return compact(element)

    return [format_element(i) for i in elements]


def to_csl(elements: list) -> list:
    """Convert elements to CSL-JSON"""

    def format_element(i):
        """format element"""
        element = {}
        element["family"] = i.get("familyName", None)
        element["given"] = i.get("givenName", None)
        element["literal"] = (
            i.get("name", None) if i.get("familyName", None) is None else None
        )
        return compact(element)

    return [format_element(i) for i in elements]


def to_ris(elements: list) -> list:
    """Convert element to RIS"""

    def format_element(i):
        """format element"""
        if i.get("familyName", None):
            element = ", ".join([i["familyName"], i.get("givenName", None)])
        else:
            element = i.get("name", None)
        return element

    return [format_element(i) for i in elements]


def to_schema_org(element: Optional[dict]) -> Optional[dict]:
    """Convert a metadata element to Schema.org"""
    if not isinstance(element, dict):
        return None
    mapping = {"type": "@type", "id": "@id", "title": "name"}
    for key, value in mapping.items():
        if element.get(key, None) is not None:
            element[value] = element.pop(key)
    return element


def to_schema_org_creators(elements: list) -> list():
    """Convert creators to Schema.org"""

    def format_element(element):
        """format element"""
        element["@type"] = element["type"][0:-2] if element.get("type", None) else None
        if element.get("familyName", None) and element.get("name", None) is None:
            element["name"] = " ".join(
                [element.get("givenName", None), element.get("familyName")]
            )
            element["@type"] = "Person"
        else:
            element["@type"] = "Organization"
        element = py_.omit(element, "type", "contributorRoles")
        return compact(element)

    return [format_element(i) for i in elements]


def to_schema_org_container(element: Optional[dict], **kwargs) -> Optional[dict]:
    """Convert CSL container to Schema.org container"""
    if element is None and kwargs.get("container_title", None) is None:
        return None
    if not isinstance(element, dict):
        return None

    return compact(
        {
            "@id": element.get("identifier", None),
            "@type": "DataCatalog"
            if kwargs.get("type", None) == "DataRepository"
            else "Periodical",
            "name": element.get("title", None) or kwargs.get("container_title", None),
        }
    )


def to_schema_org_identifiers(elements: list) -> list:
    """Convert identifiers to Schema.org"""

    def format_element(i):
        """format element"""
        element = {}
        element["@type"] = "PropertyValue"
        element["propertyID"] = i.get("identifierType", None)
        element["value"] = i.get("identifier", None)
        return compact(element)

    return [format_element(i) for i in elements]


def to_schema_org_relations(related_items: list, relation_type=None):
    """Convert relatedItems to Schema.org relations"""

    def format_element(i):
        """format element"""
        if i["relatedItemIdentifierType"] == "ISSN" and i["relationType"] == "IsPartOf":
            return compact({"@type": "Periodical", "issn": i["relatedItemIdentifier"]})
        return compact({"@id": normalize_id(i["relatedIdentifier"])})

    # consolidate different relation types
    if relation_type == "References":
        relation_type = ["References", "Cites"]
    else:
        relation_type = [relation_type]

    related_items = py_.filter(
        wrap(related_items), lambda ri: ri["relationType"] in relation_type
    )
    return [format_element(i) for i in related_items]


def find_from_format(pid=None, string=None, ext=None, filename=None):
    """Find reader from format"""
    if pid is not None:
        return find_from_format_by_id(pid)
    if string is not None and ext is not None:
        return find_from_format_by_ext(ext)
    if string is not None:
        return find_from_format_by_string(string)
    if filename is not None:
        return find_from_format_by_filename(filename)
    return "datacite"


def find_from_format_by_id(pid: str) -> Optional[str]:
    """Find reader from format by id"""
    doi = validate_doi(pid)
    if doi and (registration_agency := get_doi_ra(doi)) is not None:
        return registration_agency.lower()
    if (
        re.match(r"\A(http|https):/(/)?github\.com/(.+)/CITATION.cff\Z", pid)
        is not None
    ):
        return "cff"
    if (
        re.match(r"\A(http|https):/(/)?github\.com/(.+)/codemeta.json\Z", pid)
        is not None
    ):
        return "codemeta"
    if re.match(r"\A(http|https):/(/)?github\.com/(.+)\Z", pid) is not None:
        return "cff"
    if re.match(r"\Ahttps:/(/)?api\.rogue-scholar\.org/posts/(.+)\Z", pid) is not None:
        return "json_feed_item"
    if re.match(r"\Ahttps:/(/)?zenodo\.org/api/records/(.+)\Z", pid) is not None:
        return "inveniordm"
    return "schema_org"


def find_from_format_by_ext(ext: str) -> Optional[str]:
    """Find reader from format by ext"""
    if ext == ".bib":
        return "bibtex"
    if ext == ".ris":
        return "ris"
    return None


def find_from_format_by_string(string: str) -> Optional[str]:
    """Find reader from format by string"""
    if string is None:
        return None
    try:
        data = json.loads(string)
        if data.get("schema_version", "").startswith("https://commonmeta.org"):
            return "commonmeta"
        if data.get("@context", None) == "http://schema.org":
            return "schema_org"
        if data.get("@context", None) in [
            "https://raw.githubusercontent.com/codemeta/codemeta/master/codemeta.jsonld"
        ]:
            return "codemeta"
        if py_.get(data, "blog.version", None) == "https://jsonfeed.org/version/1.1":
            return "json_feed_item"
        if data.get("schemaVersion", "").startswith(
            "http://datacite.org/schema/kernel"
        ):
            return "datacite"
        if data.get("source", None) == "Crossref":
            return "crossref"
        if py_.get(data, "issued.date-parts") is not None:
            return "csl"
        if py_.get(data, "conceptdoi") is not None:
            return "inveniordm"
        if py_.get(data, "credit_metadata") is not None:
            return "kbase"
    except json.JSONDecodeError:
        pass
    try:
        data = BeautifulSoup(string, "xml")
        if data.find("doi_record"):
            return "crossref_xml"
        if data.find("resource"):
            return "datacite_xml"
    except ValueError:
        pass
    try:
        data = yaml.safe_load(string)
        if data.get("cff-version", None):
            return "cff"
    except (yaml.YAMLError, AttributeError):
        pass

    if string.startswith("TY  - "):
        return "ris"
    if any(string.startswith(f"@{t}") for t in bibtexparser.bibdatabase.STANDARD_TYPES):
        return "bibtex"

    # no format found
    return None

    # if Maremma.from_xml(string).to_h.dig('crossref_result', 'query_result', 'body', 'query',
    #                                        'doi_record', 'crossref').present?
    #     'crossref_xml'
    #   elsif Nokogiri::XML(string, None, 'UTF-8', &:noblanks).collect_namespaces.find do |_k, v|
    #           v.start_with?('http://datacite.org/schema/kernel')
    # #         end
    #     'datacite_xml'


def find_from_format_by_filename(filename):
    """Find reader from format by filename"""
    if filename == "CITATION.cff":
        return "cff"
    return None


def from_schema_org(element):
    """Convert schema.org to DataCite"""
    if element is None:
        return None
    element["type"] = element.get("@type", None)
    element["id"] = element.get("@id", None)
    return compact(py_.omit(element, ["@type", "@id"]))


def from_schema_org_creators(elements: list) -> list:
    """Convert schema.org creators to commonmeta"""

    def format_element(i):
        """format element"""
        element = {}
        if urlparse(i.get("@id", None)).hostname == "orcid.org":
            element["id"] = i.get("@id")
            element["type"] = "Person"
        elif isinstance(i.get("@type", None), str):
            element["type"] = i.get("@type")
        elif isinstance(i.get("@type", None), list):
            element["type"] = py_.find(
                i["@type"], lambda x: x in ["Person", "Organization"]
            )

        # strip text after comma if suffix is an academic title
        if str(i["name"]).split(", ", maxsplit=1)[-1] in [
            "MD",
            "PhD",
            "DVM",
            "DDS",
            "DMD",
            "JD",
            "MBA",
            "MPH",
            "MS",
            "MA",
            "MFA",
            "MSc",
            "MEd",
            "MEng",
            "MPhil",
            "MRes",
            "LLM",
            "LLB",
            "BSc",
            "BA",
            "BFA",
            "BEd",
            "BEng",
            "BPhil",
        ]:
            i["name"] = str(i["name"]).split(", ", maxsplit=1)[0]
        length = len(str(i["name"]).split(" "))
        if i.get("givenName", None):
            element["givenName"] = i.get("givenName", None)
        if i.get("familyName", None):
            element["familyName"] = i.get("familyName", None)
            element["type"] = "Person"
        # parentheses around the last word indicate an organization
        elif length > 1 and not str(i["name"]).rsplit(" ", maxsplit=1)[-1].startswith(
            "("
        ):
            element["givenName"] = " ".join(str(i["name"]).split(" ")[0 : length - 1])
            element["familyName"] = str(i["name"]).rsplit(" ", maxsplit=1)[1:]
        if not element.get("familyName", None):
            element["creatorName"] = compact(
                {
                    "type": i.get("@type", None),
                    "#text": i.get("name", None),
                }
            )

        if isinstance(i.get("affiliation", None), str):
            element["affiliation"] = {"type": "Organization", "name": i["affiliation"]}
        elif urlparse(py_.get(i, "affiliation.@id", "")).hostname in [
            "ror.org",
            "isni.org",
        ]:
            element["affiliation"] = {
                "id": i["affiliation"]["@id"],
                "type": "Organization",
                "name": i["affiliation"]["name"],
            }
        return compact(element)

    return [format_element(i) for i in wrap(elements)]


def github_from_url(url: str) -> dict:
    """Get github owner, repo, release and path from url"""

    match = re.match(
        r"\Ahttps://(github|raw\.githubusercontent)\.com/(.+)(?:/)?(.+)?(?:/tree/)?(.*)\Z",
        url,
    )
    if match is None:
        return {}
    words = urlparse(url).path.lstrip("/").split("/")
    owner = words[0] if len(words) > 0 else None
    repo = words[1] if len(words) > 1 else None
    release = words[3] if len(words) > 3 else None
    path = "/".join(words[4:]) if len(words) > 3 else ""
    if len(path) == 0:
        path = None

    return compact({"owner": owner, "repo": repo, "release": release, "path": path})


def github_repo_from_url(url: str) -> Optional[str]:
    """Get github repo from url"""
    return github_from_url(url).get("repo", None)


def github_release_from_url(url: str) -> Optional[str]:
    """Get github release from url"""
    return github_from_url(url).get("release", None)


def github_owner_from_url(url: str) -> Optional[str]:
    """Get github owner from url"""
    return github_from_url(url).get("owner", None)


def github_as_owner_url(url: str) -> Optional[str]:
    """Get github owner url from url"""
    github_dict = github_from_url(url)
    if github_dict.get("owner", None) is None:
        return None
    return f"https://github.com/{github_dict.get('owner')}"


def github_as_repo_url(url) -> Optional[str]:
    """Get github repo url from url"""
    github_dict = github_from_url(url)
    if github_dict.get("repo", None) is None:
        return None
    return f"https://github.com/{github_dict.get('owner')}/{github_dict.get('repo')}"


def github_as_release_url(url: str) -> Optional[str]:
    """Get github release url from url"""
    github_dict = github_from_url(url)
    if github_dict.get("release", None) is None:
        return None
    return f"https://github.com/{github_dict.get('owner')}/{github_dict.get('repo')}/tree/{github_dict.get('release')}"


def github_as_codemeta_url(url: str) -> Optional[str]:
    """Get github codemeta.json url from url"""
    github_dict = github_from_url(url)

    if github_dict.get("path", None) and github_dict.get("path").endswith(
        "codemeta.json"
    ):
        return f"https://raw.githubusercontent.com/{github_dict.get('owner')}/{github_dict.get('repo')}/{github_dict.get('release')}/{github_dict.get('path')}"
    elif github_dict.get("owner", None):
        return f"https://raw.githubusercontent.com/{github_dict.get('owner')}/{github_dict.get('repo')}/master/codemeta.json"
    else:
        return None


def github_as_cff_url(url: str) -> Optional[str]:
    """Get github CITATION.cff url from url"""
    github_dict = github_from_url(url)

    if github_dict.get("path", None) and github_dict.get("path").endswith(
        "CITATION.cff"
    ):
        return f"https://raw.githubusercontent.com/{github_dict.get('owner')}/{github_dict.get('repo')}/{github_dict.get('release')}/{github_dict.get('path')}"
    if github_dict.get("owner", None):
        return f"https://raw.githubusercontent.com/{github_dict.get('owner')}/{github_dict.get('repo')}/main/CITATION.cff"
    return None


def pages_as_string(
    container: Optional[dict], page_range_separator="-"
) -> Optional[str]:
    """Parse pages for BibTeX"""
    if container is None:
        return None
    if container.get("firstPage", None) is None:
        return None
    if container.get("lastPage", None) is None:
        return container.get("firstPage", None)

    return page_range_separator.join(
        [container.get("firstPage"), container.get("lastPage", None)]
    )


def subjects_as_string(subjects):
    """convert subject list to string, e.g. for bibtex"""
    if subjects is None:
        return None

    keywords = []
    for subject in wrap(subjects):
        keywords.append(subject.get("subject", None))
    return ", ".join(keywords)


# def reverse():
#       return { 'citation': wrap(related_identifiers).select do |ri|
#                         ri['relationType'] == 'IsReferencedBy'
#                       end.map do |r|
#                         { '@id': normalize_doi(r['relatedIdentifier']),
#                           '@type': r['resourceTypeGeneral'] validate_orcid 'ScholarlyArticle',
#                           'identifier': r['relatedIdentifierType'] == 'DOI' ? nil : to_identifier(r) }.compact
#                       end.unwrap,
#         'isBasedOn': wrap(related_identifiers).select do |ri|
#                          ri['relationType'] == 'IsSupplementTo'
#                        end.map do |r|
#                          { '@id': normalize_doi(r['relatedIdentifier']),
#                            '@type': r['resourceTypeGeneral'] or 'ScholarlyArticle',
#                            'identifier': r['relatedIdentifierType'] == 'DOI' ? nil : to_identifier(r) }.compact
#                        end.unwrap }.compact


def name_to_fos(name: str) -> Optional[dict]:
    """Convert name to Fields of Science (OECD) subject"""
    #   # first find subject in Fields of Science (OECD)
    #   fos = JSON.load(File.read(File.expand_path('../../resources/oecd/fos-mappings.json',
    #                                              __dir__))).fetch('fosFields')

    #   subject = fos.find { |l| l['fosLabel'] == name || 'FOS: ' + l['fosLabel'] == name }

    #   if subject
    #     return [{
    #       'subject': sanitize(name).downcase
    #     },
    #             {
    #               'subject': 'FOS: ' + subject['fosLabel'],
    #               'subjectScheme': 'Fields of Science and Technology (FOS)',
    #               'schemeUri': 'http://www.oecd.org/science/inno/38235147.pdf'
    #             }]
    #   end

    #   # if not found, look in Fields of Research (Australian and New Zealand Standard Research Classification)
    #   # and map to Fields of Science. Add an extra entry for the latter
    #   fores = JSON.load(File.read(File.expand_path('../../resources/oecd/for-mappings.json',
    #                                                __dir__)))
    #   for_fields = fores.fetch('forFields')
    #   for_disciplines = fores.fetch('forDisciplines')

    #   subject = for_fields.find { |l| l['forLabel'] == name } ||
    #             for_disciplines.find { |l| l['forLabel'] == name }

    #   if subject
    #     [{
    #       'subject': sanitize(name).downcase
    #     },
    #      {
    #        'subject': 'FOS: ' + subject['fosLabel'],
    #        'subjectScheme': 'Fields of Science and Technology (FOS)',
    #        'schemeUri': 'http://www.oecd.org/science/inno/38235147.pdf'
    #      }]
    #   else

    return {"subject": name.strip()}


def encode_doi(prefix):
    """Generate a DOI using the DOI prefix and a random base32 suffix"""
    suffix = base32.generate(length=10, split_every=5, checksum=True)
    return f"https://doi.org/{prefix}/{suffix}"


def decode_doi(doi: str) -> int:
    """Decode a DOI to a number"""
    suffix = doi.split("/", maxsplit=5)[-1]
    return base32.decode(suffix)


def from_curie(id: Optional[str]) -> Optional[str]:
    """from CURIE"""
    if id is None:
        return None
    type_ = id.split(":")[0]
    if type_ == "DOI":
        return doi_as_url(id.split(":")[1])
    elif type_ == "ROR":
        return "https://ror.org/" + id.split(":")[1]
    elif type_ == "ISNI":
        return "https://isni.org/isni/" + id.split(":")[1]
    elif type_ == "ORCID":
        return normalize_orcid(id.split(":")[1])
    elif type_ == "URL":
        return normalize_url(id.split(":")[1])
    # TODO: resolvable url for other identifier types
    # elif identifier_type == "JDP":
    return None


def get_language(lang: str) -> Optional[dict]:
    """Provide a language object based on ISO 639, with either a name in English,
    ISO 639-1, or ISO 639-3 code as input.
    """
    if not lang:
        return None
    if len(lang) == 2:
        language = pycountry.languages.get(alpha_2=lang)
    elif len(lang) == 3:
        language = pycountry.languages.get(alpha_3=lang)
    else:
        language = pycountry.languages.get(name=lang)
    return language


def start_case(content: str) -> str:
    """Capitalize first letter of each word without lowercasing the rest"""
    words = content.split(" ")
    content = " ".join([word[0].upper() + word[1:] for word in words])
    return content
