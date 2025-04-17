from langchain.chains.llm import LLMChain
from langchain_community.chat_models import ChatYandexGPT
from langchain_core.messages import AIMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.chains.sequential import SimpleSequentialChain
from langchain.chains.transform import TransformChain

from app import constants

import re
import json


class YandexGPT:
    def __init__(self, settings):
        self._model = ChatYandexGPT(
            api_key=settings.YANDEX_API_KEY,
            model_uri=settings.YANDEX_MODEL_URI,
            temperature=0)

    def run_model(self, message: str) -> dict:
        transform_chain_references = TransformChain(
            input_variables=["input"],
            output_variables=["input"],
            transform=self.__normalize_references
        )

        transform_chain_operation = TransformChain(
            input_variables=["input"],
            output_variables=["input"],
            transform=self.__normalize_operation
        )

        transform_chain_cultures = TransformChain(
            input_variables=["input"],
            output_variables=["input"],
            transform=self.__normalize_cultures
        )

        transform_chain_aor = TransformChain(
            input_variables=["output"],
            output_variables=["output"],
            transform=self.__assign_department
        )

        system_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(constants.AppConstants.SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template("{input}")
        ])

        llm_chain = LLMChain(prompt=system_prompt, llm=self._model)
        full_chain = SimpleSequentialChain(
            chains=[transform_chain_references,
                    transform_chain_operation,
                    transform_chain_cultures,
                    llm_chain,
                    transform_chain_aor],
            input_key="input",
            output_key="output",
            verbose=False
        )
        model_output = full_chain.run(message)

        return self.__model_output_to_json(model_output)

    def __model_output_to_json(self, response: AIMessage) -> dict:
        cleaned = re.sub(r'^```(json)?|```$', '', response, flags=re.MULTILINE).strip()

        return json.loads(cleaned)

    def __normalize_operation(self, inputs: dict) -> dict:
        text = inputs["input"]
        text = re.sub(r"внесение\s+почв\w*\s+гербицид\w*", "внесение гербицидов", text, flags=re.IGNORECASE)

        return {"input": text}

    def __assign_department(self, inputs: dict) -> dict:
        import json
        import re

        raw_output = inputs["output"]

        if isinstance(raw_output, str):
            cleaned_output = re.sub(r"^```(?:json)?\n?", "", raw_output.strip(), flags=re.IGNORECASE)
            cleaned_output = re.sub(r"\n?```$", "", cleaned_output.strip())
            try:
                data = json.loads(cleaned_output)
            except json.JSONDecodeError:
                raise ValueError("Не удалось декодировать JSON. Получен текст:\n" + cleaned_output)
        else:
            data = raw_output

        aor_departments = {1, 3, 4, 5, 6, 7, 9, 10, 11, 12, 16, 17, 18, 19, 20}

        new_operations = []

        for op in data.get("операции", []):
            otd = op.get("отделение")
            if isinstance(otd, list):
                for idx, sub_otd in enumerate(otd):
                    new_op = op.copy()
                    new_op["отделение"] = sub_otd

                    if isinstance(op.get("площадь", {}).get("за_день"), list):
                        new_op["площадь"] = {
                            "за_день": op["площадь"]["за_день"][idx],
                            "c_начала_операции": op["площадь"]["c_начала_операции"][idx]
                        }

                    if not new_op.get("подразделение") and sub_otd in aor_departments:
                        new_op["подразделение"] = "АОР"

                    new_operations.append(new_op)
            else:
                if otd in aor_departments and not op.get("подразделение"):
                    op["подразделение"] = "АОР"
                new_operations.append(op)

        data["операции"] = new_operations
        return {"output": json.dumps(data, ensure_ascii=False)}

    def __normalize_references(self, inputs: dict) -> dict:
        text = inputs["input"]

        text = re.sub(r"(по\s*п[уyу]|п[уyу])\s*(\d+)\s*/\s*(\d+)", r"ПУ \2/\3", text, flags=re.IGNORECASE)

        text = re.sub(r"(отд\.?|отделение)\s*-?\s*(\d+)[\s:]*[-]?\s*(\d+)\s*/\s*(\d+)", r"Отделение \2 \3/\4", text,
                      flags=re.IGNORECASE)

        text = re.sub(r"(отд\.?|отделение)\s*-?\s*(\d+)\s*/\s*(\d+)", r"Отделение \2/\3", text, flags=re.IGNORECASE)

        text = re.sub(r"(отд\.?|отделение)\s*-?\s*(\d+)[\s-]+(\d+)/(\d+)", r"Отделение \2 \3/\4", text,
                      flags=re.IGNORECASE)

        return {"input": text}

    def __normalize_cultures(self, inputs: dict) -> dict:
        text = inputs["input"]

        text = re.sub(
            r"\b(озим(ых|ая|ой|ую)?|оз(ы|им)?|зим(ых|няя|ою)?)\b",
            "Пшеница озимая товарная",
            text,
            flags=re.IGNORECASE
        )
        return {"input": text}
