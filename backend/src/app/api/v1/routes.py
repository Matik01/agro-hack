from pathlib import Path
import pandas as pd
from openpyxl import load_workbook

from schemas.api_schemas import AgroResponse, AgroRequest
from fastapi import APIRouter, Depends, HTTPException
from services.model import YandexGPT
from app.config.config import get_settings
from utils.json_to_dataframe import json_to_dataframe
from services.google_drive_service import upload_file_to_drive
from fastapi import BackgroundTasks

import traceback
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/agro",
    tags=["agro"],
)



@router.post("/process", response_model=AgroResponse)
def process_agro_message(request: AgroRequest,
                         settings=Depends(get_settings),
                         background_tasks: BackgroundTasks):
    def process_message():
        try:
            model = YandexGPT(settings=settings)
            json_output = model.run_model(request.message)
            decoded_message = json_to_dataframe(json_output)
            file_name = f'{request.id}_place_for_your_ads.xlsx'
            path_to_file = Path(settings.OUTPUT_DATA_FOLDER) / file_name

            if not path_to_file.is_file():
                decoded_message.to_excel(excel_writer=path_to_file, index=False)
            else:
                with pd.ExcelWriter(path_to_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                    existing_df = pd.read_excel(path_to_file)
                    start_row = len(existing_df) + 1
                    decoded_message.to_excel(writer, index=False, header=False, startrow=start_row)

            upload_file_to_drive(file_path=path_to_file, file_name=file_name)

        except Exception as e:
            logger.error("Ошибка при обработке запроса:\n%s", traceback.format_exc())
            raise HTTPException(status_code=500, detail=str(e))

    background_tasks.add_task(process_message)

    return AgroResponse(status='Added message to task queue')
