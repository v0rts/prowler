from datetime import datetime
from unittest import mock

from prowler.providers.aws.services.cognito.cognito_service import (
    UserPool,
    UserPoolClient,
)
from tests.providers.aws.utils import AWS_ACCOUNT_NUMBER, AWS_REGION_US_EAST_1


class Test_cognito_user_pool_client_token_revocation_enabled:
    def test_cognito_no_user_pools(self):
        cognito_client = mock.MagicMock
        cognito_client.user_pools = {}
        with (
            mock.patch(
                "prowler.providers.aws.services.cognito.cognito_service.CognitoIDP",
                new=cognito_client,
            ),
            mock.patch(
                "prowler.providers.aws.services.cognito.cognito_idp_client.cognito_idp_client",
                new=cognito_client,
            ),
        ):
            from prowler.providers.aws.services.cognito.cognito_user_pool_client_token_revocation_enabled.cognito_user_pool_client_token_revocation_enabled import (
                cognito_user_pool_client_token_revocation_enabled,
            )

            check = cognito_user_pool_client_token_revocation_enabled()
            result = check.execute()

            assert len(result) == 0

    def test_cognito_user_pools_token_revocation_disabled(self):
        cognito_client = mock.MagicMock
        user_pool_arn = f"arn:aws:cognito-idp:{AWS_REGION_US_EAST_1}:{AWS_ACCOUNT_NUMBER}:userpool/eu-west-1_123456789"
        user_pool_name = "user_pool_name"
        user_pool_id = "eu-west-1_123456789"
        user_pool_client_id = "eu-west-1_123456789"
        user_pool_client_name = "eu-west-1_123456789"
        user_pool_client_arn = f"{user_pool_arn}/client/{user_pool_client_id}"
        cognito_client.user_pools = {
            user_pool_arn: UserPool(
                user_pool_clients={
                    user_pool_client_id: UserPoolClient(
                        id=user_pool_client_id,
                        name=user_pool_client_name,
                        region=AWS_REGION_US_EAST_1,
                        arn=user_pool_client_arn,
                        enable_token_revocation=False,
                    )
                },
                region=AWS_REGION_US_EAST_1,
                id=user_pool_id,
                arn=user_pool_arn,
                name=user_pool_name,
                last_modified=datetime.now(),
                creation_date=datetime.now(),
                status="ACTIVE",
            )
        }
        with (
            mock.patch(
                "prowler.providers.aws.services.cognito.cognito_service.CognitoIDP",
                new=cognito_client,
            ),
            mock.patch(
                "prowler.providers.aws.services.cognito.cognito_idp_client.cognito_idp_client",
                new=cognito_client,
            ),
        ):
            from prowler.providers.aws.services.cognito.cognito_user_pool_client_token_revocation_enabled.cognito_user_pool_client_token_revocation_enabled import (
                cognito_user_pool_client_token_revocation_enabled,
            )

            check = cognito_user_pool_client_token_revocation_enabled()
            result = check.execute()

            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert result[0].status_extended == (
                f"User pool client {user_pool_client_name} has token revocation disabled."
            )

            assert result[0].resource_id == user_pool_client_id
            assert result[0].resource_arn == user_pool_client_arn

    def test_project_user_pools_token_revocation_enabled(self):
        cognito_client = mock.MagicMock
        user_pool_arn = f"arn:aws:cognito-idp:{AWS_REGION_US_EAST_1}:{AWS_ACCOUNT_NUMBER}:userpool/eu-west-1_123456789"
        user_pool_name = "user_pool_name"
        user_pool_id = "eu-west-1_123456789"
        user_pool_client_id = "eu-west-1_123456789"
        user_pool_client_name = "eu-west-1_123456789"
        user_pool_client_arn = f"{user_pool_arn}/client/{user_pool_client_id}"
        cognito_client.user_pools = {
            user_pool_arn: UserPool(
                user_pool_clients={
                    user_pool_client_id: UserPoolClient(
                        id=user_pool_client_id,
                        name=user_pool_client_name,
                        arn=user_pool_client_arn,
                        region=AWS_REGION_US_EAST_1,
                        enable_token_revocation=True,
                    )
                },
                region=AWS_REGION_US_EAST_1,
                id=user_pool_id,
                arn=user_pool_arn,
                name=user_pool_name,
                last_modified=datetime.now(),
                creation_date=datetime.now(),
                status="ACTIVE",
            )
        }
        with (
            mock.patch(
                "prowler.providers.aws.services.cognito.cognito_service.CognitoIDP",
                new=cognito_client,
            ),
            mock.patch(
                "prowler.providers.aws.services.cognito.cognito_idp_client.cognito_idp_client",
                new=cognito_client,
            ),
        ):
            from prowler.providers.aws.services.cognito.cognito_user_pool_client_token_revocation_enabled.cognito_user_pool_client_token_revocation_enabled import (
                cognito_user_pool_client_token_revocation_enabled,
            )

            check = cognito_user_pool_client_token_revocation_enabled()
            result = check.execute()

            assert len(result) == 1
            assert result[0].status == "PASS"
            assert result[0].status_extended == (
                f"User pool client {user_pool_client_name} has token revocation enabled."
            )

            assert result[0].resource_id == user_pool_client_id
            assert result[0].resource_arn == user_pool_client_arn
