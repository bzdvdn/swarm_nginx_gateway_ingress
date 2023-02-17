#!/bin/bash
set -e

# check to see if this file is being run or sourced from another script
_is_sourced() {
    # https://unix.stackexchange.com/a/215279
    [ "${#FUNCNAME[@]}" -ge 2 ] \
        && [ "${FUNCNAME[0]}" = '_is_sourced' ] \
        && [ "${FUNCNAME[1]}" = 'source' ]
}

_main() {
  if [ "$1" = 'python main.py' ]; then 
      echo "~~~ start ingress ~~~"
    python main.py &
    echo $! > /ingress/ingress.pid

    exec nginx -g "daemon off;"
  fi
  exec "$@"
}

# If we are sourced from elsewhere, don't perform any further actions
if ! _is_sourced; then
    _main "$@"
fi