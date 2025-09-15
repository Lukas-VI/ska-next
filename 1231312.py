import requests

'''requests.post('http://localhost:3000/send_private_msg', json={
    'user_id': 577913397,
    'message': [{
        'type': 'text',
        'data': {
            'text': '好好好'
        }
    }]
})'''
requests.post('http://localhost:3000/send_group_msg', json={
    'group_id': 965244857,
    'message':[{'type': 'face', 'data': {'id': '311'}}, {'type': 'face', 'data': {'id': '311'}}, {'type': 'face', 'data': {'id': '311'}}], 'message_format': 'array', 'post_type': 'message'}
)