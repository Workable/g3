from typing import Optional

from g3.domain.message_tone import MessageTone


class Creator:
    def create(self, tone: MessageTone, jira: Optional[str] = None, include: Optional[str] = None) -> list:
        raise NotImplementedError
