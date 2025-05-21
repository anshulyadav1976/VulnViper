# File: secureaudit/storage/models.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class ChunkAnalysis:
    file: str
    chunk_name: str
    chunk_type: str
    start_line: int
    end_line: int
    summary: Optional[str]
    vulnerabilities: Optional[list]
    recommendations: Optional[list]
    dependencies: Optional[list]
    parent_module: Optional[str] = ""

    def to_db_row(self):
        """Convert dataclass to tuple for DB insertion."""
        import json
        return (
            self.file,
            self.chunk_name,
            self.chunk_type,
            self.start_line,
            self.end_line,
            self.summary,
            json.dumps(self.vulnerabilities) if self.vulnerabilities else None,
            json.dumps(self.recommendations) if self.recommendations else None,
            json.dumps(self.dependencies) if self.dependencies else None,
            self.parent_module
        )

    def to_dict(self):
        """Convert dataclass to a dictionary for reporting or other uses."""
        return {
            "file": self.file,
            "chunk_name": self.chunk_name,
            "chunk_type": self.chunk_type,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "summary": self.summary,
            "vulnerabilities": self.vulnerabilities if self.vulnerabilities else [],
            "recommendations": self.recommendations if self.recommendations else [],
            "dependencies": self.dependencies if self.dependencies else [],
            "parent_module": self.parent_module
        }

    @staticmethod
    def from_db_row(row):
        """Convert DB row back into a ChunkAnalysis instance."""
        import json
        return ChunkAnalysis(
            file=row[1],
            chunk_name=row[2],
            chunk_type=row[3],
            start_line=row[4],
            end_line=row[5],
            summary=row[6],
            vulnerabilities=json.loads(row[7]) if row[7] else [],
            recommendations=json.loads(row[8]) if row[8] else [],
            dependencies=json.loads(row[9]) if row[9] else [],
            parent_module=row[10]
        )
