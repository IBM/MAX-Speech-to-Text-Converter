import os
import pytest
import requests

SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:5000')


def test_swagger():

    model_endpoint = SERVER_URL + '/swagger.json'

    r = requests.get(url=model_endpoint)
    assert r.status_code == 200
    assert r.headers['Content-Type'] == 'application/json'

    json = r.json()
    assert 'swagger' in json
    assert json.get('info') and json.get('info').get('title') == 'MAX Speech to Text Converter'
    assert json.get('info') and json.get('info').get('description') == 'Converts spoken words into text form.'


def test_metadata():

    model_endpoint = SERVER_URL + '/model/metadata'

    r = requests.get(url=model_endpoint)
    assert r.status_code == 200

    metadata = r.json()
    assert metadata['id'] == 'max-speech-to-text-converter'
    assert metadata['name'] == 'MAX Speech to Text Converter'
    assert metadata['description'] == 'Converts spoken words into text form.'
    assert metadata['license'] == 'MPL-2.0'


def test_predict():
    model_endpoint = SERVER_URL + '/model/predict'
    file_path = 'assets/2830-3980-0043.wav'

    with open(file_path, 'rb') as file:
        file_form = {'audio': (file_path, file, 'audio/wav')}
        r = requests.post(url=model_endpoint, files=file_form)

    assert r.status_code == 200
    response = r.json()
    assert response['status'] == 'ok'
    assert response['prediction'] == 'experience proves this'


def test_oversampled():
    model_endpoint = SERVER_URL + '/model/predict'
    file_path = 'tests/7s_mono_44k_regan.wav'

    with open(file_path, 'rb') as file:
        file_form = {'audio': (file_path, file, 'audio/wav')}
        r = requests.post(url=model_endpoint, files=file_form)

    assert r.status_code == 200
    response = r.json()
    assert response['status'] == 'ok'
    assert response['prediction'] == 'by god bless you and god bless the united states of america'


def test_undersampled():
    model_endpoint = SERVER_URL + '/model/predict'
    file_path = 'tests/7s_mono_8k_regan.wav'

    with open(file_path, 'rb') as file:
        file_form = {'audio': (file_path, file, 'audio/wav')}
        r = requests.post(url=model_endpoint, files=file_form)

    assert r.status_code == 200
    response = r.json()
    assert response['status'] == 'ok'
    assert 'god bless you and god bless the united states of america' in response['prediction']


def test_bad_extension():
    model_endpoint = SERVER_URL + '/model/predict'
    file_path = 'README.md'

    with open(file_path, 'rb') as file:
        file_form = {'audio': (file_path, file, 'audio/wav')}
        r = requests.post(url=model_endpoint, files=file_form)

    assert r.status_code == 400
    response = r.json()
    assert response['status'] == 'error'


def test_stereo():
    model_endpoint = SERVER_URL + '/model/predict'
    file_path = 'tests/5s_stereo_16k_whitenoise.wav'

    with open(file_path, 'rb') as file:
        file_form = {'audio': (file_path, file, 'audio/wav')}
        r = requests.post(url=model_endpoint, files=file_form)

    assert r.status_code == 400
    response = r.json()
    assert response['status'] == 'error'
    assert response['message'] == 'Only mono audio files are supported.'


def test_too_long():
    model_endpoint = SERVER_URL + '/model/predict'
    file_path = 'tests/15s_mono_16k_whitenoise.wav'

    with open(file_path, 'rb') as file:
        file_form = {'audio': (file_path, file, 'audio/wav')}
        r = requests.post(url=model_endpoint, files=file_form)

    assert r.status_code == 400
    response = r.json()
    assert response['status'] == 'error'
    assert response['message'] == 'This model is designed to work with short (about 5 second) audio files only.'


if __name__ == '__main__':
    pytest.main([__file__])
