from config import (
    DEFAULT_MEMORY_PROMPT,
    API_SERVICE_URL,
    END_CALL_TOOL_PROMPT,
    RETRIEVE_MEMORY_TOOL_PROMPT,
)

tools_payload = [
    {
        "type": "webhook",
        "name": "RETRIEVE_MEMORY_TOOL",
        "description": 'Use this tool to retrieve information from the user\'s memory. Use it as much as possible.\nEvery time the user says something, or ask you something that is not present in your knowledge base,\nuse this tool to retrieve information from the user\'s memory. If the retrieved information add value to\nthe conversation, use it to answer the user\'s question.\nThe request body must be a JSON object with the following fields:\n- agent_id: The ID of the agent, whose value is stored in the dynamic variable `agent_id`\n- text: The text to search the memory for.\ni.e:\n{\n    "agent_id": "{{agent_id}}",\n    "text": "{{text}}"\n}',
        "dynamic_variables": {"dynamic_variable_placeholders": {}},
        "api_schema": {
            "url": "https://someurl_other:8000",
            "method": "POST",
            "request_body_schema": {
                "type": "object",
                "description": "Use this tool to retrieve information from the user's memory. Use it as much as possible.\nEvery time the user says something, or ask you something that is not present in your knowledge base,\nuse this tool to retrieve information from the user's memory. If the retrieved information add value to\nthe conversation, use it to answer the user's question.\n",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "he ID of the agent, whose value is stored in the dynamic variable `agent_id`",
                        "dynamic_variable": "",
                        "constant_value": "",
                    },
                    "text": {
                        "type": "string",
                        "description": "The text to search the memory for",
                        "dynamic_variable": "",
                        "constant_value": "",
                    },
                },
                "required": ["agent_id", "text"],
            },
            "request_headers": {},
        },
    },
    {
        "type": "webhook",
        "name": "END_CALL",
        "description": 'At the end of the call, sends a summary of the conversation to the following endpoint.\nThe request body must be a JSON object with the following fields:\n- agent_id: The ID of the agent, whose value is stored in the dynamic variable `agent_id`\n- memory_id: The ID of the memory, whose value is stored in the dynamic variable `memory_id`\n- text: The summary of the conversation, must be as detailed as possible. \ni.e:\n{\n    "agent_id": "{{agent_id}}",\n    "memory_id": "{{memory_id}}",\n    "text": "{{text}}"\n}',
        "dynamic_variables": {"dynamic_variable_placeholders": {}},
        "api_schema": {
            "url": "https://someurl:8000",
            "method": "POST",
            "request_body_schema": {
                "type": "object",
                "description": "At the end of the conversation, sends a summary of the conversation AS DETAILED AS POSSIBLE",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "The ID of the agent, whose value is stored in the dynamic variable `agent_id`",
                        "dynamic_variable": "",
                        "constant_value": "",
                    },
                    "memory_id": {
                        "type": "string",
                        "description": "The ID of the memory, whose value is stored in the dynamic variable `memory_id`",
                        "dynamic_variable": "",
                        "constant_value": "",
                    },
                    "text": {
                        "type": "string",
                        "description": "The summary of the conversation, must be as detailed as possible.",
                        "dynamic_variable": "",
                        "constant_value": "",
                    },
                },
                "required": ["agent_id", "memory_id", "text"],
            },
            "request_headers": {},
        },
    },
]


create_agent_payload = {
    "conversation_config": {
        "agent": {
            "prompt": {
                "model": "gpt-4o-mini",
                "prompt": DEFAULT_MEMORY_PROMPT,
            },
            "dynamic_variables": {
                "agent_id": "str",
                "memory_id": "str",
            },
        },
    },
    "platform_settings": {
        "auth": {
            "enable_auth": False,
        },
    },
}


def load_tools_payload():
    """
    Load tools into an ElevenLabs agent
    """

    return tools_payload


def load_memory_payload(memory: str):
    return {
        "conversation_config": {
            "agent": {
                "prompt": {
                    "prompt": memory,
                },
            },
        },
    }


