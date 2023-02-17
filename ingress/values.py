TRUE_VALUES = ('true', 'yes', '1')


DEFAULT_PROXY_SET_HEADER = {
    'Host': '$host',
    'X-Forwarded-For': '$proxy_add_x_forwarded_for',
    'X-Forwarded-Proto': '$scheme',
    'X-Real-IP': '$remote_addr',
}

DEFAULT_PROXY_REQUEST_HEADER = 'on'
DEFAULT_PROXY_REDIRECT = 'off'

DEFAULT_LOG_FORMAT = '$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent" "$http_x_forwarded_for" "$request_id"'
JSON_LOG_FORMAT = '{ \
"@timestamp": "$time_iso8601", \
"@version": "1", \
"system-type": "gateway_ingress", \
"message": "$request [Status: $status]", \
"format": "access", \
"request": { \
  "clientip": "$http_x_forwarded_for", \
  "duration": $request_time, \
  "status": $status, \
  "request": "$request", \
  "path": "$uri", \
  "query": "$query_string", \
  "bytes": $bytes_sent, \
  "method": "$request_method", \
  "host": "$host", \
  "referer": "$http_referer", \
  "user_agent": "$http_user_agent", \
  "request_id": "$request_id", \
  "protocol": "$server_protocol" \
} \
}'

DEFAULT_PROXY_FOR_SERVER = {
    'location': '/',
    'port': '80',
    'custom_location_data': [
        "root   html",
        "index  index.html index.htm",
    ],
}
