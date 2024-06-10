from abc import ABC, abstractmethod


class AgentRoleBase(ABC):
    pass


class TeamLeaderRole(AgentRoleBase):
    pass


class AnalystRole(AgentRoleBase):
    pass


class CowrieAnalystRole(AnalystRole):
    pass


class HoneypotDesignerRole(AgentRoleBase):
    pass


class CowrieDesignerRole(HoneypotDesignerRole):
    pass
