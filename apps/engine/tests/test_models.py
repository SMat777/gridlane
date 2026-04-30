"""Tests for SQLAlchemy models — pure unit tests, no DB needed."""

import uuid
from decimal import Decimal

from app.models.run import PipelineRunModel, StepResultModel


class TestPipelineRunModel:
    """Test PipelineRunModel can be instantiated with expected fields."""

    def test_create_run_model(self):
        pipe_id = uuid.uuid4()
        run = PipelineRunModel(
            id=uuid.uuid4(),
            pipeline_id=pipe_id,
            pipeline_name="Test Pipeline",
            status="pending",
            pipeline_snapshot={"nodes": [], "edges": []},
        )

        assert run.pipeline_id == pipe_id
        assert run.pipeline_name == "Test Pipeline"
        assert run.status == "pending"
        assert run.pipeline_snapshot == {"nodes": [], "edges": []}

    def test_run_model_tablename(self):
        assert PipelineRunModel.__tablename__ == "pipeline_runs"


class TestStepResultModel:
    """Test StepResultModel can be instantiated with expected fields."""

    def test_create_step_result(self):
        step = StepResultModel(
            id=uuid.uuid4(),
            run_id=uuid.uuid4(),
            node_id="node_1",
            node_type="datasource",
            node_label="Data Source",
            status="completed",
            order=0,
            input_data={"query": "SELECT 1"},
            output_data={"rows": [{"id": 1}]},
            duration_ms=150,
        )

        assert step.node_id == "node_1"
        assert step.node_type == "datasource"
        assert step.status == "completed"
        assert step.order == 0
        assert step.duration_ms == 150

    def test_step_with_ai_metrics(self):
        step = StepResultModel(
            id=uuid.uuid4(),
            run_id=uuid.uuid4(),
            node_id="node_2",
            node_type="ai",
            node_label="AI Analysis",
            status="completed",
            order=1,
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            cost_usd=Decimal("0.004"),
        )

        assert step.input_tokens == 100
        assert step.output_tokens == 50
        assert step.total_tokens == 150
        assert step.cost_usd == Decimal("0.004")

    def test_step_with_error(self):
        step = StepResultModel(
            id=uuid.uuid4(),
            run_id=uuid.uuid4(),
            node_id="node_3",
            node_type="action",
            node_label="Format Output",
            status="failed",
            order=2,
            error="Connection timeout after 30s",
        )

        assert step.status == "failed"
        assert step.error == "Connection timeout after 30s"

    def test_step_result_tablename(self):
        assert StepResultModel.__tablename__ == "step_results"
