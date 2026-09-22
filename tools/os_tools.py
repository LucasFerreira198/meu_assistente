from core.os_adapter import SystemAdapter

sys_adapter = SystemAdapter()

def open_aplication(app_name: str) -> str:
    return sys_adapter.launch_app(app_name)

def close_aplication(app_name: str) -> str:
    return sys_adapter.close_app(app_name)

def get_active_apps_context() -> str:
    return sys_adapter.get_active_apps_context()

