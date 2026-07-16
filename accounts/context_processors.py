from django.core.cache import cache

def maintenance_mode_status(request):
    """
    Exposes the maintenance_mode status to all templates.
    """
    return {
        'maintenance_mode': cache.get('admin_maintenance_mode', False)
    }
