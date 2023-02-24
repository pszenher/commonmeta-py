"""Utils module for commonmeta-py"""
import os
import json
import yaml
import re
import bibtexparser
from bs4 import BeautifulSoup
from typing import Optional, Union
from urllib.parse import urlparse
from pydash import py_

# from .author_utils import get_personal_name
from .base_utils import wrap, unwrap, compact
from .doi_utils import normalize_doi, doi_from_url, get_doi_ra, validate_doi, crossref_api_url, datacite_api_url
from .constants import DC_TO_SO_TRANSLATIONS, SO_TO_DC_TRANSLATIONS

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
        if i.get("@id", None):
            idn = normalize_id(i["@id"])
            doi = doi_from_url(idn)
            related_identifier_type = "DOI" if doi is not None else "URL"
            idn = doi or idn
            type_ = (
                i.get("@type")
                if isinstance(i.get("@type", None), str)
                else wrap(i.get("@type", None))[0]
            )
            return compact(
                {
                    "relatedIdentifier": idn,
                    "relationType": relation_type,
                    "relatedIdentifierType": related_identifier_type,
                    "resourceTypeGeneral": SO_TO_DC_TRANSLATIONS.get(type_, None),
                })
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


def normalize_issn(string, **kwargs):
    """Normalize ISSN
       Pick electronic issn if there are multiple
       Format issn as xxxx-xxxx"""
    content = kwargs.get('content', '#text')
    if string is None:
        return None
    if isinstance(string, str):
        issn = string
    elif isinstance(string, dict):
        issn = string.get(content, None)
    elif isinstance(string, list):
        issn = next((i for i in string if i.get('media_type', None)
                    == 'electronic'), {}).get(content, None)
    if issn is None:
        return None
    if len(issn) == 9:
        return issn
    if len(issn) == 8:
        return issn[0:4] + '-' + issn[4:8]
    return None


