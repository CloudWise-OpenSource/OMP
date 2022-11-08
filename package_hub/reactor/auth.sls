{% if 'act' in data and data['act'] == 'denied' %}
minion_delete:
  wheel.key.delete:
    - args:
      - match: {{ data['id'] }}
{% endif %}
