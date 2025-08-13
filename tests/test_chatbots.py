def test_chatbots_crud(client):
    # Initially empty
    r = client.get('/api/chatbots')
    assert r.status_code == 200
    assert r.json()['bots'] == []

    # Create
    payload = {
        'name': 'test-bot',
        'llm_provider': 'transformers',
        'model_name': 'gpt2',
        'temperature': 0.7,
        'system_prompt': 'Assistant in Catalan',
        'api_key': '',
        'knowledge_base_ids': []
    }
    r = client.post('/api/chatbots', json=payload)
    assert r.status_code == 200
    bot_id = r.json()['chatbot']['id']

    # List contains the new bot
    r = client.get('/api/chatbots')
    assert any(b['id'] == bot_id for b in r.json()['bots'])

    # Chat (mock path)
    r = client.post('/api/chatbots/chat', json={
        'message': 'Hola',
        'bot_id': bot_id,
        'conversation_history': []
    })
    assert r.status_code == 200
    assert 'reply' in r.json()

    # Delete
    r = client.delete(f'/api/chatbots/{bot_id}')
    assert r.status_code == 200


