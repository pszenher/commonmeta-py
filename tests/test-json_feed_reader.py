# pylint: disable=invalid-name,too-many-lines
"""JSON Feed reader tests"""
from os import path
import pytest

from commonmeta import Metadata
from commonmeta.readers.json_feed_reader import (
    get_json_feed_item,
    read_json_feed_item,
)


@pytest.mark.vcr
def test_wordpress_with_references():
    "Wordpress with references"
    string = "https://rogue-scholar.org/api/posts/4e4bf150-751f-4245-b4ca-fe69e3c3bb24"
    subject = Metadata(string)
    assert subject.is_valid
    assert subject.id == "https://doi.org/10.59350/hke8v-d1e66"
    assert subject.type == "Article"
    assert (
        subject.url
        == "https://svpow.com/2023/06/09/new-paper-curtice-et-al-2023-on-the-first-haplocanthosaurus-from-dry-mesa"
    )
    assert subject.titles[0] == {
        "title": "New paper: Curtice et al. (2023) on the first Haplocanthosaurus from Dry Mesa"
    }
    assert len(subject.contributors) == 1
    assert subject.contributors[0] == {
        "contributorRoles": ["Author"],
        "type": "Person",
        "familyName": "Wedel",
        "givenName": "Matt",
    }
    assert subject.license == {
        "id": "CC-BY-4.0",
        "url": "https://creativecommons.org/licenses/by/4.0/legalcode",
    }

    assert subject.date == {
        "published": "2023-06-09T21:54:23",
        "updated": "2023-06-09T21:54:23",
    }
    assert subject.publisher == {
        "name": "Sauropod Vertebra Picture of the Week",
    }
    assert len(subject.references) == 3
    assert subject.references[0] == {
        "key": "ref1",
        "url": "https://sauroposeidon.files.wordpress.com/2010/04/foster-and-wedel-2014-haplocanthosaurus-from-snowmass-colorado.pdf",
    }

    # assert subject.funding_references == [
    #     {"funderName": "SystemsX"},
    #     {"funderName": "EMBO longterm post-doctoral fellowships"},
    #     {"funderName": "Marie Heim-Voegtlin"},
    #     {
    #         "funderName": "University of Lausanne",
    #         "funderIdentifier": "https://doi.org/10.13039/501100006390",
    #         "funderIdentifierType": "Crossref Funder ID",
    #     },
    #     {"funderName": "SystemsX"},
    #     {
    #         "funderIdentifier": "https://doi.org/10.13039/501100003043",
    #         "funderIdentifierType": "Crossref Funder ID",
    #         "funderName": "EMBO",
    #     },
    #     {
    #         "funderIdentifier": "https://doi.org/10.13039/501100001711",
    #         "funderIdentifierType": "Crossref Funder ID",
    #         "funderName": "Swiss National Science Foundation",
    #     },
    #     {
    #         "funderIdentifier": "https://doi.org/10.13039/501100006390",
    #         "funderIdentifierType": "Crossref Funder ID",
    #         "funderName": "University of Lausanne",
    #     },
    # ]
    assert subject.container == {
        "title": "Sauropod Vertebra Picture of the Week",
        "type": "Periodical",
    }
    assert (
        subject.descriptions[0]
        .get("description")
        .startswith("<em>Haplocanthosaurus</em> tibiae and dorsal vertebrae.")
    )
    # assert subject.subjects == [
    #     {"subject": "General Immunology and Microbiology"},
    #     {"subject": "General Biochemistry, Genetics and Molecular Biology"},
    #     {"subject": "General Medicine"},
    #     {"subject": "General Neuroscience"},
    # ]
    assert subject.language == "en"
    assert subject.version is None


