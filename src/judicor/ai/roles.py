from enum import Enum


class AgentRole(str, Enum):
    ANALYZER = "analyzer"
    INVESTIGATOR = "investigator"
    SUMMARIZER = "summarizer"
    RESOLVER = "resolver"
