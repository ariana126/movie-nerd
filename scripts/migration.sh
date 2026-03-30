#!/usr/bin/env bash

set -e

COMMAND=$1
MESSAGE=$2

case "$COMMAND" in

  create)
    if [ -z "$MESSAGE" ]; then
      echo "Usage: ./migrate.sh create \"message\""
      exit 1
    fi
    alembic revision --autogenerate -m "$MESSAGE"
    ;;

  upgrade-latest)
    alembic upgrade head
    ;;

  rollback-latest)
    alembic downgrade -1
    ;;

  *)
    echo "Available commands:"
    echo "  create \"message\""
    echo "  upgrade-latest"
    echo "  rollback-latest"
    exit 1
    ;;

esac
