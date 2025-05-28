from collections.abc import Generator
from typing import Any, Optional


from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from pydantic import BaseModel, Field

from utils.common_utils import get_redis_connection, NotEmptyStr


class RedisSetKeepTTLActionParameters(BaseModel):
    name: NotEmptyStr
    key: NotEmptyStr
    ttl: Optional[int] = Field(default=60)


class RedisSetKeepTTLAction(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            tool_parameters_model = RedisSetKeepTTLActionParameters(**tool_parameters)
            redis_key = tool_parameters_model.name + ':' + tool_parameters_model.key
            conn = get_redis_connection(self.runtime.credentials)

            new_count = conn.incr(redis_key)

            if tool_parameters_model.ttl > 0 >= conn.ttl(redis_key):
                conn.expire(name=redis_key, time=tool_parameters_model.ttl)

            yield self.create_text_message(str(new_count))
        except Exception as e:
            raise Exception(f"Plugin invoke fail: {type(e)}: {e}")
