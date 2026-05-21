import json

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Filmwork


FEATURED_KEY = 'featured.json'
FEATURED_SLOTS = 3


def _load_featured():
    if not default_storage.exists(FEATURED_KEY):
        return {'title': '', 'film_ids': []}
    with default_storage.open(FEATURED_KEY, 'rb') as fp:
        return json.loads(fp.read().decode('utf-8'))


@staff_member_required
def featured_dashboard(request):
    data = _load_featured()
    selected_ids = list(data.get('film_ids') or [])
    # Pad to FEATURED_SLOTS so the template can render exactly that many selects.
    selected_ids += [''] * (FEATURED_SLOTS - len(selected_ids))

    films = [
        {'id': str(film['id']), 'title': film['title']}
        for film in Filmwork.objects.order_by('title').values('id', 'title')
    ]
    slots = [
        {'index': i, 'selected_id': str(selected_ids[i]) if selected_ids[i] else ''}
        for i in range(FEATURED_SLOTS)
    ]
    public_url = default_storage.url(FEATURED_KEY) if default_storage.exists(FEATURED_KEY) else None

    return render(request, 'admin/featured_dashboard.html', {
        'title': data.get('title', ''),
        'films': films,
        'slots': slots,
        'public_url': public_url,
    })


@staff_member_required
@require_POST
def featured_save(request):
    title = (request.POST.get('title') or '').strip()
    raw_ids = [request.POST.get(f'film_{i}', '').strip() for i in range(FEATURED_SLOTS)]
    film_ids = [fid for fid in raw_ids if fid]

    if not title:
        messages.error(request, 'Title is required.')
        return redirect(reverse('featured_dashboard'))

    if len(film_ids) != FEATURED_SLOTS:
        messages.error(request, f'Pick exactly {FEATURED_SLOTS} films.')
        return redirect(reverse('featured_dashboard'))

    if len(set(film_ids)) != len(film_ids):
        messages.error(request, 'Films must be distinct.')
        return redirect(reverse('featured_dashboard'))

    existing = set(str(pk) for pk in Filmwork.objects.filter(id__in=film_ids).values_list('id', flat=True))
    missing = [fid for fid in film_ids if fid not in existing]
    if missing:
        messages.error(request, f'Unknown film ids: {", ".join(missing)}')
        return redirect(reverse('featured_dashboard'))

    payload = json.dumps({'title': title, 'film_ids': film_ids}, ensure_ascii=False).encode('utf-8')
    # `save` raises on overwrite for some backends; S3Boto3Storage overwrites by default,
    # but delete-first keeps behaviour predictable if the backend is swapped.
    if default_storage.exists(FEATURED_KEY):
        default_storage.delete(FEATURED_KEY)
    default_storage.save(FEATURED_KEY, ContentFile(payload))

    messages.success(request, 'Featured block updated.')
    return redirect(reverse('featured_dashboard'))
