"""
system configuration
"""
from __future__ import annotations

import logging
import os
import sys
import typing
from functools import partial
from pathlib import Path
from typing import Any, Dict, Optional
from charset_normalizer import from_path
from importlib import import_module

from pydantic import (
    AnyHttpUrl,
    BaseSettings,
    DirectoryPath,
    FilePath,
    PositiveInt,
    RedisDsn,
    SecretStr,
    ValidationError,
    PostgresDsn,
)
from pydantic.env_settings import (
    EnvSettingsSource,
    InitSettingsSource,
    SecretsSettingsSource,
)
from pydantic_vault import vault_config_settings_source
from krispcall.common.auth_utils import security_constants

# from yaml import safe_load
LOGGER = logging.getLogger(__name__)


Mapping = typing.Mapping[str, typing.Any]
CONFIG_EXT = ".yaml"

SECONDS_IN_A_DAY: int = 86400


class CoreSettings(BaseSettings):
    """base settings"""

    app_id: str
    app_name: str
    base_path: Path

    # application paths
    var_path: DirectoryPath
    log_dir: DirectoryPath

    # docs path
    docs_path: DirectoryPath = typing.cast(DirectoryPath, "docs/")

    # default log filenames
    application_log_file: str = "application.log"
    database_log_file: str = "database.log"
    error_log_file: str = "error.log"

    # runtime information
    app_env: typing.Literal["development", "testing", "production"]
    debug: bool
    is_testing: bool = False

    # alembic specific
    components: typing.List[str]

    # application secrets
    secret_key: SecretStr

    # postgres settings
    pg_dsn: PostgresDsn
    pg_min_size: int = 5
    pg_max_size: int = 10
    pg_use_ssl: bool = True


class WebSettings(CoreSettings):
    """web application base settings"""

    app_uri: AnyHttpUrl

    # session/cookie domain
    session_lifetime: PositiveInt
    cookie_domain: typing.Optional[str]

    # logs
    access_log_file: str = "access.log"

    # cors
    enable_cors: bool = True
    cors_allow_origins: typing.List[str] = ["*"]

    cors_allow_methods: typing.Tuple[str, ...] = (
        "GET",
        "POST",
        "DELETE",
        "PUT",
        "PATCH",
        "HEAD",
        "OPTIONS",
    )
    cors_allow_credentials: bool = False
    cors_expose_headers: typing.List[str] = []
    cors_allow_headers: typing.List[str] = ["*"]
    cors_max_age: int = 600

    # jwt settings
    jwt_algorithms: typing.List[str] = security_constants.JWT_ALGORITHMS
    jwt_secret_public_pem: SecretStr
    jwt_audiences: typing.List[str] = []

    # allowed media types
    allowed_media_types: typing.Tuple[str, ...]


