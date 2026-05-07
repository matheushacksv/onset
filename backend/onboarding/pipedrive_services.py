import httpx
from decouple import config

BASE_URL = 'https://api.pipedrive.com/api'
HEADERS = {'Content-Type': 'application/json', 'x-api-token': config('PIPEDRIVE_API_KEY')}

# 50ccb59a104c8aaea9e5f26da66996865ca5efea

def list_deals():
    '''List deals able to onboarding'''

    qualificados = []
    cursor = None

    while True:
        params={'pipeline_id': 8, 'status': 'open'}
        if cursor:
            params['cursor'] = cursor
        response = httpx.get(
            url=f'{BASE_URL}/v2/deals',
            headers=HEADERS,
            params=params,
        )
        response.raise_for_status()
        data = response.json()
        
        for deal in data['data']:
            if not deal.get('custom_fields', {}).get('50ccb59a104c8aaea9e5f26da66996865ca5efea'):
                qualificados.append(deal)

        cursor = data.get('additional_data', {}).get('next_cursor')
        if not cursor:
            break
    return qualificados


def update_deal(deal_id: int, fields: dict):
    '''Update a deal in pipedrive'''


    response = httpx.patch(
        url=f'{BASE_URL}/v2/deals/{deal_id}',
        headers=HEADERS,
        json=fields
    )
    response.raise_for_status()
    return response.json()

def create_note(deal_id: int, content: str):
    '''Create a note in pipedrive'''

    response = httpx.post(
        url=f'{BASE_URL}/v1/notes',
        headers=HEADERS,
        json={'content': content, 'deal_id': int(deal_id), 'pinned_to_deal_flag': True}
    )
    response.raise_for_status()
    return response.json()