@pytest.mark.vcr
def test_ghost_with_institutional_author():
    "ghost with institutional author"
    string = "https://rogue-scholar.org/api/posts/2b3cdd27-5123-4167-9482-3c074392e2d2"
    subject = Metadata(string)
    assert subject.is_valid
    assert subject.id == "https://doi.org/10.59350/tfahc-rp566"
    assert subject.type == "Article"
    assert (
        subject.url
        == "https://blog.oa.works/nature-features-oa-reports-work-putting-oa-policy-into-practice"
    )
    assert subject.titles[0] == {
        "title": "Nature features OA.Report's work putting OA policy into practice!"
    }
    assert len(subject.contributors) == 1
    assert subject.contributors[0] == {
        "contributorRoles": ["Author"],
        "type": "Organization",
        "name": "OA.Works",
    }
    assert subject.license == {
        "id": "CC-BY-4.0",
        "url": "https://creativecommons.org/licenses/by/4.0/legalcode",
    }

    assert subject.date == {
        "published": "2023-01-24T12:11:47",
        "updated": "2023-01-24T12:11:47",
    }
    assert subject.publisher == {
        "name": "OA.Works Blog",
    }
    assert len(subject.references) == 0

    # assert subject.funding_references == [
    #     {"funderName": "SystemsX"},
    #     {"funderName": "EMBO longterm post-doctoral fellowships"},
    #     {"funderName": "Marie Heim-Voegtlin"},
    #     {
    #         "funderName": "University of Lausanne",
    #         "funderIdentifier": "https://doi.org/10.13039/501100006390",
    #         "funderIdentifierType": "Crossref Funder ID",
    #     },
    #     {"funderName": "SystemsX"},
    #     {
    #         "funderIdentifier": "https://doi.org/10.13039/501100003043",
    #         "funderIdentifierType": "Crossref Funder ID",
    #         "funderName": "EMBO",
    #     },
    #     {
    #         "funderIdentifier": "https://doi.org/10.13039/501100001711",
    #         "funderIdentifierType": "Crossref Funder ID",
    #         "funderName": "Swiss National Science Foundation",
    #     },
    #     {
    #         "funderIdentifier": "https://doi.org/10.13039/501100006390",
    #         "funderIdentifierType": "Crossref Funder ID",
    #         "funderName": "University of Lausanne",
    #     },
    # ]
    assert subject.container == {
        "title": "OA.Works Blog",
        "type": "Periodical",
    }
    assert (
        subject.descriptions[0]
        .get("description")
        .startswith(
            "After a couple of years of working to support institutions implementing their OA policies"
        )
    )
    # assert subject.subjects == [
    #     {"subject": "General Immunology and Microbiology"},
    #     {"subject": "General Biochemistry, Genetics and Molecular Biology"},
    #     {"subject": "General Medicine"},
    #     {"subject": "General Neuroscience"},
    # ]
    assert subject.language == "en"
    assert subject.version is None

@pytest.mark.vcr
def test_ghost_with_personal_name_parsing():
    "ghost with with personal name parsing"
    string = "https://rogue-scholar.org/api/posts/c3095752-2af0-40a4-a229-3ceb7424bce2"
    subject = Metadata(string)
    assert subject.is_valid
    assert subject.id == "https://doi.org/10.59350/kj95y-gp867"
    assert subject.type == "Article"
    assert (
        subject.url
        == "https://www.ideasurg.pub/residency-visual-abstract"
    )
    assert subject.titles[0] == {
        "title": "The Residency Visual Abstract"
    }
    assert len(subject.contributors) == 1
    assert subject.contributors[0] == {
        'id': 'https://orcid.org/0000-0003-0449-4469',
        "contributorRoles": ["Author"],
        "type": "Person",
        'familyName': 'Sathe',
        'givenName': 'Tejas S.',
    }
    assert subject.license == {
        "id": "CC-BY-4.0",
        "url": "https://creativecommons.org/licenses/by/4.0/legalcode",
    }

    assert subject.date == {
        "published": "2023-04-08T21:32:34",
        "updated": "2023-04-08T21:32:34",
    }
    assert subject.publisher == {
        "name": "I.D.E.A.S.",
    }
    assert len(subject.references) == 0

    # assert subject.funding_references == [
    #     {"funderName": "SystemsX"},
    #     {"funderName": "EMBO longterm post-doctoral fellowships"},
    #     {"funderName": "Marie Heim-Voegtlin"},
    #     {
    #         "funderName": "University of Lausanne",
    #         "funderIdentifier": "https://doi.org/10.13039/501100006390",
    #         "funderIdentifierType": "Crossref Funder ID",
    #     },
    #     {"funderName": "SystemsX"},
    #     {
    #         "funderIdentifier": "https://doi.org/10.13039/501100003043",
    #         "funderIdentifierType": "Crossref Funder ID",
    #         "funderName": "EMBO",
    #     },
    #     {
    #         "funderIdentifier": "https://doi.org/10.13039/501100001711",
    #         "funderIdentifierType": "Crossref Funder ID",
    #         "funderName": "Swiss National Science Foundation",
    #     },
    #     {
    #         "funderIdentifier": "https://doi.org/10.13039/501100006390",
    #         "funderIdentifierType": "Crossref Funder ID",
    #         "funderName": "University of Lausanne",
    #     },
    # ]
    assert subject.container == {
        'identifier': '2993-1150',
        'identifierType': 'ISSN',
        'title': 'I.D.E.A.S.',
        "type": "Periodical",
    }
    assert (
        subject.descriptions[0]
        .get("description")
        .startswith(
            "My prototype for a Residency Visual Abstract"
        )
    )
    # assert subject.subjects == [
    #     {"subject": "General Immunology and Microbiology"},
    #     {"subject": "General Biochemistry, Genetics and Molecular Biology"},
    #     {"subject": "General Medicine"},
    #     {"subject": "General Neuroscience"},
    # ]
    assert subject.language == "en"
    assert subject.version is None