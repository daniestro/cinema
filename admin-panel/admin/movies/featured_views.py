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
DEFAULT_FOCUS = (50, 20)  # x%, y% — used when admin leaves the inputs empty


def _load_featured():
    """Read featured.json. Accepts both legacy `film_ids: [...]` and new `films: [{id, focus?}]`.

    Returns a list of slot dicts: [{'id': str, 'focus_x': int|None, 'focus_y': int|None}].
    """
    if not default_storage.exists(FEATURED_KEY):
        return {'title': '', 'slots': []}

    with default_storage.open(FEATURED_KEY, 'rb') as fp:
        data = json.loads(fp.read().decode('utf-8'))

    if isinstance(data.get('films'), list):
        slots = []
        for item in data['films']:
            if not isinstance(item, dict) or not item.get('id'):
                continue
            focus = item.get('focus') or [None, None]
            x = focus[0] if len(focus) > 0 else None
            y = focus[1] if len(focus) > 1 else None
            slots.append({
                'id': str(item['id']),
                'focus_x': x if isinstance(x, int) else None,
                'focus_y': y if isinstance(y, int) else None,
            })
        return {'title': data.get('title', ''), 'slots': slots}

    legacy_ids = data.get('film_ids') or []
    return {
        'title': data.get('title', ''),
        'slots': [{'id': str(fid), 'focus_x': None, 'focus_y': None} for fid in legacy_ids],
    }


@staff_member_required
def featured_dashboard(request):
    data = _load_featured()
    selected = list(data['slots'])
    # Pad to FEATURED_SLOTS so the template can render exactly that many rows.
    while len(selected) < FEATURED_SLOTS:
        selected.append({'id': '', 'focus_x': None, 'focus_y': None})

    films = [
        {'id': str(film['id']), 'title': film['title']}
        for film in Filmwork.objects.order_by('title').values('id', 'title')
    ]
    slots = [
        {
            'index': i,
            'selected_id': selected[i]['id'],
            'focus_x': '' if selected[i]['focus_x'] is None else selected[i]['focus_x'],
            'focus_y': '' if selected[i]['focus_y'] is None else selected[i]['focus_y'],
        }
        for i in range(FEATURED_SLOTS)
    ]
    public_url = default_storage.url(FEATURED_KEY) if default_storage.exists(FEATURED_KEY) else None

    return render(request, 'admin/featured_dashboard.html', {
        'title': data.get('title', ''),
        'films': films,
        'slots': slots,
        'public_url': public_url,
        'default_focus': DEFAULT_FOCUS,
    })


def _parse_focus_axis(raw):
    """Return an int in [0, 100] or None if empty/invalid."""
    raw = (raw or '').strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        return None
    return value if 0 <= value <= 100 else None


@staff_member_required
@require_POST
def featured_save(request):
    title = (request.POST.get('title') or '').strip()
    submitted = [
        {
            'id': (request.POST.get(f'film_{i}') or '').strip(),
            'focus_x': _parse_focus_axis(request.POST.get(f'focus_x_{i}')),
            'focus_y': _parse_focus_axis(request.POST.get(f'focus_y_{i}')),
        }
        for i in range(FEATURED_SLOTS)
    ]
    films_payload = [s for s in submitted if s['id']]

    if not title:
        messages.error(request, 'Title is required.')
        return redirect(reverse('featured_dashboard'))

    if len(films_payload) != FEATURED_SLOTS:
        messages.error(request, f'Pick exactly {FEATURED_SLOTS} films.')
        return redirect(reverse('featured_dashboard'))

    film_ids = [s['id'] for s in films_payload]
    if len(set(film_ids)) != len(film_ids):
        messages.error(request, 'Films must be distinct.')
        return redirect(reverse('featured_dashboard'))

    existing = set(str(pk) for pk in Filmwork.objects.filter(id__in=film_ids).values_list('id', flat=True))
    missing = [fid for fid in film_ids if fid not in existing]
    if missing:
        messages.error(request, f'Unknown film ids: {", ".join(missing)}')
        return redirect(reverse('featured_dashboard'))

    films_out = []
    for slot in films_payload:
        entry = {'id': slot['id']}
        if slot['focus_x'] is not None and slot['focus_y'] is not None:
            entry['focus'] = [slot['focus_x'], slot['focus_y']]
        films_out.append(entry)

    payload = json.dumps({'title': title, 'films': films_out}, ensure_ascii=False).encode('utf-8')
    # `save` raises on overwrite for some backends; S3Boto3Storage overwrites by default,
    # but delete-first keeps behaviour predictable if the backend is swapped.
    if default_storage.exists(FEATURED_KEY):
        default_storage.delete(FEATURED_KEY)
    default_storage.save(FEATURED_KEY, ContentFile(payload))

    messages.success(request, 'Featured block updated.')
    return redirect(reverse('featured_dashboard'))
