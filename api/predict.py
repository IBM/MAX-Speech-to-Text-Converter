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
        except OSError as error:
            abort(400, str(error), status="error")

        # Align the predictions to the required API format
        result['prediction'] = prediction
        result['status'] = 'ok'

        return result
