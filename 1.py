import requests
id3=965244857
id1=577913397
id2=1029797287
msg='好好好'


requests.post('http://localhost:3000/send_private_msg', json={
    'user_id': 577913397,
    'message': [{
        'type': 'text',
        'data': {
            'text': '好好好'
        }
    }]
})

'''requests.post('http://localhost:3000/send_group_msg', json={
    'group_id': id3,
    'message': [{
        'type': 'text',
        'data': {
            'text': '{}'.format(msg)
        }
    }]
})'''
