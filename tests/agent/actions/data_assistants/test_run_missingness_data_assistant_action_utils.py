from unittest.mock import MagicMock

import pytest

from great_expectations.agent.actions import (
    CreatedResource,
    RunMissingnessDataAssistantAction,
)
from great_expectations.agent.models import (
    RunMissingnessDataAssistantEvent,
)
from great_expectations.data_context import CloudDataContext
from great_expectations.datasource.fluent import Datasource
from great_expectations.exceptions import StoreBackendError

pytestmark = pytest.mark.unit


@pytest.fixture(scope="function")
def context():
    return MagicMock(autospec=CloudDataContext)


@pytest.fixture
def missingness_event_without_expectation_suite_name():
    return RunMissingnessDataAssistantEvent(
        type="missingness_data_assistant_request.received",
        datasource_name="test-datasource",
        data_asset_name="test-data-asset",
    )


@pytest.fixture
def missingness_event_with_expectation_suite_name():
    return RunMissingnessDataAssistantEvent(
        type="missingness_data_assistant_request.received",
        datasource_name="test-datasource",
        data_asset_name="test-data-asset",
        expectation_suite_name="test-expectation-suite",
    )


def test_run_missingness_data_assistant_action_without_expectation_suite_name(
    context, missingness_event_without_expectation_suite_name
):
    action = RunMissingnessDataAssistantAction(context=context)
    id = "096ce840-7aa8-45d1-9e64-2833948f4ae8"
    context.get_expectation_suite.side_effect = StoreBackendError("test-message")
    context.get_checkpoint.side_effect = StoreBackendError("test-message")
    expectation_suite_id = "084a6e0f-c014-4e40-b6b7-b2f57cb9e176"
    checkpoint_id = "f5d32bbf-1392-4248-bc40-a3966fab2e0e"
    expectation_suite = context.assistants.missingness.run().get_expectation_suite()
    expectation_suite.ge_cloud_id = expectation_suite_id
    checkpoint = context.add_checkpoint.return_value
    checkpoint.ge_cloud_id = checkpoint_id
    datasource = MagicMock(spec=Datasource)
    context.get_datasource.return_value = datasource

    action_result = action.run(
        event=missingness_event_without_expectation_suite_name, id=id
    )

    assert action_result.type == missingness_event_without_expectation_suite_name.type
    assert action_result.id == id
    assert action_result.created_resources == [
        CreatedResource(resource_id=expectation_suite_id, type="ExpectationSuite"),
        CreatedResource(resource_id=checkpoint_id, type="Checkpoint"),
    ]


def test_run_missingness_data_assistant_action_with_expectation_suite_name(
    context, missingness_event_with_expectation_suite_name
):
    action = RunMissingnessDataAssistantAction(context=context)
    id = "096ce840-7aa8-45d1-9e64-2833948f4ae8"
    expectation_suite_id = "084a6e0f-c014-4e40-b6b7-b2f57cb9e176"
    checkpoint_id = "f5d32bbf-1392-4248-bc40-a3966fab2e0e"
    expectation_suite = context.assistants.missingness.run().get_expectation_suite()
    expectation_suite.ge_cloud_id = expectation_suite_id
    checkpoint = context.add_checkpoint.return_value
    checkpoint.ge_cloud_id = checkpoint_id
    datasource = MagicMock(spec=Datasource)
    context.get_datasource.return_value = datasource

    action_result = action.run(
        event=missingness_event_with_expectation_suite_name, id=id
    )

    assert action_result.type == missingness_event_with_expectation_suite_name.type
    assert action_result.id == id
    assert action_result.created_resources == [
        CreatedResource(resource_id=expectation_suite_id, type="ExpectationSuite"),
        CreatedResource(resource_id=checkpoint_id, type="Checkpoint"),
    ]

    # should have created expectation suite with the name provided in the event
    assert context.get_expectation_suite(
        expectation_suite_name=missingness_event_with_expectation_suite_name.expectation_suite_name
    )
