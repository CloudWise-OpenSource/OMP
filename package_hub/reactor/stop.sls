agent_stop:
  runner.agent_stop.update:
    - agent_id_lst: {{ data['present'] }}