class Settings(WebSettings):
    """web application base settings"""

    app_uri: AnyHttpUrl
    redis_settings: RedisDsn
    send_grid_api_key: str
    broadcaster_dsn: RedisDsn

    # session/cookie domain
    session_lifetime: int = 7 * SECONDS_IN_A_DAY
    cookie_domain: typing.Optional[str]

    # logs
    access_log_file: str = "access.log"

    # cors
    cors_allow_origins: typing.List[str] = ["*"]

    cors_allow_methods: typing.Tuple[str, ...] = (
        "GET",
        "POST",
        "DELETE",
        "PUT",
        "PATCH",
        "HEAD",
        "OPTIONS",
    )
    # locations
    media_location = "/media/"
    permissions_location = "/permissions/"
    plans_location = "/billing_plans/"
    template_location = "/templates/"
    storage_url = "/storage/"
    config_location = "/config/"
    area_codes_location = "/area_codes/"
    usecase_location = "/usecases/"

    do_region_name: str
    do_spaces_root_name: str
    do_endpoint_url: AnyHttpUrl
    do_access_key_id: str
    do_secret_access_key: str
    # krispcall_twilio's conference_resource
    ring_url: AnyHttpUrl
    hold_url: AnyHttpUrl
    # for polly service
    region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str

    # all twilio credentials
    twilio_account_sid = ""
    twilio_auth_token: str

    test_twilio_account_sid = ""
    test_twilio_auth_token: str
    twilio_region = ""
    twilio_edge = ""

    # additional twilio settings for calls
    twilio_api_key = ""
    twilio_api_secret: str

    twilio_outgoing_application_sid = ""

    # stripe keys
    stripe_public_key: str
    stripe_secret_key: str
    stripe_endpoint_secret_key: str
    default_customer: str
    stripe_base_url: AnyHttpUrl

    # chargbee
    chargebee_api_key: str = ""
    chargebee_site_name: str = ""
    chargebee_webhook_key: str = ""

    # partnerstack
    partnerstack_public_key: str = ""
    partnerstack_secret_key: str = ""

    # fcm
    fcm_api_key: str

    # ios keys
    ios_cert: str
    ios_cert_key: str

    cors_allow_credentials: bool = False
    cors_expose_headers: typing.List[str] = []
    cors_allow_headers: typing.List[str] = ["*"]
    cors_max_age: int = 600

    login_attempt: int

    # allowed media types
    allowed_media_types: typing.Tuple[str, ...]

    # jwt
    jwt_algorithms: typing.List[str] = security_constants.JWT_ALGORITHMS + ["HS256"]
    jwt_audiences: typing.List[str] = []

    jwt_secret_private_pem: SecretStr
    jwt_secret_public_pem: SecretStr

    jwt_auth_token_lifetime_minutes: PositiveInt = typing.cast(
        PositiveInt, 1 * 7 * 24 * 60
    )
    jwt_access_token_lifetime_minutes: PositiveInt = typing.cast(
        PositiveInt, 1 * 7 * 24 * 60  # 1 week
    )
    jwt_refresh_token_lifetime_minutes: PositiveInt = typing.cast(
        PositiveInt, 2 * 7 * 24 * 60  # 2 week
    )

    jwt_reset_token_lifetime_minutes: PositiveInt = typing.cast(
        PositiveInt, 20  # 20 min
    )

    # polar
    polar_include_path: typing.Optional[DirectoryPath]

    # intercom_secret_key
    intercom_secret_key: bytes
    intercom_secret_key_android: bytes
    intercom_secret_key_ios: bytes
    intercom_app_secret_key: str

    # voice_token_public_pem
    voice_token_secret_key: str
    # postgres connection pool settings
    worker_pg_min_size: int = 2
    worker_pg_max_size: int = 3

    # google contact integration
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_url: str = ""
    google_project_id: str = ""

    # integromat url
    interogmat_url: str = ""

    desktop_app: dict = {}
    # support_email_inform
    support_emails: list = []
    ios_app_env: str = "production"

    domain_host: str = ""
    test_access_token: str = ""
    jwt_ttl: int = 86400
    rollbar_api_secret: str = ""
    rollbar_env: str = ""

    interogmat_workspace_review_url: str = ""

    one_signal_authorization_key: str = ""
    one_signal_app_id: str = ""
    interogmat_paid_user_data_url: str = ""

    otp_code_expiry_time: PositiveInt = typing.cast(PositiveInt, 5 * 60)  # 5 min

    otp_code_length: PositiveInt = typing.cast(PositiveInt, 6)

    otp_resend_expiry_time: PositiveInt = typing.cast(PositiveInt, 180)

    otp_remember_me_expiry_time: PositiveInt = typing.cast(
        PositiveInt, 30 * 24 * 60 * 60
    )

    slack_token: str = ""
    slack_message_channel: str = ""

    # hubspot auth details
    hubspot_redirect_uri: str = ""
    hubspot_client_id: str = ""
    hubspot_client_secret: str = ""
    hubspot_developer_api_key: str = ""
    # hubspot_app_id: int = None
    hubspot_scopes: str = ""

    fcm_push_url: str = ""

    ph_mobile_sms_forever: str = ""
    ph_mobile_sms_onetime: str = ""
    sg_mobile_sms_forever: str = ""
    sg_mobile_sms_onetime: str = ""
    phone_numbers_promo_code_forever: str = ""
    phone_numbers_promo_code_onetime: str = ""
    mixpanel_token: str = ""
    make_url: str = ""
    api_key: str = ""

    # pipedrive auth details
    pipedrive_client_id: str = ""
    pipedrive_client_secret: str = ""
    pipedrive_redirect_uri: str = ""
    pipedrive_webhook_url: str = ""
    pipedrive_api_token: str = ""
    pipedrive_krispcall_id_key: str = ""

    # dynamics auth details
    dynamics_redirect_uri: str = ""
    dynamics_client_id: str = ""
    dynamics_client_secret: str = ""
    dynamics_webhook_url: str = ""

    salesforce_redirect_uri: str = ""
    salesforce_client_id: str = ""
    salesforce_client_secret: str = ""

    zapier_client_id: str = ""
    zapier_redirect_uri: str = ""

    bitrix24_client_id: str = ""
    bitrix24_client_secret: str = ""
    bitrix24_redirect_uri: str = ""
    bitrix24_event_handler: str = ""

    auto_recharge_cooldown_time: int = 0

    forgot_password_expiration: int = 0
    forgot_password_cooldown: int = 0

    credit_toggle_cooldown: int = 0
    auto_renewal_toogle_cooldown: int = 60

    # business rules variables
    mms_charge: float
    number_add_limit_for_non_kyc: PositiveInt

    # Weekly Number subscription price id
    weekly_number_subscription_price_id: str

    # Monthly Number subscription price id
    monthly_number_subscription_price_id: str

    # total members for Essential plan
    members_count: PositiveInt

    # Minimum Risk score
    risk_score: PositiveInt

    # carrier charge is not applied to Australia (AU)
    mms_carrier_charge: float
    mms_charge_au: float

    # Default Credit
    default_credit: float

    # Default emails to skip OTP verification
    disable_otp_emails: list = []

    # CrispChat auth details
    crispchat_identifier: str = ""
    crispchat_key: str = ""
    crispchat_webhook_url: str = ""
    crispchat_base_uri: str = ""



def resolve_path_from_config(settings: CoreSettings, path: Path) -> Path:
    """resolve/expand path using settings"""
    return path if path.is_absolute() else settings.base_path.joinpath(path)


def resolve_component_module_locations(
    components: typing.List[str], module_name: str
) -> typing.List[Path]:
    """resolve component module locations for defined components"""
    locations = []
    for modname in components:
        mod = import_module(modname)
        locations.append(Path(mod.__file__).parent.joinpath(module_name))
    return locations


def resolve_component_module_location(
    component: str, module_name: str
) -> Path:
    """resolve component module locations for defined component"""
    module = import_module(component)
    return Path(module.__file__).parent.joinpath(module_name) 