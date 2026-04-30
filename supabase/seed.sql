-- Seed data for local development
--
-- Creates a sample pipeline with a completed run so the UI
-- has something to show immediately after `supabase db reset`.
--
-- No auth users yet — user_id is NULL during foundation phase.

-- ── Sample Pipeline: "Customer Feedback Analysis" ───────────────────

insert into pipelines (id, name, definition) values (
  'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
  'Customer Feedback Analysis',
  '{
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Customer Feedback Analysis",
    "nodes": [
      {
        "id": "node_1",
        "type": "datasource",
        "position": { "x": 100, "y": 200 },
        "data": {
          "label": "Feedback API",
          "nodeType": "datasource",
          "config": {
            "sourceType": "rest",
            "url": "https://api.example.com/feedback",
            "method": "GET",
            "headers": {},
            "authType": "bearer"
          }
        }
      },
      {
        "id": "node_2",
        "type": "ai",
        "position": { "x": 400, "y": 200 },
        "data": {
          "label": "Sentiment Analysis",
          "nodeType": "ai",
          "config": {
            "provider": "anthropic",
            "model": "claude-sonnet-4-20250514",
            "prompt": "Analyze the sentiment of each customer feedback entry. Categorize as positive, negative, or neutral. Provide a summary.",
            "temperature": 0.3,
            "maxTokens": 2048
          }
        }
      },
      {
        "id": "node_3",
        "type": "human",
        "position": { "x": 700, "y": 200 },
        "data": {
          "label": "Review Results",
          "nodeType": "human",
          "config": {
            "instructions": "Review the AI analysis before publishing. Flag any misclassified feedback.",
            "requireComment": true
          }
        }
      },
      {
        "id": "node_4",
        "type": "action",
        "position": { "x": 1000, "y": 200 },
        "data": {
          "label": "Export Report",
          "nodeType": "action",
          "config": {
            "actionType": "output",
            "outputFormat": "json"
          }
        }
      }
    ],
    "edges": [
      { "id": "edge_1-2", "source": "node_1", "target": "node_2" },
      { "id": "edge_2-3", "source": "node_2", "target": "node_3" },
      { "id": "edge_3-4", "source": "node_3", "target": "node_4" }
    ],
    "createdAt": "2025-07-20T10:00:00Z",
    "updatedAt": "2025-07-20T10:00:00Z"
  }'::jsonb
);

-- ── Sample Completed Run ────────────────────────────────────────────

insert into pipeline_runs (id, pipeline_id, pipeline_name, status, started_at, completed_at, total_duration_ms, total_cost_usd, pipeline_snapshot) values (
  'r1000000-0000-0000-0000-000000000001',
  'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
  'Customer Feedback Analysis',
  'completed',
  '2025-07-20T10:05:00Z',
  '2025-07-20T10:05:03.450Z',
  3450,
  0.004200,
  '{
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Customer Feedback Analysis",
    "nodes": [
      { "id": "node_1", "type": "datasource", "data": { "label": "Feedback API", "nodeType": "datasource" } },
      { "id": "node_2", "type": "ai", "data": { "label": "Sentiment Analysis", "nodeType": "ai" } },
      { "id": "node_3", "type": "human", "data": { "label": "Review Results", "nodeType": "human" } },
      { "id": "node_4", "type": "action", "data": { "label": "Export Report", "nodeType": "action" } }
    ],
    "edges": [
      { "id": "edge_1-2", "source": "node_1", "target": "node_2" },
      { "id": "edge_2-3", "source": "node_2", "target": "node_3" },
      { "id": "edge_3-4", "source": "node_3", "target": "node_4" }
    ]
  }'::jsonb
);

-- Step results for the completed run
insert into step_results (run_id, node_id, node_type, node_label, status, "order", input_data, output_data, started_at, completed_at, duration_ms) values
(
  'r1000000-0000-0000-0000-000000000001',
  'node_1', 'datasource', 'Feedback API', 'completed', 0,
  null,
  '{"data": [{"id": 1, "text": "Great product!", "rating": 5}, {"id": 2, "text": "Could be better", "rating": 3}, {"id": 3, "text": "Terrible experience", "rating": 1}], "source": "rest", "record_count": 3}'::jsonb,
  '2025-07-20T10:05:00Z', '2025-07-20T10:05:00.120Z', 120
),
(
  'r1000000-0000-0000-0000-000000000001',
  'node_2', 'ai', 'Sentiment Analysis', 'completed', 1,
  '{"data": [{"id": 1, "text": "Great product!", "rating": 5}, {"id": 2, "text": "Could be better", "rating": 3}, {"id": 3, "text": "Terrible experience", "rating": 1}]}'::jsonb,
  '{"analysis": "3 entries analyzed: 1 positive, 1 neutral, 1 negative. Overall sentiment: mixed.", "provider": "anthropic", "model": "claude-sonnet-4-20250514"}'::jsonb,
  '2025-07-20T10:05:00.120Z', '2025-07-20T10:05:03.100Z', 2980
),
(
  'r1000000-0000-0000-0000-000000000001',
  'node_3', 'human', 'Review Results', 'completed', 2,
  '{"analysis": "3 entries analyzed: 1 positive, 1 neutral, 1 negative."}'::jsonb,
  '{"approved": true, "decision": "auto-approved", "comment": "Stub: auto-approved for testing"}'::jsonb,
  '2025-07-20T10:05:03.100Z', '2025-07-20T10:05:03.200Z', 100
),
(
  'r1000000-0000-0000-0000-000000000001',
  'node_4', 'action', 'Export Report', 'completed', 3,
  '{"approved": true, "decision": "auto-approved"}'::jsonb,
  '{"output": {"approved": true}, "format": "json", "action": "output"}'::jsonb,
  '2025-07-20T10:05:03.200Z', '2025-07-20T10:05:03.450Z', 250
);

-- Add token usage to the AI step
update step_results
set input_tokens = 150, output_tokens = 89, total_tokens = 239, cost_usd = 0.004200
where node_id = 'node_2' and run_id = 'r1000000-0000-0000-0000-000000000001';
