#!bin/bash
QUERY="DELETE FROM requests_requests  WHERE to_timestamp(time) > NOW() - INTERVAL '30 days';"
PGPASSWORD="$CRON_AGENT_PASSWORD" psql -h dpg-cm13gt8cmk4c73d5es4g-a.ohio-postgres.render.com -U "$CRON_AGENT" -c "$QUERY"
