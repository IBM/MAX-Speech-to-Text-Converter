#
# Copyright 2018-2019 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from flask_restplus import fields, abort
from werkzeug.datastructures import FileStorage
from maxfw.core import MAX_API, PredictAPI
from core.model import ModelWrapper

# Set up parser for input data (http://flask-restplus.readthedocs.io/en/stable/parsing.html)
input_parser = MAX_API.parser()
input_parser.add_argument('audio', type=FileStorage, location='files', required=True,
                          help='A 16 bit, 16 kHz, mono WAV file containing English speech.')

predict_response = MAX_API.model('ModelPredictResponse', {
    'status': fields.String(required=True, description='Response status message'),
    'prediction': fields.String(required=True, description='Predicted text')
})


class ModelPredictAPI(PredictAPI):

    model_wrapper = ModelWrapper()

    @MAX_API.doc('predict')
    @MAX_API.expect(input_parser)
    @MAX_API.marshal_with(predict_response)
    def post(self):
        """Generate audio embedding from input data"""
        result = {'status': 'error'}  # set default status

        args = input_parser.parse_args()
        audio_data = args['audio'].read()

        try:
            prediction = self.model_wrapper.predict(audio_data)

            # Align the predictions to the required API format
            result['prediction'] = prediction
            result['status'] = 'ok'

            return result
        except OSError as error:
            abort(400, str(error), status="error")
