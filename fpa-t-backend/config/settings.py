"""Runtime settings (ISP S2, AP DD-R20-09).

.env can override defaults silently (AP S13 gotcha #14). Log resolved values on boot.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gcp_project: str = "fpa-t-494007"
    bq_dataset_so_rows: str = "so_rows"
    app_env: str = "dev"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
print(f"[BOOT] gcp_project={settings.gcp_project} dataset={settings.bq_dataset_so_rows} env={settings.app_env}")
