from dataclasses import dataclass, field
from typing import Any


@dataclass
class Evidence:
    """
    Standard evidence object produced by every model
    in the GeoSentinel intelligence pipeline.
    """

    source: str
    category: str

    confidence: float
    importance: float = 1.0

    description: str = ""

    geometry: dict | None = None

    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceCollection:
    """
    Container for evidence from all models.
    """

    evidence: list[Evidence] = field(default_factory=list)

    # ---------------------------------------------------------
    # Add Evidence
    # ---------------------------------------------------------

    def add(self, item: Evidence):
        self.evidence.append(item)

    def extend(self, items: list[Evidence]):
        self.evidence.extend(items)

    # ---------------------------------------------------------
    # Filtering
    # ---------------------------------------------------------

    def by_source(self, source: str):

        return [
            e
            for e in self.evidence
            if e.source == source
        ]

    def by_category(self, category: str):

        return [
            e
            for e in self.evidence
            if e.category == category
        ]

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def average_confidence(self):

        if not self.evidence:
            return 0.0

        return sum(
            e.confidence
            for e in self.evidence
        ) / len(self.evidence)

    def weighted_confidence(self):

        if not self.evidence:
            return 0.0

        total = sum(
            e.confidence * e.importance
            for e in self.evidence
        )

        weights = sum(
            e.importance
            for e in self.evidence
        )

        if weights == 0:
            return 0.0

        return total / weights

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def sources(self):

        return sorted(
            {
                e.source
                for e in self.evidence
            }
        )

    def categories(self):

        return sorted(
            {
                e.category
                for e in self.evidence
            }
        )

    def clear(self):
        self.evidence.clear()

    def __len__(self):
        return len(self.evidence)

    def __iter__(self):
        return iter(self.evidence)