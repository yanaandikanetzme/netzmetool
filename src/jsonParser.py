#lokasi src/jsonParser.py
import json
import re
from functools import lru_cache

class jsonParser():
    def __init__(self):
        self.recursion_limit = 100

    @staticmethod
    def unescape(s):
        if isinstance(s, str):
            # Handle double escaped strings
            if s.startswith('"') and s.endswith('"'):
                s = s[1:-1]
            # Replace escaped backslashes first
            s = s.replace('\\\\', '\\')
            # Then handle other escaped characters
            s = s.replace('\\"', '"')
            return s.encode('utf-8').decode('unicode_escape')
        return s

    @classmethod
    def clean_json_string(cls, json_string):
        if isinstance(json_string, str):
            # Remove literal backslashes
            cleaned = json_string.replace('\\', '')
            # If the string is wrapped in quotes, remove them
            if cleaned.startswith('"') and cleaned.endswith('"'):
                cleaned = cleaned[1:-1]
            return cleaned
        return json_string

    @classmethod
    def initial_parse(cls, json_string):
        try:
            # First try parsing as is
            return json.loads(
                json_string,
                parse_int=lambda x: str(x),
                parse_float=lambda x: str(x)
            )
        except json.JSONDecodeError:
            try:
                # If that fails, try cleaning the string first
                cleaned_json = cls.clean_json_string(json_string)
                return json.loads(
                    cleaned_json,
                    parse_int=lambda x: str(x),
                    parse_float=lambda x: str(x)
                )
            except json.JSONDecodeError:
                # If all parsing fails, return as is
                return json_string

    @classmethod
    def process_value(cls, value, depth=0):
        if depth > 100:
            return value
        
        if isinstance(value, dict):
            return {k: cls.process_value(v, depth + 1) for k, v in value.items()}
        elif isinstance(value, list):
            return [cls.process_value(item, depth + 1) for item in value]
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            try:
                # Check if the string is actually a JSON
                parsed = json.loads(
                    value,
                    parse_int=lambda x: str(x),
                    parse_float=lambda x: str(x)
                )
                return cls.process_value(parsed, depth + 1)
            except json.JSONDecodeError:
                return value
        return value

    @classmethod
    def preprocess_input(cls, json_data):
        if isinstance(json_data, str):
            try:
                parsed_data = cls.initial_parse(json_data)
                return cls.process_value(parsed_data)
            except Exception:
                return json_data
        return cls.process_value(json_data)

    @classmethod
    def jsonParserBeautify(cls, json_data):
        try:
            obj = cls.preprocess_input(json_data)
            if isinstance(obj, (dict, list)):
                return json.dumps(obj, indent=2, ensure_ascii=False)
            return obj
        except Exception as e:
            return f"Error processing JSON: {str(e)}"

    @classmethod
    def jsonParserMinify(cls, json_data):
        try:
            obj = cls.preprocess_input(json_data)
            if isinstance(obj, (dict, list)):
                return json.dumps(obj, separators=(',', ':'), ensure_ascii=False)
            return obj
        except Exception as e:
            return f"Error processing JSON: {str(e)}"

    @classmethod
    def jsonParserLoads(cls, input_data):
        try:
            return cls.preprocess_input(input_data)
        except Exception as e:
            return f"Error loading JSON: {str(e)}"

    @staticmethod
    def is_json_string(input_data):
        if not isinstance(input_data, str):
            return False
        try:
            json.loads(input_data)
            return True
        except json.JSONDecodeError:
            return False

    @staticmethod
    def is_json_object(input_data):
        return isinstance(input_data, (dict, list))