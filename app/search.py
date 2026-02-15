from __future__ import annotations

from typing import List
from urllib.parse import quote

from app.models import EvidenceLink


class SearchClient:
    """Simple search abstraction.

    In production this should call Tavily, SerpAPI, or official regulatory APIs.
    """

    BASE_PORTALS = {
        "CDSCO": "https://cdsco.gov.in",
        "FDA": "https://www.fda.gov",
        "Health Canada": "https://recalls-rappels.canada.ca",
    }

    def waterfall_search(self, product_name: str, batch_number: str, manufacturer: str) -> List[EvidenceLink]:
        query = f"{product_name} {batch_number} {manufacturer} recall NSQ"
        links: List[EvidenceLink] = []
        for source, base_url in self.BASE_PORTALS.items():
            fragment = quote(batch_number)
            deep_link = f"{base_url}/search?q={quote(query)}#:~:text={fragment}"
            links.append(
                EvidenceLink(
                    source=source,
                    title=f"{source} recall lookup for {product_name}",
                    url=deep_link,
                    highlighted_fragment=batch_number,
                )
            )
        return links
