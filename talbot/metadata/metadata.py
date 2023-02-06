
from ..readers.crossref_json_reader import get_crossref_json, read_crossref_json
from ..readers.schema_org_reader import get_schema_org, read_schema_org
from ..writers.bibtex_writer import write_bibtex
from ..writers.citeproc_writer import write_citeproc
from ..utils import normalize_id, find_from_format

class Metadata:
    """Metadata"""
    def __init__(self, input, **kwargs):
        id = normalize_id(input)

        if id is None:
            raise ValueError("No ID found")
        else:
            via = kwargs.get('via', None) # or find_from_format(id=id)
            if via == 'schema_org':
                string = get_schema_org(id=input)
                meta = read_schema_org(string=string)
            else:
                string = get_crossref_json(id=input)
                meta = read_crossref_json(string=string)
        self.id = meta.get('id')
        self.url = meta.get('url')
        self.types = meta.get('types')
        self.creators = meta.get('creators')
        self.contributors = meta.get('contributors')
        self.titles = meta.get('titles')
        self.dates = meta.get('dates')
        self.publication_year = meta.get('publication_year')
        self.date_registered = meta.get('date_registered')
        self.publisher = meta.get('publisher')
        self.rights_list = meta.get('rights_list')
        self.issn = meta.get('issn')
        self.container = meta.get('container')
        self.related_identifiers = meta.get('related_identifiers')
        self.funding_references = meta.get('funding_references')
        self.descriptions = meta.get('descriptions')
        self.subjects = meta.get('subjects')
        self.language = meta.get('language')
        self.version_info = meta.get('version_info')
        self.geo_locations = meta.get('geo_locations')
        self.agency = meta.get('agency')

    def bibtex(self):
        """Bibtex"""
        return write_bibtex(self)

    def citeproc(self):
        """Citeproc"""
        return write_citeproc(self)
