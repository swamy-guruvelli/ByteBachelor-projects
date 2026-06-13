from dataclasses import dataclass


@dataclass
class ProblemError(Exception):
    status: int
    title: str
    detail: str
    code: str

