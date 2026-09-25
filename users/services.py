def is_manager(user):
    """Проверяет, входит ли пользователь в группу Менеджеров"""
    if user.is_authenticated:
        return user.groups.filter(name="Manager").exists() or user.is_superuser
    return False
