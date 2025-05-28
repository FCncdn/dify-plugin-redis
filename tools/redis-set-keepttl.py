from collections.abc import Generator
from typing import Any, Optional


from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from pydantic import BaseModel, Field

from utils.common_utils import get_redis_connection, NotEmptyStr


class RedisSetKeepTTLParameter(BaseModel):
    name: NotEmptyStr
    key: NotEmptyStr
    value: NotEmptyStr
    ttl: Optional[int] = Field(default=60)


class RedisSetKeepTTL(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            tool_parameters_model = RedisSetKeepTTLParameter(**tool_parameters)
            redis_key = tool_parameters_model.name + ':' + tool_parameters_model.key
            conn = get_redis_connection(self.runtime.credentials)

            key_ttl = conn.ttl(name=redis_key)
            if key_ttl <= 0 < tool_parameters_model.ttl:
                conn.setex(redis_key, tool_parameters_model.ttl, tool_parameters_model.value)
            else:
                conn.set(name=redis_key, value=tool_parameters_model.value, keepttl=True)
            yield self.create_text_message(tool_parameters_model.value)
        except Exception as e:
            raise Exception(f"Plugin invoke fail: {type(e)}: {e}")
