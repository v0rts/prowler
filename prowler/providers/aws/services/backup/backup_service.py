import threading
from datetime import datetime

from pydantic import BaseModel

from prowler.lib.logger import logger
from prowler.lib.scan_filters.scan_filters import is_resource_filtered
from prowler.providers.aws.aws_provider import generate_regional_clients


################## Backup
class Backup:
    def __init__(self, audit_info):
        self.service = "backup"
        self.session = audit_info.audit_session
        self.audited_account = audit_info.audited_account
        self.audit_resources = audit_info.audit_resources
        self.regional_clients = generate_regional_clients(self.service, audit_info)
        # If the region is not set in the audit profile,
        # we pick the first region from the regional clients list
        self.region = (
            audit_info.profile_region
            if audit_info.profile_region
            else list(self.regional_clients.keys())[0]
        )
        self.backup_vaults = []
        self.__threading_call__(self.__list_backup_vaults__)
        self.backup_plans = []
        self.__threading_call__(self.__list_backup_plans__)
        self.backup_report_plans = []
        self.__threading_call__(self.__list_backup_report_plans__)

    def __threading_call__(self, call):
        threads = []
        for regional_client in self.regional_clients.values():
            threads.append(threading.Thread(target=call, args=(regional_client,)))
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def __list_backup_vaults__(self, regional_client):
        logger.info("Backup - Listing Backup Vaults...")
        try:
            list_backup_vaults_paginator = regional_client.get_paginator(
                "list_backup_vaults"
            )
            for page in list_backup_vaults_paginator.paginate():
                for configuration in page.get("BackupVaultList"):
                    if not self.audit_resources or (
                        is_resource_filtered(
                            configuration.get("BackupVaultArn"),
                            self.audit_resources,
                        )
                    ):
                        self.backup_vaults.append(
                            BackupVault(
                                arn=configuration.get("BackupVaultArn"),
                                name=configuration.get("BackupVaultName"),
                                region=regional_client.region,
                                encryption=configuration.get("EncryptionKeyArn"),
                                recovery_points=configuration.get(
                                    "NumberOfRecoveryPoints"
                                ),
                                locked=configuration.get("Locked"),
                                min_retention_days=configuration.get(
                                    "MinRetentionDays"
                                ),
                                max_retention_days=configuration.get(
                                    "MaxRetentionDays"
                                ),
                            )
                        )

        except Exception as error:
            logger.error(
                f"{regional_client.region} -- {error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
            )

    def __list_backup_plans__(self, regional_client):
        logger.info("Backup - Listing Backup Plans...")
        try:
            list_backup_plans_paginator = regional_client.get_paginator(
                "list_backup_plans"
            )
            for page in list_backup_plans_paginator.paginate():
                for configuration in page.get("BackupPlansList"):
                    if not self.audit_resources or (
                        is_resource_filtered(
                            configuration.get("BackupPlanArn"),
                            self.audit_resources,
                        )
                    ):
                        self.backup_plans.append(
                            BackupPlan(
                                arn=configuration.get("BackupPlanArn"),
                                id=configuration.get("BackupPlanId"),
                                region=regional_client.region,
                                name=configuration.get("BackupPlanName"),
                                version_id=configuration.get("VersionId"),
                                last_execution_date=configuration.get(
                                    "LastExecutionDate"
                                ),
                                advanced_settings=configuration.get(
                                    "AdvancedBackupSettings"
                                ),
                            )
                        )

        except Exception as error:
            logger.error(
                f"{regional_client.region} -- {error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
            )

    def __list_backup_report_plans__(self, regional_client):
        logger.info("Backup - Listing Backup Report Plans...")

        try:
            list_backup_report_plans = regional_client.list_report_plans()[
                "ReportPlans"
            ]
            for backup_report_plan in list_backup_report_plans:
                if not self.audit_resources or (
                    is_resource_filtered(
                        backup_report_plan.get("ReportPlanArn"),
                        self.audit_resources,
                    )
                ):
                    self.backup_report_plans.append(
                        BackupReportPlan(
                            arn=backup_report_plan.get("ReportPlanArn"),
                            region=regional_client.region,
                            name=backup_report_plan.get("ReportPlanName"),
                            last_attempted_execution_date=backup_report_plan.get(
                                "LastAttemptedExecutionTime"
                            ),
                            last_successful_execution_date=backup_report_plan.get(
                                "LastSuccessfulExecutionTime"
                            ),
                        )
                    )

        except Exception as error:
            logger.error(
                f"{regional_client.region} -- {error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
            )


class BackupVault(BaseModel):
    arn: str
    name: str
    region: str
    encryption: str
    recovery_points: int
    locked: bool
    min_retention_days: int = None
    max_retention_days: int = None


class BackupPlan(BaseModel):
    arn: str
    id: str
    region: str
    name: str
    version_id: str
    last_execution_date: datetime
    advanced_settings: list


class BackupReportPlan(BaseModel):
    arn: str
    region: str
    name: str
    last_attempted_execution_date: datetime
    last_successful_execution_date: datetime