def dict_to_spdx(dct: dict) -> dict:
    """Convert a dict to SPDX"""
    dct.update({"rightsUri": normalize_cc_url(dct.get("rightsUri", None))})
    file_path = os.path.join(os.path.dirname(
        __file__), "resources/spdx/licenses.json")
    with open(file_path, encoding="utf-8") as json_file:
        spdx = json.load(json_file).get("licenses")
    license_ = next(
        (
            l
            for l in spdx
            if l["licenseId"].casefold() == dct.get("rightsIdentifier", '').casefold()
            or l["seeAlso"][0] == dct.get("rightsUri", None)
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
            "rights": license_["name"],
            "rightsUri": license_["seeAlso"][0],
            "rightsIdentifier": license_["licenseId"].lower(),
            "rightsIdentifierScheme": "SPDX",
            "schemeUri": "https://spdx.org/licenses/",
            "lang": dct.get("lang", None),
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


def from_citeproc(elements: list) -> list:
    """Convert from citeproc elements"""
    def format_element(element):
        """format element"""
        if element.get("literal", None) is not None:
            element["@type"] = "Organization"
            element["name"] = element["literal"]
        elif element.get("name", None) is not None:
            element["@type"] = "Organization"
            element["name"] = element.get("name")
        else:
            element["@type"] = "Person"
            element["name"] = " ".join(
                [element.get("given", None), element.get("family", None)]
            )
        element["givenName"] = element.get("given", None)
        element["familyName"] = element.get("family", None)
        element["affiliation"] = element.get("affiliation", None)
        element = py_.omit(element, "given", "family", "literal", "sequence")
        return compact(element)
    return [format_element(i) for i in elements]


def to_citeproc(elements: list) -> list:
    """Convert elements to citeproc"""
    def format_element(i):
        """format element"""
        element = {}
        element["family"] = i.get("familyName", None)
        element["given"] = i.get("givenName", None)
        element["literal"] = (
            i.get("name", None) if i.get(
                "familyName", None) is None else None
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
            element = i.get('name', None)
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
        element["@type"] = element["nameType"][0:-
                                               2] if element.get("nameType", None) else None
        if element.get("familyName", None) and element.get("name", None) is None:
            element["name"] = " ".join(
                [element.get("givenName", None), element.get("familyName")])
            element["@type"] = "Person"
        else:
            element["@type"] = "Organization"
        element = py_.omit(element, "nameType")
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
            return compact({"@type": "Periodical",
                            "issn": i["relatedItemIdentifier"]})
        return compact(
            {
                "@id": normalize_id(i["relatedIdentifier"]),
                "@type": DC_TO_SO_TRANSLATIONS.get(
                    i.get("resourceTypeGeneral", "CreativeWork")
                ),
            }
        )

    # consolidate different relation types
    if relation_type == "References":
        relation_type = ["References", "Cites"]
    else:
        relation_type = [relation_type]

    related_items = py_.filter(
        wrap(
            related_items), lambda ri: ri["relationType"] in relation_type
    )
    return [format_element(i) for i in related_items]


def find_from_format(pid=None, string=None, ext=None, filename=None):
    """Find reader from format"""
    if pid is not None:
        return find_from_format_by_id(pid)
    if string is not None and ext is not None:
        return find_from_format_by_ext(string, ext=ext)
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
    if re.match(r"\A(http|https):/(/)?github\.com/(.+)/CITATION.cff\Z", pid) is not None:
        return "cff"
    if (
        re.match(r"\A(http|https):/(/)?github\.com/(.+)/codemeta.json\Z", pid)
        is not None
    ):
        return "codemeta"
    if re.match(r"\A(http|https):/(/)?github\.com/(.+)\Z", pid) is not None:
        return "cff"
    return "schema_org"


def find_from_format_by_ext(string, ext=None):
    """Find reader from format by ext"""


def find_from_format_by_string(string: str) -> Optional[str]:
    """Find reader from format by string"""
    if string is None:
        return None
    try:
        data = json.loads(string)
        if data.get("@context", None) == "http://schema.org":
            return "schema_org"
        if data.get("@context", None) in ['https://raw.githubusercontent.com/codemeta/codemeta/master/codemeta.jsonld']:
            return "codemeta"
        if data.get("schemaVersion", '').startswith("http://datacite.org/schema/kernel"):
            return "datacite"
        if data.get("source", None) == "Crossref":
            return "crossref"
        if py_.get(data, "issued.date-parts") is not None:
            return "citeproc"
    except json.JSONDecodeError:
        pass
    try:
        data = BeautifulSoup(string, "xml")
        if data.find("doi_record"):
            return 'crossref_xml'
        if data.find("resource"):
            return 'datacite_xml'
    except ValueError:
        pass
    try:
        data = yaml.safe_load(string)
        if data.get("cff-version", None):
            return "cff"
    except (yaml.YAMLError, AttributeError):
        pass

    if string.startswith('TY  - '):
        return 'ris'
    if any(string.startswith(f"@{t}") for t in bibtexparser.bibdatabase.STANDARD_TYPES):
        return 'bibtex'

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
    """Convert schema.org creators to DataCite"""
    def format_element(i):
        """format element"""
        element = {}
        if isinstance(i.get("affiliation", None), str):
            i["affiliation"] = {"name": i["affiliation"]}
            affiliation_identifier_scheme = None
            scheme_uri = None
        elif py_.get(i, "affiliation.@id", "").startswith("https://ror.org"):
            affiliation_identifier_scheme = "ROR"
            scheme_uri = "https://ror.org/"
        elif i.get("affiliation.@id", "").startswith("https://isni.org"):
            affiliation_identifier_scheme = "ISNI"
            scheme_uri = "https://isni.org/isni/"
        else:
            affiliation_identifier_scheme = None
            scheme_uri = None
        element["nameIdentifier"] = [
            {
                "#text": i.get("@id", None),
                "nameIdentifierScheme": "ORCID",
                "schemeUri": "https://orcid.org",
            }
        ]

        if isinstance(i.get("@type", None), list):
            element["@type"] = py_.find(
                i["@type"], lambda x: x in ["Person", "Organization"]
            )
        element["creatorName"] = compact(
            {
                "nameType": i["@type"].title() + "al"
                if i.get("@type", None)
                else None,
                "#text": i.get("name", None)
            }
        )
        length = len(str(i["name"]).split(" "))
        if i.get("givenName", None):
            element["givenName"] = i.get("givenName", None)
        else:
            element["givenName"] = " ".join(
                str(i["name"]).split(" ")[0: length - 1])
        if i.get("familyName", None):
            element["familyName"] = i.get("familyName", None)
        else:
            element["familyName"] = str(i["name"]).rsplit(" ", maxsplit=1)[1:]

        element["affiliation"] = compact(
            {
                "#text": py_.get(i, "affiliation.name"),
                "affiliationIdentifier": py_.get(i, "affiliation.@id"),
                "affiliationIdentifierScheme": affiliation_identifier_scheme,
                "schemeUri": scheme_uri,
            }
        ) if i.get("affiliation", None) is not None else None
        return compact(element)
    return [format_element(i) for i in wrap(elements)]


def github_from_url(url: str) -> dict:
    """Get github owner, repo, release and path from url"""

    match = re.match(
        r"\Ahttps://(github|raw\.githubusercontent)\.com/(.+)(?:/)?(.+)?(?:/tree/)?(.*)\Z", url)
    if match is None:
        return {}
    words = urlparse(url).path.lstrip('/').split('/')
    owner = words[0] if len(words) > 0 else None
    repo = words[1] if len(words) > 1 else None
    release = words[3] if len(words) > 3 else None
    path = '/'.join(words[4:]) if len(words) > 3 else None

    return compact({'owner': owner, 'repo': repo, 'release': release, 'path': path})


def github_repo_from_url(url: str) -> Optional[str]:
    """Get github repo from url"""
    return github_from_url(url).get('repo', None)


def github_release_from_url(url: str) -> Optional[str]:
    """Get github release from url"""
    return github_from_url(url).get('release', None)


def github_owner_from_url(url: str) -> Optional[str]:
    """Get github owner from url"""
    return github_from_url(url).get('owner', None)


def github_as_owner_url(url: str) -> Optional[str]:
    """Get github owner url from url"""
    github_dict = github_from_url(url)
    if github_dict.get('owner', None) is None:
        return None
    return f"https://github.com/{github_dict.get('owner')}"


def github_as_repo_url(url) -> Optional[str]:
    """Get github repo url from url"""
    github_dict = github_from_url(url)
    if github_dict.get('repo', None) is None:
        return None
    return f"https://github.com/{github_dict.get('owner')}/{github_dict.get('repo')}"


def github_as_release_url(url: str) -> Optional[str]:
    """Get github release url from url"""
    github_dict = github_from_url(url)
    if github_dict.get('release', None) is None:
        return None
    return f"https://github.com/{github_dict.get('owner')}/{github_dict.get('repo')}/tree/{github_dict.get('release')}"


def github_as_codemeta_url(url: str) -> Optional[str]:
    """Get github codemeta.json url from url"""
    github_dict = github_from_url(url)

    if github_dict.get('path', None) and github_dict.get('path').endswith('codemeta.json'):
        return f"https://raw.githubusercontent.com/{github_dict.get('owner')}/{github_dict.get('repo')}/{github_dict.get('release')}/{github_dict.get('path')}"
    elif github_dict.get('owner', None):
        return f"https://raw.githubusercontent.com/{github_dict.get('owner')}/{github_dict.get('repo')}/master/codemeta.json"
    else:
        return None


def github_as_cff_url(url: str) -> Optional[str]:
    """Get github CITATION.cff url from url"""
    github_dict = github_from_url(url)

    if github_dict.get('path', None) and github_dict.get('path').endswith('CITATION.cff'):
        return f"https://raw.githubusercontent.com/{github_dict.get('owner')}/{github_dict.get('repo')}/{github_dict.get('release')}/{github_dict.get('path')}"
    if github_dict.get('owner', None):
        return f"https://raw.githubusercontent.com/{github_dict.get('owner')}/{github_dict.get('repo')}/main/CITATION.cff"
    return None


def pages_as_string(container: Optional[dict], page_range_separator="-") -> Optional[str]:
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

    return {"subject": name.lower()}