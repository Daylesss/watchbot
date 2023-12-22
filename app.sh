#!/bin/bash
sleep 20

alembic upgrade head

python main.py