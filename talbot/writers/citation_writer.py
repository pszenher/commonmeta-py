import json
import re
from citeproc import CitationStylesStyle, CitationStylesBibliography
from citeproc import Citation, CitationItem
from citeproc import formatter
from citeproc.source.json import CiteProcJSON
from citeproc_styles import get_style_filepath


def write_citation(metadata):
    """Write citation"""

    def _clean_result(text):
        """Remove double spaces, punctuation."""
        text = re.sub(r"\s\s+", " ", text)
        text = re.sub(r"\.\.+", ".", text)
        return text

    citeproc_json = json.loads(metadata.citeproc())

    # Remove keys that are not supported by citeproc-py.
    for key in ['copyright', 'categories']:
        del citeproc_json[key]

    # Process the JSON data to generate a citeproc-py BibliographySource.
    source = CiteProcJSON([citeproc_json])
    style_path = get_style_filepath(metadata.style)
    style = CitationStylesStyle(style_path, locale=metadata.locale)
    bib = CitationStylesBibliography(style, source, formatter.html)
    citation = Citation([CitationItem(metadata.id)])
    bib.register(citation)
    return _clean_result(str(bib.bibliography()[0]))