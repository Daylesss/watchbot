#!/bin/bash
sleep 10

alembic upgrade head

python main.py