PATCH_AGENT_PAYLOAD = {
    "name": "Agent 63gww",
    "conversation_config": {
        "agent": {
            "first_message": "",
            "language": "en",
            "dynamic_variables": {
                "dynamic_variable_placeholders": {
                    "agent_id": "some",
                    "memory_id": "agent_tool",
                }
            },
            "prompt": {
                "prompt": "\n“You are the alter ego of **name**\n\nWho am I (long term memory)\n\nHow's life been lately (short term memory)\n\nWhat was the topic of our latest conversation (short term memory)\n\n{{agent_id}} {{memory_id}}\n",
                "max_tokens": -1,
                "temperature": 0,
                "llm": "gemini-2.0-flash-001",
                "knowledge_base": [],
                "custom_llm": None,
                "rag": {
                    "enabled": False,
                    "embedding_model": "e5_mistral_7b_instruct",
                    "max_documents_length": 50000,
                    "max_vector_distance": 0.6,
                },
                "tools": [
                    # {
                    #     "type": "webhook",
                    #     "name": "RETRIEVE_MEMORY_TOOL",
                    #     "description": 'Use this tool to retrieve information from the user\'s memory. Use it as much as possible.\nEvery time the user says something, or ask you something that is not present in your knowledge base,\nuse this tool to retrieve information from the user\'s memory. If the retrieved information add value to\nthe conversation, use it to answer the user\'s question.\nThe request body must be a JSON object with the following fields:\n- agent_id: The ID of the agent, whose value is stored in the dynamic variable `agent_id`\n- text: The text to search the memory for.\ni.e:\n{\n    "agent_id": "{{agent_id}}",\n    "text": "{{text}}"\n}',
                    #     "dynamic_variables": {"dynamic_variable_placeholders": {}},
                    #     "api_schema": {
                    #         "url": f"{API_SERVICE_URL}/memory/get",
                    #         "method": "POST",
                    #         "request_body_schema": {
                    #             "type": "object",
                    #             "description": "Use this tool to retrieve information from the user's memory. Use it as much as possible.\nEvery time the user says something, or ask you something that is not present in your knowledge base,\nuse this tool to retrieve information from the user's memory. If the retrieved information add value to\nthe conversation, use it to answer the user's question.\n",
                    #             "properties": {
                    #                 "agent_id": {
                    #                     "type": "string",
                    #                     "description": "he ID of the agent, whose value is stored in the dynamic variable `agent_id`",
                    #                     "dynamic_variable": "",
                    #                     "constant_value": "",
                    #                 },
                    #                 "text": {
                    #                     "type": "string",
                    #                     "description": "The text to search the memory for",
                    #                     "dynamic_variable": "",
                    #                     "constant_value": "",
                    #                 },
                    #             },
                    #             "required": ["agent_id", "text"],
                    #         },
                    #         "request_headers": {},
                    #     },
                    # },
                    # {
                    #     "type": "webhook",
                    #     "name": "END_CALL",
                    #     "description": 'At the end of the call, sends a summary of the conversation to the following endpoint.\nThe request body must be a JSON object with the following fields:\n- agent_id: The ID of the agent, whose value is stored in the dynamic variable `agent_id`\n- memory_id: The ID of the memory, whose value is stored in the dynamic variable `memory_id`\n- text: The summary of the conversation, must be as detailed as possible. \ni.e:\n{\n    "agent_id": "{{agent_id}}",\n    "memory_id": "{{memory_id}}",\n    "text": "{{text}}"\n}',
                    #     "dynamic_variables": {"dynamic_variable_placeholders": {}},
                    #     "api_schema": {
                    #         "url": f"{API_SERVICE_URL}/memory/update",
                    #         "method": "POST",
                    #         "request_body_schema": {
                    #             "type": "object",
                    #             "description": "At the end of the conversation, sends a summary of the conversation AS DETAILED AS POSSIBLE",
                    #             "properties": {
                    #                 "agent_id": {
                    #                     "type": "string",
                    #                     "description": "The ID of the agent, whose value is stored in the dynamic variable `agent_id`",
                    #                     "dynamic_variable": "",
                    #                     "constant_value": "",
                    #                 },
                    #                 "memory_id": {
                    #                     "type": "string",
                    #                     "description": "The ID of the memory, whose value is stored in the dynamic variable `memory_id`",
                    #                     "dynamic_variable": "",
                    #                     "constant_value": "",
                    #                 },
                    #                 "text": {
                    #                     "type": "string",
                    #                     "description": "The summary of the conversation, must be as detailed as possible.",
                    #                     "dynamic_variable": "",
                    #                     "constant_value": "",
                    #                 },
                    #             },
                    #             "required": ["agent_id", "memory_id", "text"],
                    #         },
                    #         "request_headers": {},
                    #     },
                    # },
                ],
            },
        },
        "asr": {
            "quality": "high",
            "provider": "elevenlabs",
            "user_input_audio_format": "pcm_16000",
            "keywords": [],
        },
        "tts": {
            "voice_id": "cjVigY5qzO86Huf0OWal",
            "model_id": "eleven_turbo_v2",
            "agent_output_audio_format": "pcm_16000",
            "optimize_streaming_latency": 3,
            "stability": 0.5,
            "speed": 1,
            "similarity_boost": 0.8,
            "pronunciation_dictionary_locators": [],
        },
        "turn": {"turn_timeout": 7, "silence_end_call_timeout": -1},
        "conversation": {
            "max_duration_seconds": 600,
            "client_events": ["audio", "interruption"],
        },
        "language_presets": {},
    },
    "platform_settings": {
        "widget": {
            "variant": "full",
            "expandable": "never",
            "feedback_mode": "none",
            "avatar": {"type": "orb", "color_1": "#2792dc", "color_2": "#9ce6e6"},
            "language_selector": False,
            "bg_color": "#ffffff",
            "text_color": "#000000",
            "btn_color": "#000000",
            "btn_text_color": "#ffffff",
            "border_color": "#e1e1e1",
            "focus_color": "#000000",
            "border_radius": None,
            "btn_radius": None,
            "action_text": None,
            "start_call_text": None,
            "end_call_text": None,
            "expand_text": None,
            "listening_text": None,
            "speaking_text": None,
            "terms_text": None,
            "terms_key": None,
            "shareable_page_text": None,
            "shareable_page_show_terms": True,
            "show_avatar_when_collapsed": False,
            "mic_muting_enabled": False,
        },
        "evaluation": {"criteria": []},
        "auth": {"enable_auth": False, "allowlist": []},
        "overrides": {
            "enable_conversation_initiation_client_data_from_webhook": False,
            "custom_llm_extra_body": False,
            "conversation_config_override": {
                "agent": {
                    "prompt": {"prompt": False},
                    "first_message": False,
                    "language": False,
                },
                "tts": {"voice_id": False},
            },
        },
        "call_limits": {"agent_concurrency_limit": -1, "daily_limit": 100000},
        "privacy": {
            "record_voice": True,
            "retention_days": -1,
            "delete_transcript_and_pii": False,
            "delete_audio": False,
            "apply_to_existing_conversations": False,
        },
        "data_collection": {},
        "workspace_overrides": {},
    },
}
