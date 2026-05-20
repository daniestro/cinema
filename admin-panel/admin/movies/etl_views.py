import json

import requests
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST


ETL_BASE = 'http://etl:8000'
READ_TIMEOUT = 2
RESET_TIMEOUT = 30


def _combine(existing: str | None, new: str) -> str:
    return f'{existing}; {new}' if existing else new


@staff_member_required
def etl_dashboard(request):
    state = None
    health = None
    error = None

    try:
        state = requests.get(f'{ETL_BASE}/state', timeout=READ_TIMEOUT).json()
    except requests.RequestException as exc:
        error = _combine(error, f'/state unreachable: {exc}')

    try:
        response = requests.get(f'{ETL_BASE}/health', timeout=READ_TIMEOUT)
        health = response.json()
        health['status_code'] = response.status_code
    except requests.RequestException as exc:
        error = _combine(error, f'/health unreachable: {exc}')

    state_files_pretty = (
        json.dumps(state.get('state_files', {}), indent=2, ensure_ascii=False)
        if state else None
    )

    return render(request, 'admin/etl_dashboard.html', {
        'state': state,
        'state_files_pretty': state_files_pretty,
        'health': health,
        'error': error,
    })


@staff_member_required
@require_POST
def etl_trigger(request):
    try:
        requests.post(f'{ETL_BASE}/trigger', timeout=READ_TIMEOUT)
        messages.success(request, 'ETL tick triggered')
    except requests.RequestException as exc:
        messages.error(request, f'Failed to trigger ETL: {exc}')
    return redirect(reverse('etl_dashboard'))


@staff_member_required
@require_POST
def etl_reset(request):
    try:
        response = requests.post(f'{ETL_BASE}/reset-index', timeout=RESET_TIMEOUT)
        payload = response.json()
        deleted = ', '.join(payload.get('deleted_indexes') or []) or '—'
        removed = ', '.join(payload.get('removed_state_files') or []) or '—'
        messages.success(
            request,
            f'Indexes reset. Deleted indexes: {deleted}. Removed state files: {removed}.',
        )
    except requests.RequestException as exc:
        messages.error(request, f'Failed to reset indexes: {exc}')
    return redirect(reverse('etl_dashboard'))
