import pytest
from talbot import Metadata


@pytest.mark.vcr
def test_doi_with_data_citation():
    "DOi with data citation"
    subject = Metadata("10.7554/elife.01567")
    assert subject.id == "https://doi.org/10.7554/elife.01567"
    assert subject.types.get('bibtex') == 'article'

    bibtex = subject.bibtex()
    print(bibtex)
    assert bibtex == \
"""@article{https://doi.org/10.7554/elife.01567,
    abstract = {Among various advantages, their small size makes model organisms preferred subjects of investigation. Yet, even in model systems detailed analysis of numerous developmental processes at cellular level is severely hampered by their scale. For instance, secondary growth of Arabidopsis hypocotyls creates a radial pattern of highly specialized tissues that comprises several thousand cells starting from a few dozen. This dynamic process is difficult to follow because of its scale and because it can only be investigated invasively, precluding comprehensive understanding of the cell proliferation, differentiation, and patterning events involved. To overcome such limitation, we established an automated quantitative histology approach. We acquired hypocotyl cross-sections from tiled high-resolution images and extracted their information content using custom high-throughput image processing and segmentation. Coupled with automated cell type recognition through machine learning, we could establish a cellular resolution atlas that reveals vascular morphodynamics during secondary growth, for example equidistant phloem pole formation.},
    author = {Sankar, Martial and Nieminen, Kaisa and Ragni, Laura and Xenarios, Ioannis and Hardtke, Christian S},
    copyright = {https://creativecommons.org/licenses/by/3.0/legalcode},
    doi = {10.7554/elife.01567},
    issn = {2050-084X},
    journal = {eLife},
    language = {en},
    month = {feb},
    title = {Automated quantitative histology reveals vascular morphodynamics during Arabidopsis hypocotyl secondary growth},
    url = {https://elifesciences.org/articles/01567},
    urldate = {2014-02-11},
    year = {2014}
}
"""


def test_doi_for_blog_post():
    "DOi for blog post"
    subject = Metadata("10.53731/avg2ykg-gdxppcd")
    assert subject.id == "https://doi.org/10.53731/avg2ykg-gdxppcd"
    assert subject.types.get('bibtex') == 'article'

    bibtex = subject.bibtex()
    print(bibtex)
    assert bibtex == \
"""@article{https://doi.org/10.53731/avg2ykg-gdxppcd,
    abstract = {Science blogs have been around for at least 20 years and have become an important part of science communication. So are there any fundamental issues that need fixing? Barriers to Entry Blogging platforms are mature at this point, and the technology is not imposing barriers to entry for most people. The user experience has greatly improved over the last few years and there are a number of affordable ways for hosting a blog that also work for science blogs, including free options such as GitHub},
    author = {Fenner, Martin},
    copyright = {https://creativecommons.org/licenses/by/4.0/legalcode},
    doi = {10.53731/avg2ykg-gdxppcd},
    month = {jan},
    title = {Do we need to fix science blogs?},
    url = {https://blog.front-matter.io/posts/need-to-fix-science-blogs},
    urldate = {2023-01-25},
    year = {2023}
}
"""

def test_blog_post():
    "blog post"
    input = "https://upstream.force11.org/welcome-to-upstream/"
    subject = Metadata(input, via='schema_org')
    assert subject.id == "https://doi.org/10.54900/rckn8ey-1fm76va-qsrnf"
    assert subject.types.get('bibtex') == 'article'
    bibtex = subject.bibtex()
    print(bibtex)
    assert bibtex == \
"""@article{https://doi.org/10.54900/rckn8ey-1fm76va-qsrnf,
    abstract = {Today we are announcing Upstream. And if you’re reading this, you’re already a part of it! Upstream is a community blogging platform designed for Open enthusiasts to discuss… you guessed it: all things Open. It’s a space for the whole community to voice opinions, discuss open approaches to scholarly communication, and showcase research. A central place to exchange in writing ideas about open research and all that it encompasses Supported by FORCE11, this is a global and inclusive blog, bringi},
    author = {Chodacki, John and Hendricks, Ginny and Ferguson, Christine and Fenner, Martin},
    copyright = {https://creativecommons.org/licenses/by/4.0/legalcode},
    doi = {10.54900/rckn8ey-1fm76va-qsrnf},
    journal = {Upstream},
    language = {en},
    month = {nov},
    title = {Welcome to Upstream: the new space for scholarly community discussion on all things open},
    url = {https://upstream.force11.org/welcome-to-upstream},
    urldate = {2021-11-22},
    year = {2021}
}
"""

def test_article_with_pages():
    "article with pages"
    input = "https://doi.org/10.1371/journal.ppat.1008184"
    subject = Metadata(input)
    assert subject.id == "https://doi.org/10.1371/journal.ppat.1008184"
    assert subject.types.get('bibtex') == 'article'

    bibtex = subject.bibtex()
    print(bibtex)
    assert bibtex == \
"""@article{https://doi.org/10.1371/journal.ppat.1008184,
    author = {Twittenhoff, Christian and Heroven, Ann Kathrin and Mühlen, Sabrina and Dersch, Petra and Narberhaus, Franz},
    copyright = {https://creativecommons.org/licenses/by/4.0/legalcode},
    doi = {10.1371/journal.ppat.1008184},
    issn = {1553-7374},
    issue = {1},
    journal = {PLOS Pathogens},
    language = {en},
    month = {jan},
    pages = {e1008184},
    title = {An RNA thermometer dictates production of a secreted bacterial toxin},
    url = {https://dx.plos.org/10.1371/journal.ppat.1008184},
    urldate = {2020-01-17},
    year = {2020}
}
"""

def test_article_dlib_magazine():
    "article dlib magazine"
    input = "https://doi.org/10.1045/january2017-burton"
    subject = Metadata(input)
    assert subject.id == "https://doi.org/10.1045/january2017-burton"
    assert subject.types.get('bibtex') == 'article'

    bibtex = subject.bibtex()
    print(bibtex)
    assert bibtex == \
"""@article{https://doi.org/10.1045/january2017-burton,
    author = {Burton, Adrian and Aryani, Amir and Koers, Hylke and Manghi, Paolo and La Bruzzo, Sandro and Stocker, Markus and Diepenbroek, Michael and Schindler, Uwe and Fenner, Martin},
    doi = {10.1045/january2017-burton},
    issn = {1082-9873},
    issue = {1/2},
    journal = {D-Lib Magazine},
    language = {en},
    month = {jan},
    title = {The Scholix Framework for Interoperability in Data-Literature Information Exchange},
    url = {http://www.dlib.org/dlib/january17/burton/01burton.html},
    urldate = {2017-01},
    year = {2017}
}
"""