## Wefusion

### Hardware requirements
#### Min

- 6 CPU cores
- NVIDIA graphics with 8GB of VRAM
- 16 GB RAM

#### Optimal
- 10 CPU cores
- NVIDIA graphics with 12GB of VRAM
- 16 GB RAM

### Quick start
1. Create your .env file. You can use copy of .env.example
2.
    i. Use `poetry` to install deps `poetry install`.
    ii. Or use `python3 -m venv ./.venv && source ./.venv/bin/activate && pip install -r requirements.txt && pip install -e .`
3. Run `docker compose up -d`
4. Run `POSTGRES_HOST=localhost alembic upgrade head`
5. API docs available on `localhost/api/docs`
