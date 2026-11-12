.PHONY: data db load queries reset

data:
	python3 scripts/generate_data.py

db:
	docker compose up -d
	@until docker compose exec -T db pg_isready -U shop -d shop >/dev/null 2>&1; do sleep 1; done

load: db
	docker compose exec -T -w /workspace db psql -U shop -d shop -v ON_ERROR_STOP=1 -f sql/schema.sql
	docker compose exec -T -w /workspace db psql -U shop -d shop -v ON_ERROR_STOP=1 -f sql/load.sql

queries:
	@for f in sql/queries/*.sql; do echo "--- $$f"; docker compose exec -T -w /workspace db psql -U shop -d shop -f "$$f"; done

reset:
	docker compose down -v
