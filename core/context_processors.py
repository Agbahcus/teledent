from django.db.models import Count

from consultations.models import Consultation
from dentist.models import DentistProfile


def sidebar_counts(request):
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return {}
    try:
        profile = DentistProfile.objects.get(user=request.user)
    except DentistProfile.DoesNotExist:
        return {}

    rows = Consultation.objects.filter(dentist=profile).values('status').annotate(c=Count('id'))
    counts_map = {r['status']: r['c'] for r in rows}
    return {
        'counts': {
            'NEW': counts_map.get('NEW', 0),
            'IN_REVIEW': counts_map.get('IN_REVIEW', 0),
            'RESPONDED': counts_map.get('RESPONDED', 0),
        },
        'current_profile': profile,
    }
